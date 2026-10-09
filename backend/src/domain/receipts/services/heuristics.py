"""Plausibility checks run on what the analysis read from a receipt.

A photographed receipt is almost always from today; a date in another month or
year usually means the analysis misread it.
"""

from datetime import date

from src.domain.receipts.ocr_notes import HeuristicIssue, HeuristicLevel, OcrNotes


def _month_name(value: date) -> str:
    return value.strftime("%B")


def check_suspicious_date(receipt_date: date, today: date) -> HeuristicIssue | None:
    """Flag a receipt date that is not today. Another month or year is severe."""
    if receipt_date.year != today.year:
        relation = "previous" if receipt_date.year < today.year else "future"
        return HeuristicIssue(
            level=HeuristicLevel.SEVERE,
            message=f"Date is in {relation} year ({receipt_date.year})",
        )
    if receipt_date.month != today.month:
        return HeuristicIssue(
            level=HeuristicLevel.SEVERE,
            message=(
                f"Date is from {_month_name(receipt_date)} (current month: {_month_name(today)})"
            ),
        )
    if receipt_date != today:
        return HeuristicIssue(
            level=HeuristicLevel.WARN,
            message=(
                f"Date is {_month_name(receipt_date)} {receipt_date.day} "
                f"(today is {_month_name(today)} {today.day})"
            ),
        )
    return None


def run_heuristics(receipt_date: date, today: date) -> OcrNotes:
    """Run every heuristic on an analysed receipt."""
    return OcrNotes(suspicious_date=check_suspicious_date(receipt_date, today))
