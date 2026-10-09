"""Use case for deleting notes."""

from src.application.notes.protocols.note_repository import NoteRepositoryProtocol
from src.domain.common.value_objects import NoteId
from src.domain.notes.exceptions import NoteNotFoundError


class DeleteNoteUseCase:
    """Delete a note."""

    def __init__(self, note_repository: NoteRepositoryProtocol) -> None:
        self.note_repository = note_repository

    async def delete_note(self, note_id: int) -> None:
        """Delete the note.

        Raises:
            NoteNotFoundError: If there is no such note.
        """
        if not await self.note_repository.delete(NoteId(note_id)):
            raise NoteNotFoundError(note_id)
