"""Guards on the generated OpenAPI document, which the frontend client is built from."""

import json
from collections import Counter
from pathlib import Path
from typing import Any

from src.main import app

HTTP_METHODS = {"get", "put", "post", "delete", "options", "head", "patch", "trace"}
COMMITTED_SCHEMA = Path(__file__).resolve().parent.parent / "openapi.json"


def _operations() -> list[tuple[str, str, dict[str, Any]]]:
    """Every (path, method, operation) in the schema, ignoring path-level keys."""
    schema = app.openapi()
    return [
        (path, method, operation)
        for path, item in schema["paths"].items()
        for method, operation in item.items()
        if method in HTTP_METHODS
    ]


def test_operation_ids_are_unique() -> None:
    """
    Handler names are the operationIds, so a duplicate name anywhere in the app
    would merge two operations into one and silently drop it from the generated
    client. Rename one of the handlers rather than relaxing this.
    """
    counts = Counter(operation["operationId"] for _, _, operation in _operations())
    duplicates = {name: count for name, count in counts.items() if count > 1}

    assert not duplicates, f"Duplicate operationIds: {duplicates}"


def test_committed_schema_matches_the_app() -> None:
    """Run `make api-client` when this fails, and commit the regenerated files."""
    committed = json.loads(COMMITTED_SCHEMA.read_text(encoding="utf-8"))
    current = app.openapi()

    assert committed["paths"] == current["paths"]
    assert committed["components"] == current["components"]
