"""Application configuration."""

import logging
import sys
import tomllib
from functools import lru_cache
from pathlib import Path
from typing import Literal

import structlog
from pydantic_settings import BaseSettings, SettingsConfigDict

BACKEND_ROOT = Path(__file__).parent.parent.resolve()


def _read_project_version() -> str:
    """Read the release version from `pyproject.toml`.

    The Docker image copies the manifest next to `src/`, so the same file is the
    version source in development and in the container.
    """
    manifest = BACKEND_ROOT / "pyproject.toml"
    try:
        with manifest.open("rb") as handle:
            return str(tomllib.load(handle)["project"]["version"])
    except (OSError, KeyError, tomllib.TOMLDecodeError):
        logging.getLogger(__name__).warning("Could not read version from %s", manifest)
        return "unknown"


def normalize_database_url(url: str) -> str:
    """Rewrite the legacy `postgres://` scheme to the `postgresql://` SQLAlchemy needs.

    Hosted Postgres providers still hand out `postgres://` URLs, which SQLAlchemy
    rejects. Normalizing at the edge keeps the engine and Alembic working
    whichever spelling the provider chose.
    """
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql://", 1)
    return url


class Settings(BaseSettings):
    """Application settings, read from the environment and `.env`."""

    # env_ignore_empty: docker compose passes `${VAR:-}` as an empty string,
    # which must mean "unset", not an empty value.
    model_config = SettingsConfigDict(
        env_file=("../.env", ".env"), env_file_encoding="utf-8", env_ignore_empty=True
    )

    DATABASE_URL: str = (
        "postgresql://receipt_raven:receipt_raven_dev_password@localhost:5432/receipt_raven"
    )

    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "Receipt Raven"
    VERSION: str = _read_project_version()

    ENVIRONMENT: Literal["development", "production", "test"] = "development"
    LOG_LEVEL: str = "INFO"

    CORS_ORIGINS: list[str] = ["http://localhost:5173"]


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings."""
    return Settings()


def configure_logging(settings: Settings) -> None:
    """Configure structlog: JSON in production, coloured console output elsewhere."""
    renderer: structlog.types.Processor = (
        structlog.processors.JSONRenderer()
        if settings.ENVIRONMENT == "production"
        else structlog.dev.ConsoleRenderer()
    )
    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=settings.LOG_LEVEL)
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            renderer,
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelNamesMapping()[settings.LOG_LEVEL]
        ),
        cache_logger_on_first_use=True,
    )
