"""Repository for ReceiptJob aggregates."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.jobs.entities.receipt_job import JobStatus, ReceiptJob
from src.infrastructure.common.repositories import BaseRepository
from src.infrastructure.jobs.mappers.receipt_job_mapper import ReceiptJobMapper
from src.infrastructure.jobs.orm.receipt_job_model import ReceiptJobModel


class ReceiptJobRepository(BaseRepository[ReceiptJob, ReceiptJobModel]):
    """Stores jobs. ``find_by_id`` and ``save`` come from the base class."""

    def __init__(self, db: AsyncSession) -> None:
        super().__init__(db, ReceiptJobModel, ReceiptJobMapper())

    async def find_next_waiting(self) -> ReceiptJob | None:
        stmt = (
            select(ReceiptJobModel)
            .where(ReceiptJobModel.status == JobStatus.WAITING.value)
            .order_by(ReceiptJobModel.created_at, ReceiptJobModel.id)
            .limit(1)
        )
        row = await self.db.scalar(stmt)
        return self._mapper.to_domain(row) if row is not None else None
