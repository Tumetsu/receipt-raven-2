"""Background loop that analyses uploaded documents one at a time."""

import asyncio
from collections.abc import Callable

import structlog
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.application.analysis.commands.process_next_job_use_case import ProcessNextJobUseCase
from src.database import bind_db_session
from src.domain.jobs.entities.receipt_job import JobStatus

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
        """Process the next waiting job. Returns whether it succeeded.

        False also when no job was waiting: either way the loop pauses, so a
        failing job is retried after the poll interval rather than at once.
        """
        async with self.session_factory() as db:
            with bind_db_session(db):
                use_case = self.use_case_provider()
            job = await use_case.process_next_job()
            return job is not None and job.status is JobStatus.PROCESSED

    async def run_forever(self) -> None:
        logger.info("job_worker_started", poll_interval=self.poll_interval)
        while True:
            try:
                if await self.run_once():
                    continue  # More may be waiting: no pause after a success.
            except asyncio.CancelledError:
                raise
            except Exception:
                logger.exception("job_worker_iteration_failed")
            await asyncio.sleep(self.poll_interval)
