"""Database configuration and session management."""

from collections.abc import AsyncGenerator, Generator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Annotated

from fastapi import Depends
from sqlalchemy import MetaData, event
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool

from src.config import Settings, get_settings, sqlite_file_path

# Deterministic constraint names, so Alembic autogenerate can drop and rename
# constraints instead of guessing at database-generated names.
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(DeclarativeBase):
    """Base class for all ORM models."""

    metadata = MetaData(naming_convention=NAMING_CONVENTION)


# Module-level singletons (application-scoped)
_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def make_async_url(url: str) -> str:
    """Convert a SQLite URL to its async (aiosqlite) dialect."""
    if url.startswith("sqlite://"):
        return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    return url


def _configure_sqlite_connection(dbapi_connection: DBAPIConnection, _record: object) -> None:
    """Per-connection SQLite settings.

    Foreign keys are off by default in SQLite. WAL lets the analysis worker
    write while requests read, and the busy timeout makes a writer wait for
    the other instead of failing with "database is locked".
    """
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=5000")
    cursor.close()


def create_engine_for(url: str) -> AsyncEngine:
    """Create the async engine for a SQLite URL, creating the file's directory.

    An in-memory database lives as long as its one connection, so it gets a
    single shared connection (StaticPool); a file database gets a pool.
    """
    db_file = sqlite_file_path(url)
    if db_file is None:
        engine = create_async_engine(
            make_async_url(url),
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        db_file.parent.mkdir(parents=True, exist_ok=True)
        engine = create_async_engine(make_async_url(url))
    event.listen(engine.sync_engine, "connect", _configure_sqlite_connection)
    return engine


def initialize_database(settings: Settings) -> None:
    """Create the engine and session factory once at startup. Later calls are no-ops."""
    global _engine, _session_factory  # noqa: PLW0603

    if _engine is not None:
        return

    _engine = create_engine_for(settings.DATABASE_URL)
    _session_factory = async_sessionmaker(
        autocommit=False, autoflush=False, expire_on_commit=False, bind=_engine
    )


def get_session_factory(
    settings: Annotated[Settings, Depends(get_settings)],
) -> async_sessionmaker[AsyncSession]:
    """Return the session factory, initializing the database on first use."""
    if _session_factory is None:
        initialize_database(settings)
    if _session_factory is None:
        raise RuntimeError("Failed to initialize database session factory.")
    return _session_factory


async def dispose_engine() -> None:
    """Dispose of the engine on shutdown."""
    global _engine, _session_factory  # noqa: PLW0603
    if _engine is not None:
        await _engine.dispose()
        _engine = None
        _session_factory = None


async def get_db(
    session_factory: Annotated[async_sessionmaker[AsyncSession], Depends(get_session_factory)],
) -> AsyncGenerator[AsyncSession]:
    """Yield a database session for one request."""
    async with session_factory() as db:
        yield db


# The session the DI container builds repositories against. A ContextVar rather
# than a module global: every request runs in its own asyncio task with its own
# copy of the context, so concurrent requests cannot see each other's session.
_request_db_session: ContextVar[AsyncSession] = ContextVar("request_db_session")


@contextmanager
def bind_db_session(session: AsyncSession) -> Generator[None]:
    """Bind a database session for the duration of the block."""
    token = _request_db_session.set(session)
    try:
        yield
    finally:
        _request_db_session.reset(token)


def current_db_session() -> AsyncSession:
    """Return the session bound to the current context.

    Raises:
        RuntimeError: If no session is bound, which means a provider was
            resolved outside of a ``bind_db_session`` block.
    """
    try:
        return _request_db_session.get()
    except LookupError as exc:
        msg = (
            "No database session is bound to the current context. "
            "Resolve container providers inside a bind_db_session(...) block."
        )
        raise RuntimeError(msg) from exc


DatabaseSession = Annotated[AsyncSession, Depends(get_db)]
