"""
Domain layer exceptions.

These represent business rules being violated or invariants being broken. The
infrastructure layer translates them to HTTP responses (see
`src/infrastructure/common/error_handlers.py`).

Raise a specific subclass from the owning module's `exceptions.py`, such as
`NoteNotFoundError`, never a bare `EntityNotFoundError("Note", id)`.
"""


class DomainError(Exception):
    """Base exception for all domain errors."""

    def __init__(self, message: str, details: dict[str, object] | None = None) -> None:
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def __str__(self) -> str:
        if self.details:
            return f"{self.message} - {self.details}"
        return self.message


class ValidationError(DomainError):
    """Raised when domain validation fails, e.g. an empty title."""

    def __init__(self, message: str, field: str | None = None, value: object = None) -> None:
        details: dict[str, object] = {}
        if field:
            details["field"] = field
        if value is not None:
            details["value"] = value
        super().__init__(message, details)
        self.field = field
        self.value = value


class EntityNotFoundError(DomainError):
    """Base for "entity not found" errors. Subclass it per entity."""

    def __init__(self, entity_type: str, entity_id: object) -> None:
        message = f"{entity_type} with id {entity_id} not found"
        super().__init__(message, {"entity_type": entity_type, "entity_id": entity_id})
        self.entity_type = entity_type
        self.entity_id = entity_id


class BusinessRuleViolationError(DomainError):
    """Raised when a business rule is violated."""

    def __init__(self, rule: str, message: str | None = None) -> None:
        msg = message or f"Business rule violated: {rule}"
        super().__init__(msg, {"rule": rule})
        self.rule = rule


class ConflictError(DomainError):
    """Raised when an operation conflicts with existing state, e.g. a duplicate."""


class ExternalServiceError(DomainError):
    """Raised when a service the app depends on fails or rejects a request.

    The message is shown to the user, so write it for them.
    """


class AuthenticationError(DomainError):
    """Raised when authentication fails."""


class AuthorizationError(DomainError):
    """Raised when the caller lacks permission for an action."""


class InvariantViolationError(BusinessRuleViolationError):
    """Raised when an aggregate invariant is violated."""

    def __init__(self, aggregate: str, invariant: str) -> None:
        message = f"Invariant violation in {aggregate}: {invariant}"
        super().__init__(rule=f"{aggregate}.{invariant}", message=message)
        self.aggregate = aggregate
        self.invariant = invariant
