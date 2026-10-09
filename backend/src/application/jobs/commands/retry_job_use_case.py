"""Use case for retrying a failed analysis."""

from src.application.jobs.protocols.receipt_job_repository import ReceiptJobRepositoryProtocol
from src.domain.common.value_objects import ReceiptJobId
from src.domain.jobs.entities.receipt_job import ReceiptJob
from src.domain.jobs.exceptions import ReceiptJobNotFoundError


class RetryJobUseCase:
    """Queue a failed job for analysis again."""

    def __init__(self, job_repository: ReceiptJobRepositoryProtocol) -> None:
        self.job_repository = job_repository

    async def retry_job(self, job_id: int) -> ReceiptJob:
        """Requeue the job.

        Raises:
            ReceiptJobNotFoundError: If there is no such job.
            JobNotRetryableError: If the job has not failed.
        """
        job = await self.job_repository.find_by_id(ReceiptJobId(job_id))
        if job is None:
            raise ReceiptJobNotFoundError(job_id)
        job.retry()
        return await self.job_repository.save(job)
