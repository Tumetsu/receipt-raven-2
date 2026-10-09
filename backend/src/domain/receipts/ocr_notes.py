"""Notes the automatic analysis leaves on a receipt for the user to review."""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

from src.domain.common.value_object import ValueObject


class HeuristicLevel(StrEnum):
    """How strongly a heuristic doubts a value the analysis read."""

    WARN = "WARN"
    SEVERE = "SEVERE"
    ERROR = "ERROR"


@dataclass(frozen=True)
class HeuristicIssue(ValueObject):
    """One doubt about an analysed value, with a message for the user."""

    level: HeuristicLevel
    message: str


@dataclass(frozen=True)
class OcrNotes(ValueObject):
    """Every issue the heuristics found. A field is None when its check passed."""

    suspicious_date: HeuristicIssue | None = None

    @property
    def is_empty(self) -> bool:
        return self.suspicious_date is None
