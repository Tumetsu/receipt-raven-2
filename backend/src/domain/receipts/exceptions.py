"""Receipts domain exceptions."""

from src.domain.common.exceptions import BusinessRuleViolationError, EntityNotFoundError


class ReceiptNotFoundError(EntityNotFoundError):
    """Raised when a receipt cannot be found."""

    def __init__(self, receipt_id: int) -> None:
        super().__init__("Receipt", receipt_id)
        self.receipt_id = receipt_id


class ReceiptAlreadyApprovedError(BusinessRuleViolationError):
    """Raised when an approved receipt would be changed: it is already in the ledger."""

    def __init__(self, receipt_id: int) -> None:
        super().__init__(
            rule="approved_receipt_is_final",
            message="Receipt is already approved and can no longer be changed",
        )
        self.receipt_id = receipt_id


class ReceiptNotApprovableError(BusinessRuleViolationError):
    """Raised when a receipt is not ready to be written to the ledger."""

    def __init__(self, reason: str) -> None:
        super().__init__(rule="approvable_receipt", message=reason)
