"""Response schemas shared by every module."""

from pydantic import BaseModel


class CollectionResponse[T](BaseModel):
    """Return-all list wrapper (no pagination)."""

    items: list[T]


class PaginatedResponse[T](BaseModel):
    """Paginated list wrapper."""

    items: list[T]
    total: int
    offset: int
    limit: int


class ErrorResponse(BaseModel):
    """Body of every error response the domain error handler produces."""

    error: str
    message: str


__all__ = ["CollectionResponse", "ErrorResponse", "PaginatedResponse"]
