import sys
import runpy
import time

from task import *
from log import *

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
for task in tasks:
    task.start()
logger.log(Msg.Started)

while True:
    logger.dump_queue()
    time.sleep(0.2)

    # break if nothing is running
    any_alive = False
    for task in Task.tasks.values():
        if task.alive:
            any_alive = True
    if not any_alive:
        break

logger.dump_queue()
logger.log(Msg.Finished)
