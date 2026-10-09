"""Unit tests for the suspicious-date heuristic: one case per branch."""

from datetime import date

import pytest

from src.domain.receipts.ocr_notes import HeuristicIssue, HeuristicLevel
from src.domain.receipts.services.heuristics import check_suspicious_date

TODAY = date(2026, 10, 9)


@pytest.mark.parametrize(
    ("receipt_date", "expected"),
    [
        (TODAY, None),
        (
            date(2026, 10, 5),
            HeuristicIssue(HeuristicLevel.WARN, "Date is October 5 (today is October 9)"),
        ),
        (
            date(2026, 9, 30),
            HeuristicIssue(
                HeuristicLevel.SEVERE, "Date is from September (current month: October)"
            ),
        ),
        (
            date(2025, 10, 9),
            HeuristicIssue(HeuristicLevel.SEVERE, "Date is in previous year (2025)"),
        ),
        (date(2027, 1, 1), HeuristicIssue(HeuristicLevel.SEVERE, "Date is in future year (2027)")),
    ],
)
def test_flags_dates_other_than_today(receipt_date: date, expected: HeuristicIssue | None) -> None:
    assert check_suspicious_date(receipt_date, TODAY) == expected
