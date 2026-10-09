"""Use case for creating notes."""

import structlog

from src.application.notes.protocols.note_repository import NoteRepositoryProtocol
from src.domain.notes.entities.note import Note

logger = structlog.get_logger(__name__)


class CreateNoteUseCase:
    """Create a note."""

    def __init__(self, note_repository: NoteRepositoryProtocol) -> None:
        self.note_repository = note_repository

    async def create_note(self, title: str, body: str) -> Note:
        note = await self.note_repository.save(Note.create(title=title, body=body))
        logger.info("note_created", note_id=note.id.value)
        return note
