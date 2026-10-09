"""Use case for typing in a receipt by hand."""

import structlog

from src.application.receipts.commands.receipt_fields import ReceiptFields
from src.application.receipts.protocols.receipt_repository import ReceiptRepositoryProtocol
from src.domain.receipts.entities.receipt import Receipt

logger = structlog.get_logger(__name__)


class CreateReceiptUseCase:
    """Store a receipt the user entered. It starts unapproved, like an analysed one."""

    def __init__(self, receipt_repository: ReceiptRepositoryProtocol) -> None:
        self.receipt_repository = receipt_repository

    async def create_receipt(self, fields: ReceiptFields) -> Receipt:
        receipt = await self.receipt_repository.save(
            Receipt.create_manual(
                payee=fields.payee,
                receipt_date=fields.receipt_date,
                total_sum=fields.total_sum,
                lines=fields.lines,
                description=fields.description,
                source_account=fields.source_account,
            )
        )
        logger.info("receipt_created", receipt_id=receipt.id.value)
        return receipt
