"""Unit tests for the Note aggregate's invariants.

Pure domain logic with real branching earns a unit test; everything that goes
through an endpoint is covered by the API tests instead.
"""

import pytest

from src.domain.common.exceptions import ValidationError
from src.domain.notes.entities.note import MAX_TITLE_LENGTH, Note


@pytest.mark.parametrize(
    ("title", "expected"),
    [("  padded  ", "padded"), ("x" * MAX_TITLE_LENGTH, "x" * MAX_TITLE_LENGTH)],
)
def test_title_is_trimmed_and_accepted_up_to_limit(title: str, expected: str) -> None:
    assert Note.create(title=title).title == expected


@pytest.mark.parametrize("title", ["", "   ", "x" * (MAX_TITLE_LENGTH + 1)])
def test_invalid_title_is_rejected(title: str) -> None:
    with pytest.raises(ValidationError):
        Note.create(title=title)


def test_update_validates_the_new_title_and_keeps_the_old_one_on_failure() -> None:
    note = Note.create(title="Original", body="body")

    with pytest.raises(ValidationError):
        note.update_content(title=" ", body="changed")

    assert (note.title, note.body) == ("Original", "body")
