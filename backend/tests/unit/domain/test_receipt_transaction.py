"""Unit tests for merging receipt items into one posting per expense account."""

from src.domain.ledger.receipt_transaction import ReceiptPosting, merge_postings_by_account


def test_merges_by_account_in_order_of_first_appearance_and_rounds_to_cents() -> None:
    merged = merge_postings_by_account(
        [
            ReceiptPosting("Kahvi", "Expenses:Groceries", 0.1),
            ReceiptPosting("Kynä", "Expenses:Office", 1.99),
            ReceiptPosting("Maito", "Expenses:Groceries", 0.2),
        ]
    )

    assert merged == (
        ReceiptPosting("Kahvi, Maito", "Expenses:Groceries", 0.3),
        ReceiptPosting("Kynä", "Expenses:Office", 1.99),
    )
