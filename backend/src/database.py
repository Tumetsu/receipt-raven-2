"""Database configuration and session management."""

from collections.abc import AsyncGenerator, Generator
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Annotated

from fastapi import Depends
from sqlalchemy import MetaData
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.pool import StaticPool

from src.config import Settings, get_settings, normalize_database_url

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
    """Convert a database URL to its async-compatible dialect."""
    url = normalize_database_url(url)
    if url.startswith("sqlite://"):
        return url.replace("sqlite://", "sqlite+aiosqlite://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    return url


def initialize_database(settings: Settings) -> None:
    """Create the engine and session factory once at startup. Later calls are no-ops."""
    global _engine, _session_factory  # noqa: PLW0603

    if _engine is not None:
        return

    async_url = make_async_url(settings.DATABASE_URL)
    if async_url.startswith("sqlite"):
        _engine = create_async_engine(
            async_url,
            connect_args={"check_same_thread": False},
            poolclass=StaticPool,
        )
    else:
        _engine = create_async_engine(
            async_url,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True,
            pool_recycle=3600,
        )

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
