"""Port for storing ReceiptJob aggregates."""

from typing import Protocol

from src.domain.common.value_objects import ReceiptJobId
from src.domain.jobs.entities.receipt_job import ReceiptJob


class ReceiptJobRepositoryProtocol(Protocol):
    """Load and store jobs, and pick the next one to analyse."""

    async def find_by_id(self, job_id: ReceiptJobId, /) -> ReceiptJob | None:
        """Return the job, or ``None`` when there is no such job."""
        ...

    async def find_next_waiting(self) -> ReceiptJob | None:
        """Return the oldest job waiting for analysis, or ``None``."""
        ...

    async def save(self, job: ReceiptJob, /) -> ReceiptJob:
        """Insert a new job (id 0) or update an existing one."""
        ...
