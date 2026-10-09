"""Response schemas for the ledger API."""

from typing import Literal

from pydantic import BaseModel

AccountTypeValue = Literal["Assets", "Liabilities", "Equity", "Income", "Expenses"]


class LedgerAccount(BaseModel):
    """An open ledger account."""

    name: str
    type: AccountTypeValue


__all__ = ["AccountTypeValue", "LedgerAccount"]
