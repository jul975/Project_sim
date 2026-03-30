from enum import Enum, auto

class ExecutionMode(Enum):
    EXPERIMENT = auto()
    VALIDATION = auto()
    VERIFICATION = auto()
    EXPLORATION = auto()
    DIAGNOSTIC = auto()