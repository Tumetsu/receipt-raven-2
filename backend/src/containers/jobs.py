from dependency_injector import containers, providers

from src.application.jobs.commands.retry_job_use_case import RetryJobUseCase
from src.application.jobs.commands.upload_receipt_document_use_case import (
    UploadReceiptDocumentUseCase,
)
from src.application.jobs.queries.get_receipt_document_use_case import (
    GetReceiptDocumentUseCase,
)
from src.application.jobs.queries.list_jobs_use_case import ListJobsUseCase


class JobsContainer(containers.DeclarativeContainer):
    """Jobs module use cases: uploads and the analysis queue."""

    settings = providers.Dependency()
    receipt_job_repository = providers.Dependency()
    job_list_query = providers.Dependency()
    document_storage = providers.Dependency()
    uploads_cleanup = providers.Dependency()

    upload_receipt_document_use_case = providers.Factory(
        UploadReceiptDocumentUseCase,
        job_repository=receipt_job_repository,
        document_storage=document_storage,
        uploads_cleanup=uploads_cleanup,
        max_upload_bytes=providers.Callable(
            lambda megabytes: int(megabytes * 1024 * 1024), settings.provided.MAX_UPLOAD_SIZE_MB
        ),
    )
    retry_job_use_case = providers.Factory(RetryJobUseCase, job_repository=receipt_job_repository)
    list_jobs_use_case = providers.Factory(ListJobsUseCase, job_list_query=job_list_query)
    get_receipt_document_use_case = providers.Factory(
        GetReceiptDocumentUseCase, document_storage=document_storage
    )
