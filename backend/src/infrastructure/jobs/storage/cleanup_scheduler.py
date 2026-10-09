"""Periodic uploads cleanup: once at startup, then every interval."""

import asyncio

import structlog

from src.infrastructure.jobs.storage.uploads_cleanup import UploadsCleanup

logger = structlog.get_logger(__name__)

SECONDS_PER_HOUR = 3600


async def run_cleanup_schedule(cleanup: UploadsCleanup, interval_hours: float) -> None:
    if not cleanup.enabled:
        logger.info("uploads_cleanup_disabled")
        return
    while True:
        try:
            await cleanup.run()
        except Exception:
            logger.exception("uploads_cleanup_failed")
        await asyncio.sleep(interval_hours * SECONDS_PER_HOUR)
