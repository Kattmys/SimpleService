from queue import Queue
from datetime import datetime
import os

from variables import *

main_messages = {
    "Basic":            "{msg}",
    "Debug":            "{RED}DEBUG:{RESET} {msg}",
    "Starting":         "{GREEN}Starting...{RESET}",
    "Started":          "{GREEN}Started!{RESET}",
    "Finished":         "{GREEN}Finished.{RESET}",
    "TaskInvalidArgs":  "{RED}Invalid arguments for '{name}':{RESET} {msg}",
    "SIGINT":           "{RED}SIGINT received!{RESET}",
    "InternalError":    "{RED}Error!{RESET} {error}"
}

task_messages = {
    "Output":         "{output}",
    "ProcessBasic":   "{msg}",
    "ProcessStarted": "{GREEN}Started!{RESET}",
    "ProcessExited":  "{RED}Exited with return code {return_code}.{RESET}"
}

messages = main_messages | task_messages

class MsgClass:
    def __getattr__(self, item):
        if item in messages:
            return item
        else:
            raise NameError(f"Not found: {item}")

Msg = MsgClass()

get_date = lambda: datetime.now().isoformat(" ", "minutes")

def format_message(msg_type, task, kwargs, task_file=False):
    msg = "{BLUE}[{}]{RESET} ".format(get_date(), **COLORS)

    if task is not None and not task_file:
        msg += "{YELLOW}[{}]{RESET} ".format(task.display, **COLORS)

    msg += messages[msg_type].format(**kwargs, **COLORS)
    msg += "\n"

    return msg

class Logger:
    def __init__(self,
            main_log_file="logs/log",
            tasks_dir="logs/tasks",
        ):

        self.file = main_log_file
        self.tasks_dir = tasks_dir

        # queue for messages from tasks (separate threads)
        #   before they are dumped using dump_queue() by the main thread
        self.msg_queue = Queue()

        # buffer for text to be written to main log
        self.buffer = ""

    def flush(self):
        with open(self.file, "a") as file:
            file.write(self.buffer)

        self.buffer = ""

    def dump(self, msg_type, task, kwargs):
        if msg_type != Msg.Output:
            main_out = format_message(msg_type, task, kwargs)

            if task is not None:
                self.buffer += main_out

                task_out = format_message(msg_type, task, kwargs, task_file=True)
                with open(os.path.join(self.tasks_dir, task.name), "a") as file:
                    file.write(task_out)

            else:
                with open(self.file, "a") as file:
                    file.write(main_out)

        else:
            with open(os.path.join(self.tasks_dir, task.name), "a") as file:
                file.write(kwargs["output"])

    def log(self, msg_type, task=None, **kwargs):
        # # check if kwargs are valid
        # if messages[msg_type] != kwargs.keys():
        #     raise ValueError(
        #         f"Invalid arguments. Required fields: " + ", ".join(messages[msg_type])
        #     )
        
        if task is None:
            # dump the message directly
            self.dump(msg_type, task, kwargs)

        else:
            # as the message comes from a task (a thread),
            # it is not safe to dump directly.
            # instead, add it to the queue.
            self.msg_queue.put((msg_type, task, kwargs))

    def dump_queue(self):
        # dump queued messages

        while not self.msg_queue.empty():
            self.dump(*self.msg_queue.get())

        self.flush()
