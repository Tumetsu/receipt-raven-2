"""Column types shared by the ORM models."""

from datetime import UTC, datetime

from sqlalchemy import DateTime
from sqlalchemy.engine import Dialect
from sqlalchemy.types import TypeDecorator


class UTCDateTime(TypeDecorator[datetime]):
    """A timezone-aware UTC timestamp.

    SQLite stores no time zone, so values come back naive. This stores them in
    UTC and returns them aware, as the domain expects.
    """

    impl = DateTime
    cache_ok = True

    def process_bind_param(self, value: datetime | None, dialect: Dialect) -> datetime | None:
        if value is None:
            return None
        if value.tzinfo is None:
            raise ValueError("UTCDateTime needs a timezone-aware datetime")
        return value.astimezone(UTC).replace(tzinfo=None)

    def process_result_value(self, value: object, dialect: Dialect) -> datetime | None:
        if value is None:
            return None
        assert isinstance(value, datetime)  # noqa: S101 - the impl type is DateTime
        return value.replace(tzinfo=UTC)
