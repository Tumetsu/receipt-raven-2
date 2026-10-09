"""
Service for extracting account information from beancount ledger
"""
from typing import List, Optional
from beancount.core import getters
from models import Account, AccountType
from repositories import ILedgerRepository
from utils.logging import get_logger

logger = get_logger(__name__)


def get_account_type(account_name: str) -> AccountType:
    """
    Determine account type from account name
    Beancount accounts follow the pattern: Type:Subaccount:...
    """
    if account_name.startswith("Assets:"):
        return AccountType.ASSETS
    elif account_name.startswith("Liabilities:"):
        return AccountType.LIABILITIES
    elif account_name.startswith("Equity:"):
        return AccountType.EQUITY
    elif account_name.startswith("Income:"):
        return AccountType.INCOME
    elif account_name.startswith("Expenses:"):
        return AccountType.EXPENSES
    else:
        # Default to expenses if unknown
        return AccountType.EXPENSES


def get_display_name(account_name: str) -> str:
    """
    Generate a human-readable display name from account name
    Example: Expenses:Food:Groceries -> Groceries
    """
    parts = account_name.split(":")
    return parts[-1] if len(parts) > 1 else account_name


def get_accounts(
    repository: ILedgerRepository, account_type_filter: Optional[str] = None
) -> List[Account]:
    """
    Get all accounts from the beancount ledger

    Args:
        repository: Ledger repository instance
        account_type_filter: Optional filter by account type (e.g., "Expenses")

    Returns:
        List of Account objects
    """
    entries, errors, options = repository.load_entries()

    # Errors are already logged in the repository

    # Get all account names from the ledger
    all_accounts = getters.get_accounts(entries)

    accounts = []
    for account_name in sorted(all_accounts):
        account_type = get_account_type(account_name)

        # Apply filter if provided
        if account_type_filter and account_type.value != account_type_filter:
            continue

        accounts.append(
            Account(
                name=account_name,
                type=account_type,
                display_name=get_display_name(account_name),
            )
        )

    return accounts
