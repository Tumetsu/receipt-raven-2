"""FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.config import configure_logging, get_settings
from src.database import dispose_engine, initialize_database
from src.infrastructure.common.error_handlers import register_error_handlers
from src.infrastructure.common.middleware import (
    RequestIdAndLoggingMiddleware,
    SecurityHeadersMiddleware,
)
from src.infrastructure.common.openapi import operation_id
from src.infrastructure.common.spa import mount_spa
from src.infrastructure.notes.routers import notes as notes_router

settings = get_settings()
configure_logging(settings)
logger = structlog.get_logger(__name__)

# The Docker image copies the frontend build here; absent in development.
STATIC_DIR = Path(__file__).parent.parent / "static"


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None]:
    """Create the database engine on startup and dispose of it on shutdown."""
    initialize_database(settings)
    logger.info("app_started", environment=settings.ENVIRONMENT, version=settings.VERSION)
    yield
    await dispose_engine()


_docs_enabled = settings.ENVIRONMENT != "production"

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    docs_url=f"{settings.API_V1_PREFIX}/docs" if _docs_enabled else None,
    redoc_url=None,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json" if _docs_enabled else None,
    lifespan=lifespan,
    generate_unique_id_function=operation_id,
)

app.add_middleware(RequestIdAndLoggingMiddleware, api_prefix=settings.API_V1_PREFIX)
app.add_middleware(SecurityHeadersMiddleware, production=settings.ENVIRONMENT == "production")
# With wildcard origins, browsers reject credentials, so only allow them otherwise.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials="*" not in settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_error_handlers(app)


@app.get("/health", include_in_schema=False)
async def health() -> dict[str, str]:
    """Liveness probe for Docker and load balancers."""
    return {"status": "healthy"}


# Routers, one block per module
app.include_router(notes_router.router, prefix=settings.API_V1_PREFIX)

# Last: its catch-all route would otherwise shadow the API.
mount_spa(app, STATIC_DIR, settings.API_V1_PREFIX)
