"""Port to the bookkeeping ledger."""

from typing import Protocol

from src.domain.ledger.account import AccountType, LedgerAccount
from src.domain.ledger.receipt_transaction import ReceiptTransaction


class LedgerServiceProtocol(Protocol):
    """Read accounts and payees from the ledger and write receipts to it.

    Implementations raise `LedgerUnavailableError` when the ledger cannot be
    reached and `LedgerRejectedTransactionError` when it refuses a receipt.
    """

    async def list_accounts(self, account_type: AccountType | None = None) -> list[LedgerAccount]:
        """Return the open accounts, optionally of one type only."""
        ...

    async def list_payees(self) -> list[str]:
        """Return the payees the ledger's transactions name."""
        ...

    async def submit_receipt(self, transaction: ReceiptTransaction) -> None:
        """Write the receipt's transaction to the ledger."""
        ...
