"""Query adapter for the job list."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.common.pagination import Page, PageRequest
from src.application.jobs.queries.job_list import JobListItemView
from src.domain.jobs.entities.receipt_job import JobStatus
from src.infrastructure.common.pagination import count_rows, page_of
from src.infrastructure.jobs.orm.receipt_job_model import ReceiptJobModel


class JobListQuery:
    """Serves the job list read model."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def list_jobs(self, page: PageRequest) -> Page[JobListItemView]:
        stmt = select(ReceiptJobModel).order_by(
            ReceiptJobModel.created_at.desc(), ReceiptJobModel.id.desc()
        )
        total = await count_rows(self.db, stmt)
        rows = (await self.db.scalars(page_of(stmt, page))).all()
        return Page(
            items=tuple(
                JobListItemView(
                    id=row.id,
                    filename=row.filename,
                    mime_type=row.mime_type,
                    status=JobStatus(row.status),
                    retry_count=row.retry_count,
                    analysis_error=row.analysis_error,
                    created_at=row.created_at,
                    processed_at=row.processed_at,
                )
                for row in rows
            ),
            total=total,
            offset=page.offset,
            limit=page.limit,
        )
