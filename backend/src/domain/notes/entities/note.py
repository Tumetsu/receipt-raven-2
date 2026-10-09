"""Note aggregate: the example domain module this template ships with.

Replace it with your own domain. It exists to show every layer working end to
end; see `docs/agents/domain-modules.md` for how to add a module of your own.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime

from src.domain.common.aggregate_root import AggregateRoot
from src.domain.common.exceptions import ValidationError
from src.domain.common.value_objects import NoteId

MAX_TITLE_LENGTH = 200


@dataclass
class Note(AggregateRoot[NoteId]):
    """
    A short titled note.

    Business rules:
    - The title is trimmed, cannot be empty and is at most 200 characters
    - The body may be empty
    """

    id: NoteId
    title: str
    body: str = ""
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        self.title = self._valid_title(self.title)

    def update_content(self, title: str, body: str) -> None:
        """Replace the title and body."""
        self.title = self._valid_title(title)
        self.body = body

    @staticmethod
    def _valid_title(title: str) -> str:
        stripped = title.strip()
        if not stripped:
            raise ValidationError("Note title cannot be empty", field="title")
        if len(stripped) > MAX_TITLE_LENGTH:
            raise ValidationError(
                f"Note title cannot exceed {MAX_TITLE_LENGTH} characters", field="title"
            )
        return stripped

    @classmethod
    def create(cls, title: str, body: str = "") -> Note:
        """Create a new note. Its id stays 0 until the repository stores it."""
        return cls(id=NoteId.generate(), title=title, body=body)

    @classmethod
    def create_with_id(
        cls,
        id: NoteId,
        title: str,
        body: str,
        created_at: datetime,
        updated_at: datetime,
    ) -> Note:
        """Reconstitute a note from persistence."""
        return cls(id=id, title=title, body=body, created_at=created_at, updated_at=updated_at)
