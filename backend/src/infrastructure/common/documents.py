"""URLs of uploaded documents, as the API returns them."""

from urllib.parse import quote

from src.config import get_settings


def document_url(filename: str) -> str:
    """The URL the `get_receipt_document` endpoint serves the document at."""
    return f"{get_settings().API_V1_PREFIX}/documents/{quote(filename)}"
