"""Jobs domain exceptions."""

from src.domain.common.exceptions import ConflictError, EntityNotFoundError


class ReceiptJobNotFoundError(EntityNotFoundError):
    """Raised when a job cannot be found."""

    def __init__(self, job_id: int) -> None:
        super().__init__("Job", job_id)
        self.job_id = job_id


class JobNotRetryableError(ConflictError):
    """Raised when a job that has not failed is retried."""

    def __init__(self, job_id: int) -> None:
        super().__init__("Only a failed job can be retried", {"job_id": job_id})
        self.job_id = job_id


class ReceiptDocumentNotFoundError(EntityNotFoundError):
    """Raised when an uploaded document is not stored (or was cleaned up)."""

    def __init__(self, filename: str) -> None:
        super().__init__("Document", filename)
        self.filename = filename
