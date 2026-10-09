"""Unit tests for the uploads disk budget."""

import os
from pathlib import Path

import pytest

from src.infrastructure.jobs.storage.local_document_storage import safe_filename
from src.infrastructure.jobs.storage.uploads_cleanup import cleanup_directory, parse_disk_size


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("1GB", 1024**3),
        ("500mb", 500 * 1024**2),
        ("1.5 GB", int(1.5 * 1024**3)),
        ("10B", 10),
        ("lots", None),
        ("-1GB", None),
    ],
)
def test_parse_disk_size(text: str, expected: int | None) -> None:
    assert parse_disk_size(text) == expected


def test_deletes_oldest_files_until_under_budget(tmp_path: Path) -> None:
    for age, name in enumerate(["newest", "middle", "oldest"]):
        path = tmp_path / name
        path.write_bytes(b"x" * 100)
        os.utime(path, (1_000_000 - age * 1000, 1_000_000 - age * 1000))

    result = cleanup_directory(tmp_path, max_bytes=150)

    assert sorted(p.name for p in tmp_path.iterdir()) == ["newest"]
    assert (result.deleted_files, result.size_before, result.size_after) == (2, 300, 100)


@pytest.mark.parametrize(
    ("original", "expected"),
    [
        ("camera capture.jpg", "camera_capture.jpg"),
        ("../../etc/passwd", "passwd"),
        ("C:\\Users\\me\\Kuitti ä.pdf", "Kuitti_.pdf"),
        ("...", "receipt"),
    ],
)
def test_safe_filename(original: str, expected: str) -> None:
    assert safe_filename(original) == expected
