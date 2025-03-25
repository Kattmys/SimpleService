import os
import sys
import time
import runpy
import threading

from task import *
from log import *

def send_to_pipe(msg):
    # opens pipe for writing, sends msg and then closes it,
    # in a separate thread

    def func():
        with open("pipes/receive", "w") as send_pipe:
            send_pipe.write(msg)
            send_pipe.flush()

    t = threading.Thread(target=func)
    t.start()

def process_command(cmd):
    spl = cmd.split()
    cmd = spl[0]
    args = spl[1:]

    def check_args(*lengths):
        # checks number of arguments
        if len(args) not in lengths:
            return "Invalid number of arguments: expected " + ", ".join([str(i) for i in lengths])

    match cmd:
        case "kill":
            m = check_args(1)
            if m is not None: return m

            Task.tasks[args[0]].process.kill()
            return "Killed!"

        case "list":
            m = check_args(0)
            if m is not None: return m
            # return "\n".join([str(i) for i in Task.tasks.keys()])
            return Task.list()
        
        case _:
            return "Unknown command."

logger = Logger()
Task.default_log = logger

path = sys.argv[1] if len(sys.argv) > 1 else "user/config.py"

g = runpy.run_path(
    path,
    init_globals={
        "Task": Task
    }
)

if "tasks" in g:
    tasks = g["tasks"]
else:
    print(f"Variable 'tasks' not found in {path}.")
    sys.exit(1)

logger.log(Msg.Starting)

receive_pipe = os.fdopen(os.open("pipes/send", os.O_RDONLY|os.O_NONBLOCK, 0))

for task in tasks:
    task.start()
logger.log(Msg.Started)

while True:
    cmd = receive_pipe.readline()
    if cmd:
        send_to_pipe(process_command(cmd) + "\n")

    logger.dump_queue()

    # break if nothing is running
    # any_alive = False
    # for task in Task.tasks.values():
    #     if task.alive:
    #         any_alive = True
    # if not any_alive:
    #     break

    time.sleep(0.2)

logger.dump_queue()
logger.log(Msg.Finished)
