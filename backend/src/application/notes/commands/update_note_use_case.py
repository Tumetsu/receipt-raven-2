"""Use case for updating notes."""

from src.application.notes.protocols.note_repository import NoteRepositoryProtocol
from src.domain.common.value_objects import NoteId
from src.domain.notes.entities.note import Note
from src.domain.notes.exceptions import NoteNotFoundError


class UpdateNoteUseCase:
    """Replace a note's title and body."""

    def __init__(self, note_repository: NoteRepositoryProtocol) -> None:
        self.note_repository = note_repository

    async def update_note(self, note_id: int, title: str, body: str) -> Note:
        """Update the note.

        Raises:
            NoteNotFoundError: If there is no such note.
        """
        note = await self.note_repository.find_by_id(NoteId(note_id))
        if note is None:
            raise NoteNotFoundError(note_id)
        note.update_content(title=title, body=body)
        return await self.note_repository.save(note)
