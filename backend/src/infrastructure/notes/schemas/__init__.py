"""Request and response schemas for the notes API."""

from datetime import datetime

from pydantic import BaseModel, Field


class NoteRequest(BaseModel):
    """Body of the create and update requests."""

    title: str = Field(..., min_length=1, max_length=200)
    body: str = ""


class Note(BaseModel):
    """A note."""

    id: int
    title: str
    body: str
    created_at: datetime
    updated_at: datetime


class NoteListItem(BaseModel):
    """A note as the list shows it."""

    id: int
    title: str
    body_preview: str
    updated_at: datetime


__all__ = ["Note", "NoteListItem", "NoteRequest"]
