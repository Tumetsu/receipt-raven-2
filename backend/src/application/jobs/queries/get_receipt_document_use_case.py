"""Read use case for an uploaded document, to show it next to its receipt or job."""

from pathlib import Path

from src.application.jobs.protocols.document_storage import DocumentStorageProtocol
from src.domain.jobs.exceptions import ReceiptDocumentNotFoundError


class GetReceiptDocumentUseCase:
    """Find a stored document."""

    def __init__(self, document_storage: DocumentStorageProtocol) -> None:
        self.document_storage = document_storage

    def locate(self, filename: str) -> Path:
        """Return the document's path.

        Raises:
            ReceiptDocumentNotFoundError: If it is not stored, for example after cleanup.
        """
        path = self.document_storage.locate(filename)
        if path is None:
            raise ReceiptDocumentNotFoundError(filename)
        return path
