"""Uploaded documents as files in a local directory."""

import asyncio
import re
import time
from pathlib import Path

from src.domain.jobs.exceptions import ReceiptDocumentNotFoundError

_UNSAFE_CHARACTERS = re.compile(r"[^A-Za-z0-9._-]+")
MAX_NAME_LENGTH = 100


def safe_filename(original: str) -> str:
    """Reduce a client-supplied filename to a safe, readable basename."""
    basename = original.replace("\\", "/").rsplit("/", 1)[-1]
    cleaned = _UNSAFE_CHARACTERS.sub("_", basename).strip("._")
    return cleaned[-MAX_NAME_LENGTH:] or "receipt"


class LocalDocumentStorage:
    """Stores each document as `<milliseconds>-<safe name>` in one directory."""

    def __init__(self, directory: Path) -> None:
        self.directory = directory

    async def store(self, original_filename: str, content: bytes) -> str:
        self.directory.mkdir(parents=True, exist_ok=True)
        filename = f"{time.time_ns() // 1_000_000}-{safe_filename(original_filename)}"
        await asyncio.to_thread((self.directory / filename).write_bytes, content)
        return filename

    async def read(self, filename: str) -> bytes:
        path = self.locate(filename)
        if path is None:
            raise ReceiptDocumentNotFoundError(filename)
        return await asyncio.to_thread(path.read_bytes)

    def locate(self, filename: str) -> Path | None:
        directory = self.directory.resolve()
        path = (directory / filename).resolve()
        # Reject path traversal out of the uploads directory.
        if path.parent != directory or not path.is_file():
            return None
        return path
