"""Port for storing Note aggregates."""

from typing import Protocol

from src.domain.common.value_objects import NoteId
from src.domain.notes.entities.note import Note


class NoteRepositoryProtocol(Protocol):
    """Load and store Note aggregates."""

    async def find_by_id(self, note_id: NoteId, /) -> Note | None:
        """Return the note, or ``None`` when there is no such note."""
        ...

    async def save(self, note: Note, /) -> Note:
        """Insert a new note (id 0) or update an existing one."""
        ...

    async def delete(self, note_id: NoteId, /) -> bool:
        """Delete a note. Returns False if there was no such note."""
        ...
