import subprocess
import threading

from log import Msg

class Task:
    tasks = {}

    # every used name, including finished tasks and aliases
    taken_names = set()

    default_log = None

    def __init__(
                self,
                name,
                args,
                log=None,
                aliases=[],
                display=None,
                shell=False,
                cwd=None,
                read_len=4,
                max_unread=32,
                encoding="utf-8"
            ):

        if not shell and type(args) is str:
            raise ValueError("Argument 'args' should be an array when shell = False.")
        elif shell and type(args) is not str:
            raise ValueError("Argument 'args' should be a string when shell = True.")

        self.args = args
        self.shell = shell
        self.cwd = cwd
        self.name = name
        self.aliases = aliases
        self.read_len = read_len
        self.max_unread = max_unread
        self.encoding = encoding
        self.log_ = log if log is not None else __class__.default_log
        self.display = display if display is not None else self.name

        self.process = None
        self.thread  = None

        __class__.taken_names.add(self.name)
        for alias in self.aliases:
            __class__.taken_names.add(alias)
        __class__.tasks[self.name] = self

    # @classmethod
    # def from_config(cls, config):
    #     return cls(
    #         config["name"],
    #         config["cmd"],
    #         aliases=config["aliases"],
    #         shell=config["shell"]
    #     )

    @property
    def alive(self):
        return self.process.returncode is None or self.thread.is_alive()

    def log(self, msg_type, **kwargs):
        self.log_.log(msg_type, task=self, **kwargs)

    def log_output(self, output):
        self.log(Msg.Output, output=output)

    def start(self):
        self.process = subprocess.Popen(
            self.args,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            shell=self.shell,
            cwd=self.cwd
        )

        self.log(Msg.ProcessStarted)

        def loop():
            buf = ""

            while True:
                b = self.process.stdout.read(self.read_len)

                if b:
                    buf += b.decode(self.encoding)

                    if '\n' in buf:
                        while '\n' in buf:
                            self.log_output(buf[:buf.index('\n')+1])
                            buf = buf[buf.index('\n')+1:]

                    elif self.max_unread is not None and self.max_unread > 0 and len(buf) >= self.max_unread:
                        self.log_output(buf)
                        buf = ""

                else:
                    break

            # out = self.process.stdout.read()
            # if out:
            #     self.log_output(out.decode(self.encoding))

            self.log(Msg.ProcessExited, return_code=self.process.wait())

        self.thread = threading.Thread(target=loop)
        self.thread.start()
