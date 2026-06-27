from enum import StrEnum, auto


class IncidentSeverity(StrEnum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    CRITICAL = auto()
