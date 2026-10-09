"""Read use case for a single receipt with its items.

A read too small to deserve its own port: it delegates to the repository and
returns the domain entity (the ADR's "halfway option").
"""

from src.application.receipts.protocols.receipt_repository import ReceiptRepositoryProtocol
from src.domain.common.value_objects import ReceiptId
from src.domain.receipts.entities.receipt import Receipt
from src.domain.receipts.exceptions import ReceiptNotFoundError


class GetReceiptUseCase:
    """Serve one receipt."""

    def __init__(self, receipt_repository: ReceiptRepositoryProtocol) -> None:
        self.receipt_repository = receipt_repository

    async def get_receipt(self, receipt_id: int) -> Receipt:
        """Return the receipt.

        Raises:
            ReceiptNotFoundError: If there is no such receipt.
        """
        receipt = await self.receipt_repository.find_by_id(ReceiptId(receipt_id))
        if receipt is None:
            raise ReceiptNotFoundError(receipt_id)
        return receipt
