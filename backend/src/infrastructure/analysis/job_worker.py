"""Background loop that analyses uploaded documents one at a time."""

import asyncio
from collections.abc import Callable

import structlog
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.analysis.commands.process_next_job_use_case import ProcessNextJobUseCase
from src.database import bind_db_session

logger = structlog.get_logger(__name__)


class JobWorker:
    """Polls for waiting jobs and processes them, each in its own session.

    One worker per process keeps the analysis sequential, as the original app
    did: the AI provider is the bottleneck, and SQLite has one writer anyway.
    """

    def __init__(
        self,
        session_factory: async_sessionmaker[AsyncSession],
        use_case_provider: Callable[[], ProcessNextJobUseCase],
        poll_interval_seconds: float,
    ) -> None:
        self.session_factory = session_factory
        self.use_case_provider = use_case_provider
        self.poll_interval = poll_interval_seconds

    async def run_once(self) -> bool:
        """Process the next waiting job. Returns whether there was one."""
        async with self.session_factory() as db:
            with bind_db_session(db):
                use_case = self.use_case_provider()
            return await use_case.process_next_job() is not None

    async def run_forever(self) -> None:
        logger.info("job_worker_started", poll_interval=self.poll_interval)
        while True:
            try:
                if await self.run_once():
                    continue  # More may be waiting: do not sleep between jobs.
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("job_worker_iteration_failed")
            await asyncio.sleep(self.poll_interval)
