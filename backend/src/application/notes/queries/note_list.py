"""Read model for the note list.

These are view DTOs, not domain entities: they exist to be rendered and must
never be fed back into a command (the `queries-are-dead-ends` import contract
enforces that). See `docs/adr/0001-read-models-and-query-services.md`.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol


@dataclass(frozen=True)
class NoteListItemView:
    """One row of the note list: the body is cut to a preview."""

    id: int
    title: str
    body_preview: str
    updated_at: datetime


class NoteListQueryProtocol(Protocol):
    """Port for reading the note list."""

    async def list_notes(self, search: str | None) -> tuple[NoteListItemView, ...]:
        """Return notes, most recently updated first, optionally filtered by title."""
        ...
