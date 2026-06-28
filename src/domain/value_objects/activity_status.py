from enum import StrEnum, auto


class ActivityStatus(StrEnum):
    DRAFT = auto()
    ACTIVE = auto()
    UNDER_REVIEW = auto()
    SUSPENDED = auto()
    ARCHIVED = auto()
