"""Ledger accounts."""

from dataclasses import dataclass
from enum import StrEnum

from src.domain.common.value_object import ValueObject


class AccountType(StrEnum):
    """The top-level account categories of a double-entry ledger."""

    ASSETS = "Assets"
    LIABILITIES = "Liabilities"
    EQUITY = "Equity"
    INCOME = "Income"
    EXPENSES = "Expenses"


@dataclass(frozen=True)
class LedgerAccount(ValueObject):
    """An open account, such as `Expenses:Food:Groceries`."""

    name: str
    type: AccountType
