"""Repository for Receipt aggregates."""

from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.receipts.entities.receipt import Receipt
from src.infrastructure.common.repositories import BaseRepository
from src.infrastructure.receipts.mappers.receipt_mapper import ReceiptMapper
from src.infrastructure.receipts.orm.receipt_model import ReceiptModel


class ReceiptRepository(BaseRepository[Receipt, ReceiptModel]):
    """Stores receipts with their items (loaded eagerly, deleted with the receipt)."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, ReceiptModel, ReceiptMapper())
