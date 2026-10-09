"""Query adapter for the note list.

Selects only the columns the view needs and maps rows straight to view DTOs:
no aggregate is loaded, because nothing here is going to be changed.
"""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.notes.queries.note_list import NoteListItemView
from src.infrastructure.notes.orm.note_model import NoteModel

PREVIEW_LENGTH = 140


class NoteListQuery:
    """Serves the note list read model."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_notes(self, search: str | None) -> tuple[NoteListItemView, ...]:
        stmt = select(
            NoteModel.id,
            NoteModel.title,
            func.substr(NoteModel.body, 1, PREVIEW_LENGTH),
            NoteModel.updated_at,
        ).order_by(NoteModel.updated_at.desc(), NoteModel.id.desc())
        if search:
            stmt = stmt.where(NoteModel.title.icontains(search, autoescape=True))

        result = await self.db.execute(stmt)
        return tuple(
            NoteListItemView(id=id, title=title, body_preview=preview, updated_at=updated_at)
            for id, title, preview, updated_at in result
        )
