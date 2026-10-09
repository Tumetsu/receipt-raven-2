"""Read use case for a single note.

A read too small to deserve its own port: it delegates to the repository and
returns the domain entity (the ADR's "halfway option").
"""

from src.application.notes.protocols.note_repository import NoteRepositoryProtocol
from src.domain.common.value_objects import NoteId
from src.domain.notes.entities.note import Note
from src.domain.notes.exceptions import NoteNotFoundError


class GetNoteUseCase:
    """Serve one note."""

    def __init__(self, note_repository: NoteRepositoryProtocol) -> None:
        self.note_repository = note_repository

    async def get_note(self, note_id: int) -> Note:
        """Return the note.

        Raises:
            NoteNotFoundError: If there is no such note.
        """
        note = await self.note_repository.find_by_id(NoteId(note_id))
        if note is None:
            raise NoteNotFoundError(note_id)
        return note
