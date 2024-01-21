from enum import Enum


# Platform codes
class PlatformCode(Enum):
    WINDOWS = "win32"
    LINUX = "linux"
    MAC = "darwin"
    UNKNOWN = "unknown"


# Operation codes
class OpCode(Enum):
    ADD = "+"
    SUB = "-"
    MULT = "*"
    DIV = "/"
