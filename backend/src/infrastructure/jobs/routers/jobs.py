"""API routes for uploads, the analysis queue and the stored documents."""

from fastapi import APIRouter, Depends, File, UploadFile, status
from fastapi.responses import FileResponse

from src.application.common.pagination import PageRequest
from src.application.jobs.commands.retry_job_use_case import RetryJobUseCase
from src.application.jobs.commands.upload_receipt_document_use_case import (
    UploadReceiptDocumentUseCase,
)
from src.application.jobs.queries.get_receipt_document_use_case import (
    GetReceiptDocumentUseCase,
)
from src.application.jobs.queries.list_jobs_use_case import ListJobsUseCase
from src.containers import container
from src.domain.jobs.entities.receipt_job import ReceiptJob
from src.infrastructure.common.di import inject_use_case
from src.infrastructure.common.documents import document_url
from src.infrastructure.common.schemas import ErrorResponse, PaginatedResponse
from src.infrastructure.common.schemas.pagination import page_request
from src.infrastructure.jobs.schemas import Job

router = APIRouter(tags=["jobs"])

# Read one byte past the limit: enough to tell "too large" without reading it all.
READ_CHUNK_SLACK = 1


def job_to_schema(job: ReceiptJob) -> Job:
    return Job(
        id=job.id.value,
        filename=job.filename,
        mime_type=job.mime_type,
        status=job.status.value,
        retry_count=job.retry_count,
        analysis_error=job.analysis_error,
        document_url=document_url(job.filename),
        created_at=job.created_at,
        processed_at=job.processed_at,
    )


@router.get("/jobs", response_model=PaginatedResponse[Job])
async def list_jobs(
    page: PageRequest = Depends(page_request),
    use_case: ListJobsUseCase = Depends(inject_use_case(container.jobs.list_jobs_use_case)),
) -> PaginatedResponse[Job]:
    result = await use_case.list_jobs(page)
    return PaginatedResponse(
        items=[
            Job(
                id=view.id,
                filename=view.filename,
                mime_type=view.mime_type,
                status=view.status.value,
                retry_count=view.retry_count,
                analysis_error=view.analysis_error,
                document_url=document_url(view.filename),
                created_at=view.created_at,
                processed_at=view.processed_at,
            )
            for view in result.items
        ],
        total=result.total,
        offset=result.offset,
        limit=result.limit,
    )


@router.post(
    "/jobs",
    response_model=Job,
    status_code=status.HTTP_201_CREATED,
    responses={400: {"model": ErrorResponse, "description": "Not an image or PDF, or too large"}},
)
async def upload_receipt(
    file: UploadFile = File(..., description="Photo (image/*) or PDF of the receipt"),
    use_case: UploadReceiptDocumentUseCase = Depends(
        inject_use_case(container.jobs.upload_receipt_document_use_case)
    ),
) -> Job:
    """Upload a receipt document and queue it for analysis."""
    content = await file.read(use_case.max_upload_bytes + READ_CHUNK_SLACK)
    job = await use_case.upload(
        original_filename=file.filename or "receipt",
        mime_type=file.content_type or "application/octet-stream",
        content=content,
    )
    return job_to_schema(job)


@router.post(
    "/jobs/{job_id}/retry",
    response_model=Job,
    responses={
        404: {"model": ErrorResponse, "description": "No such job"},
        409: {"model": ErrorResponse, "description": "The job has not failed"},
    },
)
async def retry_job(
    job_id: int,
    use_case: RetryJobUseCase = Depends(inject_use_case(container.jobs.retry_job_use_case)),
) -> Job:
    """Queue a failed job for analysis again."""
    return job_to_schema(await use_case.retry_job(job_id))


@router.get(
    "/documents/{filename}",
    response_class=FileResponse,
    responses={404: {"model": ErrorResponse, "description": "No such document"}},
)
async def get_receipt_document(
    filename: str,
    use_case: GetReceiptDocumentUseCase = Depends(
        inject_use_case(container.jobs.get_receipt_document_use_case)
    ),
) -> FileResponse:
    """The uploaded photo or PDF."""
    return FileResponse(use_case.locate(filename))
