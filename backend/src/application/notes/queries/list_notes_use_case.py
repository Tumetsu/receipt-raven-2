"""Read use case for the note list."""

from src.application.notes.queries.note_list import NoteListItemView, NoteListQueryProtocol


class ListNotesUseCase:
    """Serve the note list from its query port."""

    def __init__(self, note_list_query: NoteListQueryProtocol) -> None:
        self.note_list_query = note_list_query

    async def list_notes(self, search: str | None = None) -> tuple[NoteListItemView, ...]:
        cleaned = search.strip() if search else None
        return await self.note_list_query.list_notes(cleaned or None)
