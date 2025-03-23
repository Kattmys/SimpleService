from datetime import datetime
from queue import Queue

general_messages = {
    "Basic":          ["msg"],
    "Starting":       [],
    "Started":        [],
    "InternalError":  ["error"],
}

process_messages = {
    "Output":         ["name", "data"],
    "ProcessBasic":   ["name", "msg"],
    "ProcessStarted": ["name"],
    "ProcessExited":  ["name", "return_code"],
}

messages = general_messages | process_messages

class Names:
    def __init__(self, names):
        self.names = names

    def __getattr__(self, item):
        if item in messages:
            return item
        else:
            raise NameError(f"Not found: {item}")

Msg = Names(messages.keys())
msg_queue = Queue()

def dump(msg_type, kwargs):
    print(msg_type, kwargs)

def log(msg_type, **kwargs):
    if messages[msg_type] != list(kwargs.keys()):
        raise ValueError(
            f"Invalid arguments. Required fields: {', '.join(messages[msg_type])}"
        )
    
    if not msg_type in process_messages:
        dump(msg_type, kwargs)
    else:
        msg_queue.put((msg_type, kwargs))

def flush_messages():
    while not msg_queue.empty():
        dump(*msg_queue.get())

# # Types:

# # Output:

# class Output:
#     def __init__(self, name, data):
#         self.name = name
#         self.data = data

#     def as_str(self):
#         return self.data

# # Message bases:

# class Message:
#     def __init__(self):
#         self.datetime = datetime.now()

#     def date(self):
#         return self.datetime.isoformat(' ', 'minutes')
    
#     def prefix(self):
#         return f"[{self.date()}] "
    
#     def format_message(self):
#         return self.message.replace("\n", "\n" + " " * len(self.prefix()))

#     def as_str(self):
#         return self.prefix() + self.format_message() + "\n"

# class ProcessMessage(Message):
#     def __init__(self, name):
#         super().__init__()
#         self.name = name

#     def prefix(self):
#         return super().prefix() + f"[{self.name}] "

#     def as_str(self, include_name=False):
#         return (self.prefix() if include_name else super().prefix()) + \
#                 self.format_message() + "\n"

# # Global messages:

# class MessageBasic(Message):
#     # Should only be used as a placeholder

#     def __init__(self, message):
#         super().__init__()
#         self.message = message

# class MessageStarted(Message):
#     def __init__(self):
#         super().__init__()
#         self.message = "Started."

# class MessageFinished(Message):
#     def __init__(self):
#         super().__init__()
#         self.message = "Finished."

# class MessageError(MessageBasic):
#     pass

# class MessageFatalError(Message):
#     def __init__(self, error):
#         super().__init__()
#         self.message = f"Internal error!\n{type(error).__name__}: {str(error)}"

# # Process specific messages:

# class MessageProcessStarted(ProcessMessage):
#     def __init__(self, name):
#         super().__init__(name)
#         self.message = "Started."

# class MessageProcessExited(ProcessMessage):
#     def __init__(self, name, return_code):
#         super().__init__(name)
#         self.return_code = return_code
#         self.message = f"Exited. ({self.return_code})"
