"""Read use case for the job list."""

from src.application.common.pagination import Page, PageRequest
from src.application.jobs.queries.job_list import JobListItemView, JobListQueryProtocol


class ListJobsUseCase:
    """Serve one page of the job list from its query port."""

    def __init__(self, job_list_query: JobListQueryProtocol) -> None:
        self.job_list_query = job_list_query

    async def list_jobs(self, page: PageRequest) -> Page[JobListItemView]:
        return await self.job_list_query.list_jobs(page)
