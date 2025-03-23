# loads configuration files and ensures everything is in place

import tomllib
import os
import sys
import pprint

DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

os.chdir(DIR)

dirs = (
    "src",
    "config",
    # "logs",
    # "logs/services",
    "pipe",
)

files = (
    "paths.toml",
    "src/main.py",
    "src/startup.py",
    "src/log.py",
    "pipe/pipe1",
    "pipe/pipe2",
)


def err(msg):
    print(f"Error: {msg}")
    sys.exit(1)


def check_files():
    success = True

    for i in dirs:
        if not os.path.isdir(i):
            print(f"Directory does not exist: {i}")
            success = False

    for i in files:
        # the reason for not using isfile() is that it does not
        # allow named pipes / FIFOs
        if not os.path.exists(i) and not os.path.isdir(i):
            print(f"File does not exist: {i}")
            success = False

    if not success:
        err("Invalid directory structure.")
        return False
    
    return True


def check_dict(d, **keys):
    # checks dict keys

    missing        = []
    invalid_key    = []
    incorrect_type = []

    for key in keys:
        if key not in d:
            missing.append(key)

        else:
            # check type
            if (type(d[key]) is not keys[key]) if type(keys[key]) is not tuple else \
               (type(d[key]) not in keys[key]):
                incorrect_type.append((key, keys[key]))

    for key in d:
        if key not in keys:
            invalid_key.append(key)

    if not (len(missing)        == 0 and \
            len(invalid_key)    == 0 and \
            len(incorrect_type) == 0):

        err(
            f"Invalid dict!\n"
            f"Missing keys: {missing}\n"
            f"Invalid keys: {invalid_key}\n"
            f"Keys with incorrect types: {incorrect_type}"
        )


def load_config(path, **keys):
    # TODO: handle errors here that check_files will miss
    with open(path) as file:
        d = tomllib.loads(file.read())

    check_dict(d, **keys)

    return d


def load_tasks():
    global tasks

    NoneType = type(None)

    task_args = {
        "desc": (str, ""),
        "nick": ((str, NoneType), None),
        "dir": ((str, NoneType), None),
        "target": ((str, NoneType), None),
        "args": (list, []),
        "logging_enabled": (bool, True),
        "log_dir": ((str, NoneType), "logs"),
        "log_output": (bool, True),
    }

    task_default = {
        k: task_args[k][1] for k in task_args
    }

    task_args = {
        k: task_args[k][0] for k in task_args
    }

    required = ("target",)

    tasks = {}

    default_path = os.path.join(paths["tasks_dir"], "default.toml")
    if os.path.isfile(default_path):
        with open(default_path) as file:
            d = tomllib.loads(file.read())
        task_default = task_default | d
        check_dict(task_default, **task_args)

    for filename in os.listdir(paths["tasks_dir"]):
        filename = os.path.join(paths["tasks_dir"], filename)
        if os.path.isfile(filename):
            if filename == default_path:
                continue

            with open(filename) as file:
                d = tomllib.loads(file.read())

            default = task_default
            if "default" in d:
                default = default | d["default"]
                check_dict(default, **task_args)
                del d["default"]
            
            if "tasks" in d:
                for k, v in d["tasks"].items():
                    v = default | v
                    check_dict(v, **task_args)
                    if k not in tasks:
                        tasks[k] = v
                    else:
                        err(f"Duplicate task: {k}")
                del d["tasks"]
            
            if len(d) != 0:
                err(f"Unrecognized keys: {d.keys()}")

    pprint.pp(tasks)


def init():
    global config
    global paths

    check_files()

    paths = load_config("paths.toml",
        tasks_dir=str,
        config_file=str
    )

    config = load_config(paths["config_file"])

    load_tasks()


config = None
paths = None
tasks = None

init()

