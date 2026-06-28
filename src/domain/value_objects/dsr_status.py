from enum import StrEnum, auto


class DSRStatus(StrEnum):
    OPEN = auto()
    ASSIGNED = auto()
    IN_PROGRESS = auto()
    RESPONDED = auto()
    COMPLETED = auto()
    OVERDUE = auto()
    REJECTED = auto()
