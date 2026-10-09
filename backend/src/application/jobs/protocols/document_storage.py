"""Port to where uploaded receipt documents are kept."""

from pathlib import Path
from typing import Protocol


class DocumentStorageProtocol(Protocol):
    """Store uploaded documents under unique names and give them back."""

    async def store(self, original_filename: str, content: bytes) -> str:
        """Store the document and return the unique filename it is kept under."""
        ...

    async def read(self, filename: str) -> bytes:
        """Return the document's bytes.

        Raises:
            ReceiptDocumentNotFoundError: If no document has that name.
        """
        ...

    def locate(self, filename: str) -> Path | None:
        """Return the document's path, or None when it is not stored."""
        ...


class UploadsCleanupProtocol(Protocol):
    """Keeps the stored documents under their disk budget."""

    def schedule(self) -> None:
        """Start a cleanup in the background, if a budget is configured."""
        ...
