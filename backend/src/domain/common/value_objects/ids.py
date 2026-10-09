"""Strongly-typed entity identifiers."""

from dataclasses import dataclass

from ..entity import EntityId


@dataclass(frozen=True)
class NoteId(EntityId):
    """Strongly-typed note identifier."""

    value: int
