"""Keep the uploads directory under a disk budget by deleting the oldest documents.

The receipts keep their data; only the photo or PDF goes, which the UI then
shows as missing.
"""

import asyncio
import re
from dataclasses import dataclass
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)

_SIZE_PATTERN = re.compile(r"^(\d+(?:\.\d+)?)\s*(GB|MB|KB|B)$", re.IGNORECASE)
_MULTIPLIERS = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3}


def parse_disk_size(text: str) -> int | None:
    """Parse a size such as "1GB", "500MB" or "1.5 GB" to bytes; None if invalid."""
    match = _SIZE_PATTERN.match(text.strip())
    if match is None:
        return None
    return int(float(match.group(1)) * _MULTIPLIERS[match.group(2).upper()])


@dataclass(frozen=True)
class CleanupResult:
    deleted_files: int
    freed_bytes: int
    size_before: int
    size_after: int


def cleanup_directory(directory: Path, max_bytes: int) -> CleanupResult:
    """Delete the least recently modified files until the directory fits `max_bytes`."""
    if not directory.is_dir():
        return CleanupResult(0, 0, 0, 0)
    files = [(path, path.stat()) for path in directory.iterdir() if path.is_file()]
    size = size_before = sum(stat.st_size for _, stat in files)
    deleted = 0
    for path, stat in sorted(files, key=lambda entry: entry[1].st_mtime):
        if size <= max_bytes:
            break
        try:
            path.unlink()
        except OSError as exc:
            logger.warning("upload_cleanup_delete_failed", file=path.name, error=str(exc))
            continue
        size -= stat.st_size
        deleted += 1
    return CleanupResult(deleted, size_before - size, size_before, size)


class UploadsCleanup:
    """Runs `cleanup_directory` on the uploads directory when a budget is configured."""

    def __init__(self, directory: Path, max_disk_size: str | None) -> None:
        self.directory = directory
        self.max_bytes = parse_disk_size(max_disk_size) if max_disk_size else None
        if max_disk_size and self.max_bytes is None:
            logger.warning("invalid_max_uploads_disk_size", value=max_disk_size)
        self._tasks: set[asyncio.Task[None]] = set()

    @property
    def enabled(self) -> bool:
        return self.max_bytes is not None

    async def run(self) -> None:
        if self.max_bytes is None:
            return
        result = await asyncio.to_thread(cleanup_directory, self.directory, self.max_bytes)
        if result.deleted_files:
            logger.info(
                "uploads_cleaned_up",
                deleted_files=result.deleted_files,
                freed_bytes=result.freed_bytes,
                size_after=result.size_after,
            )

    def schedule(self) -> None:
        if self.max_bytes is None:
            return
        task = asyncio.create_task(self.run())
        # Keep a reference until done, or the task may be garbage collected mid-run.
        self._tasks.add(task)
        task.add_done_callback(self._tasks.discard)
