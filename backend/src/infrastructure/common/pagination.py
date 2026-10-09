"""Pagination helpers for query adapters."""

from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.application.common.pagination import PageRequest


async def count_rows(db: AsyncSession, stmt: Select[*tuple[Any, ...]]) -> int:
    """Count the rows a select would return, ignoring its ordering."""
    subquery = stmt.order_by(None).subquery()
    return int(await db.scalar(select(func.count()).select_from(subquery)) or 0)


def page_of[S: Select[*tuple[Any, ...]]](stmt: S, page: PageRequest) -> S:
    """Limit a select to one page."""
    return stmt.offset(page.offset).limit(page.limit)
