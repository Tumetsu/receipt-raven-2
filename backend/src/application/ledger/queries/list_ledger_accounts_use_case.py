"""Read use case for the ledger's accounts."""

from src.application.ledger.protocols.ledger_service import LedgerServiceProtocol
from src.domain.ledger.account import AccountType, LedgerAccount


class ListLedgerAccountsUseCase:
    """Serve the ledger's open accounts, optionally of the given types only."""

    def __init__(self, ledger_service: LedgerServiceProtocol) -> None:
        self.ledger_service = ledger_service

    async def list_accounts(self, account_types: list[AccountType]) -> list[LedgerAccount]:
        if not account_types:
            return await self.ledger_service.list_accounts()
        accounts: list[LedgerAccount] = []
        for account_type in dict.fromkeys(account_types):
            accounts.extend(await self.ledger_service.list_accounts(account_type))
        return accounts
