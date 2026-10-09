"""The transaction a receipt becomes in the ledger."""

from dataclasses import dataclass
from datetime import date

from src.domain.common.value_object import ValueObject


@dataclass(frozen=True)
class ReceiptPosting(ValueObject):
    """Money booked to one expense account; `name` lists the products it covers."""

    name: str
    expense_account: str
    price: float


@dataclass(frozen=True)
class ReceiptTransaction(ValueObject):
    """A receipt as the ledger books it: expense postings balanced by the source account,
    every posting in the receipt's currency.

    Items sharing an expense account become one posting, so the ledger shows one
    line per account rather than one per product.
    """

    receipt_id: int
    payee: str
    description: str | None
    receipt_date: date
    source_account: str
    total: float
    currency: str
    postings: tuple[ReceiptPosting, ...]

    @classmethod
    def from_items(
        cls,
        *,
        receipt_id: int,
        payee: str,
        description: str | None,
        receipt_date: date,
        source_account: str,
        total: float,
        currency: str,
        items: list[ReceiptPosting],
    ) -> "ReceiptTransaction":
        return cls(
            receipt_id=receipt_id,
            payee=payee,
            description=description,
            receipt_date=receipt_date,
            source_account=source_account,
            total=total,
            currency=currency,
            postings=merge_postings_by_account(items),
        )


def merge_postings_by_account(items: list[ReceiptPosting]) -> tuple[ReceiptPosting, ...]:
    """Combine items with the same expense account, in order of first appearance.

    Names are joined with ", " and prices summed and rounded to the cent, so
    floating-point sums such as 0.1 + 0.2 do not leak into the ledger.
    """
    groups: dict[str, list[ReceiptPosting]] = {}
    for item in items:
        groups.setdefault(item.expense_account, []).append(item)
    return tuple(
        ReceiptPosting(
            name=", ".join(item.name for item in group),
            expense_account=account,
            price=round(sum(item.price for item in group), 2),
        )
        for account, group in groups.items()
    )
