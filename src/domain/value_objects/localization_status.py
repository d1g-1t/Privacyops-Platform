from enum import StrEnum, auto


class LocalizationStatus(StrEnum):
    UNKNOWN = auto()
    COMPLIANT = auto()
    NON_COMPLIANT = auto()
    UNDER_REVIEW = auto()
    EXCEPTION_GRANTED = auto()
