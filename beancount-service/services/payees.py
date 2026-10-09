"""
Service for extracting payees from beancount ledger
"""
from typing import List
from beancount.core.data import Transaction
from models import Payee
from repositories import ILedgerRepository
from utils.logging import get_logger

logger = get_logger(__name__)


def get_payees(repository: ILedgerRepository) -> List[Payee]:
    """
    Get all payees (shops, vendors) from the beancount ledger

    Args:
        repository: Ledger repository instance

    Returns:
        List of Payee objects
    """
    entries, errors, options = repository.load_entries()

    # Extract unique payees from transactions
    payees = set()
    for entry in entries:
        if isinstance(entry, Transaction) and entry.payee:
            payees.add(entry.payee)

    return [Payee(name=payee) for payee in sorted(payees)]
