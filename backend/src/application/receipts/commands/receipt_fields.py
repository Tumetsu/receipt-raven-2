"""The editable fields of a receipt, as the create and approve commands take them."""

from dataclasses import dataclass
from datetime import date

from src.domain.receipts.entities.receipt import ReceiptLine


@dataclass(frozen=True)
class ReceiptFields:
    """Header fields and line items the user entered."""

    payee: str
    receipt_date: date
    total_sum: float
    lines: list[ReceiptLine]
    description: str | None = None
    source_account: str | None = None
    currency: str = "EUR"
