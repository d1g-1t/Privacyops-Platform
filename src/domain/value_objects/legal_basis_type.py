from enum import StrEnum, auto


class LegalBasisType(StrEnum):
    CONSENT = auto()
    CONTRACT = auto()
    LEGAL_OBLIGATION = auto()
    VITAL_INTEREST = auto()
    PUBLIC_INTEREST = auto()
    LEGITIMATE_INTEREST = auto()
    STATUTORY = auto()
