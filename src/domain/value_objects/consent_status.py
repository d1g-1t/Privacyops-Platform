from enum import StrEnum, auto


class ConsentStatus(StrEnum):
    COLLECTED = auto()
    ACTIVE = auto()
    WITHDRAWN = auto()
    EXPIRED = auto()
    REVOKED = auto()
