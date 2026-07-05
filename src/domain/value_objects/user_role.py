from enum import StrEnum, auto


class UserRole(StrEnum):
    ADMIN = auto()
    DPO = auto()
    COMPLIANCE = auto()
    LEGAL = auto()
    ANALYST = auto()
    VIEWER = auto()
