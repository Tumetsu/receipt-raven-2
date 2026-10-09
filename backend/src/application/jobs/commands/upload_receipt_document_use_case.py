"""Use case for uploading a receipt photo or PDF for analysis."""

import structlog

from src.application.jobs.protocols.document_storage import (
    DocumentStorageProtocol,
    UploadsCleanupProtocol,
)
from src.application.jobs.protocols.receipt_job_repository import ReceiptJobRepositoryProtocol
from src.domain.common.exceptions import ValidationError
from src.domain.jobs.entities.receipt_job import ReceiptJob

logger = structlog.get_logger(__name__)

PDF_MIME_TYPE = "application/pdf"


def is_supported_document(mime_type: str) -> bool:
    """The analysis reads images and PDFs."""
    return mime_type.startswith("image/") or mime_type == PDF_MIME_TYPE


class UploadReceiptDocumentUseCase:
    """Store an uploaded document and queue it for analysis."""

    def __init__(
        self,
        job_repository: ReceiptJobRepositoryProtocol,
        document_storage: DocumentStorageProtocol,
        uploads_cleanup: UploadsCleanupProtocol,
        max_upload_bytes: int,
    ) -> None:
        self.job_repository = job_repository
        self.document_storage = document_storage
        self.uploads_cleanup = uploads_cleanup
        self.max_upload_bytes = max_upload_bytes

    async def upload(self, original_filename: str, mime_type: str, content: bytes) -> ReceiptJob:
        """Store the document and create its job.

        Raises:
            ValidationError: If the file is empty, too large or not an image or PDF.
        """
        if not is_supported_document(mime_type):
            raise ValidationError("Upload a photo or a PDF of the receipt", field="file")
        if not content:
            raise ValidationError("The uploaded file is empty", field="file")
        if len(content) > self.max_upload_bytes:
            limit_mb = self.max_upload_bytes / (1024 * 1024)
            raise ValidationError(f"The file is larger than {limit_mb:g} MB", field="file")

        filename = await self.document_storage.store(original_filename, content)
        job = await self.job_repository.save(ReceiptJob.create(filename, mime_type))
        logger.info("receipt_document_uploaded", job_id=job.id.value, filename=filename)
        self.uploads_cleanup.schedule()
        return job
