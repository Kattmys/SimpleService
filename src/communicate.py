import os
import sys

def communicate(msg):
    pipe1 = open("pipe1", "w")
    pipe1.write(msg)
    pipe1.flush()

    pipe2 = open("pipe2", "r")
    return pipe2.read()

match sys.argv[1]:
    case "kill":
        print(communicate(f"kill {sys.argv[2]}"))

    case "status":
        print(communicate("status"))

    case _:
        print("Invalid command.")
