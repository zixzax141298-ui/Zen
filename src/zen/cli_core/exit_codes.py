from enum import IntEnum


class ExitCode(IntEnum):
    OK = 0
    SOURCE_ERROR = 1
    IO_ERROR = 1
    USAGE_ERROR = 2
    TIMEOUT = 124
    INTERRUPTED = 130
