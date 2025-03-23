import os
from sys import argv
from threading import Thread
from subprocess import Popen, PIPE, STDOUT
# from queue import Queue
# from datetime import datetime
from time import sleep

from log import *
from startup import *

try:
    os.chdir(os.path.dirname(os.path.dirname(argv[0])))
except FileNotFoundError:
    pass

READ_LEN   = 4 # amount of bytes read each .read() call
MAX_UNREAD = 4 # consume buffer at this length when no newlines are reached

ENCODING = "utf-8"

names = []
threads = {}
processes = {}

def execute(name, config):
    if name in names:
        log(Msg.Basic, msg=f"Name {name} is taken.")
        return
    else:
        names.append(name)

    p = Popen(
        (config["target"], *config["args"]),
        stdout=PIPE,
        stderr=STDOUT,
        cwd=config["dir"]
    )

    log(Msg.ProcessStarted, name=name)

    def loop():
        buf = ""

        while True:
            b = p.stdout.read(READ_LEN)

            if b:
                buf += b.decode(ENCODING)

                if '\n' in buf:
                    while '\n' in buf:
                        log(Msg.Output, name=name, data=buf[:buf.index('\n')+1])
                        buf = buf[buf.index('\n')+1:]

                elif len(buf) >= MAX_UNREAD and MAX_UNREAD > 0:
                    log(Msg.Output, name=name, data=buf)
                    buf = ""

            else:
                break

        log(Msg.ProcessExited, name=name, return_code=p.wait())

        del processes[name]
        del threads[name]

    t = Thread(target=loop)
    t.start()

    processes[name] = p
    threads[name] = t

def send_to_pipe(msg):
    # opens pipe for writing, sends msg and then closes it,
    # in a separate thread

    def func():
        pipe2 = open("pipe/pipe2", "w")
        pipe2.write(msg)
        pipe2.flush()
        pipe2.close()

    t = Thread(target=func)
    t.start()

log(Msg.Starting)

# execute("a", ("python", "testing/testprocess.py", "hejsan", "10"))
# execute("b", ("python", "testing/testprocess.py", "hejsan", "100"))

init()

for task in tasks:
    execute(task, tasks[task])#, (tasks[task]["target"], *tasks[task]["args"]))

log(Msg.Started)

pipe = os.fdopen(os.open("pipe/pipe1", os.O_RDONLY|os.O_NONBLOCK, 0))

while True:
    s = pipe.readline()
    if s:
        spl = s.split()
        match spl[0]:
            case "kill":
                processes[spl[1]].kill()
                send_to_pipe("Killed!")

            case "status":
                send_to_pipe(f"{processes.keys()}")

    flush_messages()

    # if len(processes) == 0:
    #     break

    sleep(1/15)
