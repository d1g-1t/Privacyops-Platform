"""Domain exceptions — typed errors that map to HTTP codes at the edge."""

from __future__ import annotations


class DomainError(Exception):
    """Base for all domain-level errors."""

    def __init__(self, detail: str, *, code: str = "DOMAIN_ERROR") -> None:
        self.detail = detail
        self.code = code
        super().__init__(detail)


class EntityNotFoundError(DomainError):
    def __init__(self, entity: str, identifier: str) -> None:
        super().__init__(
            f"{entity} with id={identifier} not found",
            code="NOT_FOUND",
        )


class DuplicateEntityError(DomainError):
    def __init__(self, entity: str, key: str) -> None:
        super().__init__(
            f"{entity} already exists: {key}",
            code="DUPLICATE",
        )


class InvalidStateTransitionError(DomainError):
    def __init__(self, entity: str, current: str, target: str) -> None:
        super().__init__(
            f"Cannot transition {entity} from {current} to {target}",
            code="INVALID_TRANSITION",
        )


class AuthenticationError(DomainError):
    def __init__(self, detail: str = "Invalid credentials") -> None:
        super().__init__(detail, code="AUTH_ERROR")


class AuthorizationError(DomainError):
    def __init__(self, detail: str = "Insufficient permissions") -> None:
        super().__init__(detail, code="FORBIDDEN")


class ComplianceViolationError(DomainError):
    """Raised when a business rule prevents an action for compliance reasons."""

    def __init__(self, detail: str) -> None:
        super().__init__(detail, code="COMPLIANCE_VIOLATION")
