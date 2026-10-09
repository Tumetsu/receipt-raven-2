"""Query parameters shared by the paginated list endpoints."""

from typing import Annotated

from fastapi import Query

from src.application.common.pagination import PageRequest

MAX_PAGE_SIZE = 100


def page_request(
    offset: Annotated[int, Query(ge=0, description="Index of the first item")] = 0,
    limit: Annotated[
        int, Query(ge=1, le=MAX_PAGE_SIZE, description="Number of items per page")
    ] = 30,
) -> PageRequest:
    """FastAPI dependency reading `offset` and `limit`."""
    return PageRequest(offset=offset, limit=limit)
