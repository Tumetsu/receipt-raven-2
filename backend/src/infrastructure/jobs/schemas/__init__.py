"""Response schemas for the jobs API."""

import datetime as dt
from typing import Literal

from pydantic import BaseModel


class Job(BaseModel):
    """An uploaded receipt document and its analysis status."""

    id: int
    filename: str
    mime_type: str
    status: Literal["waiting", "processed", "failed"]
    retry_count: int
    analysis_error: str | None
    document_url: str
    created_at: dt.datetime
    processed_at: dt.datetime | None


__all__ = ["Job"]
