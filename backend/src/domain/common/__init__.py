"""
Domain common module: the building blocks every domain module shares.

- ValueObject: immutable objects defined by their attributes
- Entity / EntityId: objects with identity and lifecycle
- AggregateRoot: consistency boundaries
- Domain exceptions
"""

from .aggregate_root import AggregateRoot
from .entity import Entity, EntityId
from .exceptions import (
    BusinessRuleViolationError,
    ConflictError,
    DomainError,
    EntityNotFoundError,
    InvariantViolationError,
    ValidationError,
)
from .value_object import ValueObject

__all__ = [
    "AggregateRoot",
    "BusinessRuleViolationError",
    "ConflictError",
    "DomainError",
    "Entity",
    "EntityId",
    "EntityNotFoundError",
    "InvariantViolationError",
    "ValidationError",
    "ValueObject",
]
