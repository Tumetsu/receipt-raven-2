from dependency_injector import containers, providers

from src.application.ledger.queries.list_ledger_accounts_use_case import (
    ListLedgerAccountsUseCase,
)
from src.application.ledger.queries.list_ledger_payees_use_case import ListLedgerPayeesUseCase


class LedgerContainer(containers.DeclarativeContainer):
    """Ledger module use cases."""

    ledger_service = providers.Dependency()

    list_ledger_accounts_use_case = providers.Factory(
        ListLedgerAccountsUseCase, ledger_service=ledger_service
    )
    list_ledger_payees_use_case = providers.Factory(
        ListLedgerPayeesUseCase, ledger_service=ledger_service
    )
