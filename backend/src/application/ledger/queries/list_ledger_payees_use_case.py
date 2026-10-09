"""Read use case for the payees known to the ledger."""

from src.application.ledger.protocols.ledger_service import LedgerServiceProtocol


class ListLedgerPayeesUseCase:
    """Serve the payee names, sorted, for suggesting a payee."""

    def __init__(self, ledger_service: LedgerServiceProtocol) -> None:
        self.ledger_service = ledger_service

    async def list_payees(self) -> list[str]:
        return sorted(set(await self.ledger_service.list_payees()), key=str.casefold)
