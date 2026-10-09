"""Alembic environment: runs migrations against DATABASE_URL with the app's metadata."""

from logging.config import fileConfig
from typing import Literal

from sqlalchemy import engine_from_config, pool

from alembic import context
from src.config import get_settings, sqlite_file_path
from src.infrastructure.common.orm_types import UTCDateTime
from src.models import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# Same source as the app (environment, then .env). Alembic runs synchronously,
# on the standard library's sqlite3 driver.
database_url = get_settings().DATABASE_URL
db_file = sqlite_file_path(database_url)
if db_file is not None:
    db_file.parent.mkdir(parents=True, exist_ok=True)
config.set_main_option("sqlalchemy.url", database_url)


def render_item(type_: str, obj: object, _autogen_context: object) -> str | Literal[False]:
    """Render app-specific column types as the plain type they store."""
    if type_ == "type" and isinstance(obj, UTCDateTime):
        return "sa.DateTime()"
    return False


def run_migrations_offline() -> None:
    """Emit SQL to stdout instead of running against a database."""
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        render_as_batch=True,
        render_item=render_item,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against the database."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        # SQLite cannot ALTER most of a table; batch mode recreates it instead.
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            render_as_batch=True,
            render_item=render_item,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
