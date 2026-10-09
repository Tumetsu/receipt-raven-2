"""Use case for deleting receipts."""

from src.application.receipts.protocols.receipt_repository import ReceiptRepositoryProtocol
from src.domain.common.value_objects import ReceiptId
from src.domain.receipts.exceptions import ReceiptNotFoundError


class DeleteReceiptUseCase:
    """Delete a receipt and its items. The ledger is not touched."""

    def __init__(self, receipt_repository: ReceiptRepositoryProtocol) -> None:
        self.receipt_repository = receipt_repository

    async def delete_receipt(self, receipt_id: int) -> None:
        """Delete the receipt.

        Raises:
            ReceiptNotFoundError: If there is no such receipt.
        """
        if not await self.receipt_repository.delete(ReceiptId(receipt_id)):
            raise ReceiptNotFoundError(receipt_id)
