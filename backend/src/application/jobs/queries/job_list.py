"""Read model for the job list. View DTOs only; see the receipt list for the rules."""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from src.application.common.pagination import Page, PageRequest
from src.domain.jobs.entities.receipt_job import JobStatus


@dataclass(frozen=True)
class JobListItemView:
    """One row of the job list."""

    id: int
    filename: str
    mime_type: str
    status: JobStatus
    retry_count: int
    analysis_error: str | None
    created_at: datetime
    processed_at: datetime | None


class JobListQueryProtocol(Protocol):
    """Port for reading the job list."""

    async def list_jobs(self, page: PageRequest) -> Page[JobListItemView]:
        """Return jobs, newest first."""
        ...
