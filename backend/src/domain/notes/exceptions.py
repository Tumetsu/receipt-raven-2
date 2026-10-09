"""Notes domain exceptions."""

from src.domain.common.exceptions import EntityNotFoundError


class NoteNotFoundError(EntityNotFoundError):
    """Raised when a note cannot be found."""

    def __init__(self, note_id: int) -> None:
        super().__init__("Note", note_id)
        self.note_id = note_id
