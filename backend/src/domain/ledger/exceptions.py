"""Ledger domain exceptions."""

from src.domain.common.exceptions import ExternalServiceError


class LedgerUnavailableError(ExternalServiceError):
    """Raised when the ledger service cannot be reached or fails."""

    def __init__(self, detail: str) -> None:
        super().__init__("The ledger service is not available. Try again later.")
        self.detail = detail


class LedgerRejectedTransactionError(ExternalServiceError):
    """Raised when the ledger refuses a transaction, for example an unknown account."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"The ledger rejected the receipt: {reason}")
        self.reason = reason
