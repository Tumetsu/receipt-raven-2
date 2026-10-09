"""ReceiptJob aggregate: an uploaded document and its trip through the analysis.

A job waits until the analysis worker picks it up. Success marks it processed;
a failure puts it back in the queue until it has failed `max_attempts` times,
after which it stays failed until the user retries it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum

from src.domain.common.aggregate_root import AggregateRoot
from src.domain.common.exceptions import ValidationError
from src.domain.common.value_objects import ReceiptJobId
from src.domain.jobs.exceptions import JobNotRetryableError


def _now() -> datetime:
    return datetime.now(UTC)


class JobStatus(StrEnum):
    """Where the job is in the analysis."""

    WAITING = "waiting"
    PROCESSED = "processed"
    FAILED = "failed"


@dataclass(eq=False)
class ReceiptJob(AggregateRoot[ReceiptJobId]):
    """
    An uploaded receipt document queued for analysis.

    Business rules:
    - Every failed attempt counts; the job fails for good after `max_attempts`
    - Only a failed job can be retried, which gives it a fresh set of attempts
    """

    id: ReceiptJobId
    filename: str
    mime_type: str
    status: JobStatus = JobStatus.WAITING
    retry_count: int = 0
    analysis_error: str | None = None
    created_at: datetime = field(default_factory=_now)
    updated_at: datetime = field(default_factory=_now)
    processed_at: datetime | None = None

    def __post_init__(self) -> None:
        if not self.filename.strip():
            raise ValidationError("A job needs a document file", field="filename")

    @classmethod
    def create(cls, filename: str, mime_type: str) -> ReceiptJob:
        """Queue a stored document for analysis."""
        return cls(id=ReceiptJobId.generate(), filename=filename, mime_type=mime_type)

    def mark_processed(self) -> None:
        """Record a successful analysis."""
        now = _now()
        self.status = JobStatus.PROCESSED
        self.analysis_error = None
        self.processed_at = now
        self.updated_at = now

    def record_failure(self, error: str, max_attempts: int) -> None:
        """Record a failed attempt; queue the job again unless it is out of attempts."""
        self.retry_count += 1
        self.analysis_error = error
        self.status = JobStatus.WAITING if self.retry_count < max_attempts else JobStatus.FAILED
        self.updated_at = _now()

    def retry(self) -> None:
        """Queue a failed job again with a fresh set of attempts.

        Raises:
            JobNotRetryableError: If the job has not failed.
        """
        if self.status is not JobStatus.FAILED:
            raise JobNotRetryableError(self.id.value)
        self.status = JobStatus.WAITING
        self.retry_count = 0
        self.analysis_error = None
        self.updated_at = _now()
