"""Pagination shared by the list read models."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PageRequest:
    """Which slice of a list to read."""

    offset: int = 0
    limit: int = 30


@dataclass(frozen=True)
class Page[T]:
    """One slice of a list and the size of the whole list."""

    items: tuple[T, ...]
    total: int
    offset: int
    limit: int
