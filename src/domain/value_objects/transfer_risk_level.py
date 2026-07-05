from enum import StrEnum, auto


class TransferRiskLevel(StrEnum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    BLOCKED = auto()
