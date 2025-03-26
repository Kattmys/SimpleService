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

    num_args = {
        "kill":  1,
        "list":  0,
        "names": 0,
        "send":  2,
        "ask":   2,
    }

    if cmd in num_args:
        m = check_args(num_args[cmd])
        if m is not None:
            return m
    else:
        return "Unknown command."

    match cmd:
        case "kill":
            t = Task.get(args[0])
            if t:
                t.process.kill()
                return "Killed!"
            else:
                return f"Task {args[0]} not found."

        case "list":
            return Task.list()
        
        case "names":
            return Task.names()

        case "send":
            t = Task.get(args[0])
            if t:
                if t.send(args[1] + "\n"):
                    return "Sent!"
                else:
                    return "Not sent."
            else:
                return f"Task {args[0]} not found."

path = sys.argv[1] if len(sys.argv) > 1 else "user/config.py"

logger = Logger()
Task.default_log = logger

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

if "log_file" in g:
    logger.main_log_file = g["log_file"]
if "tasks_dir" in g:
    logger.tasks_dir = g["tasks_dir"]

logger.log(Msg.Starting)

receive_pipe = os.fdopen(os.open("pipes/send", os.O_RDONLY|os.O_NONBLOCK, 0))

for task in tasks:
    task.start()
logger.log(Msg.Started)

try:
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

except KeyboardInterrupt:
    logger.log(Msg.SIGINT)
    print()

finally:
    while True in [task.alive for task in Task.tasks.values()]:
        pass

    logger.dump_queue()
    logger.log(Msg.Finished)
