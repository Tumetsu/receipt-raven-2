"""Repository for Note aggregates."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.notes.entities.note import Note
from src.infrastructure.common.repositories import BaseRepository
from src.infrastructure.notes.mappers.note_mapper import NoteMapper
from src.infrastructure.notes.orm.note_model import NoteModel


class NoteRepository(BaseRepository[Note, NoteModel]):
    """Stores notes. ``find_by_id``, ``save`` and ``delete`` come from the base class."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, NoteModel, NoteMapper())
