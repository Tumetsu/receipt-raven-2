"""Mapper for ReceiptJob ORM <-> domain conversion."""

from src.domain.common.value_objects import ReceiptJobId
from src.domain.jobs.entities.receipt_job import JobStatus, ReceiptJob
from src.infrastructure.common.mappers import orm_id
from src.infrastructure.jobs.orm.receipt_job_model import ReceiptJobModel


class ReceiptJobMapper:
    """Convert between the ReceiptJob aggregate and its row."""

    def to_domain(self, orm_model: ReceiptJobModel) -> ReceiptJob:
        return ReceiptJob(
            id=ReceiptJobId(orm_model.id),
            filename=orm_model.filename,
            mime_type=orm_model.mime_type,
            status=JobStatus(orm_model.status),
            retry_count=orm_model.retry_count,
            analysis_error=orm_model.analysis_error,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
            processed_at=orm_model.processed_at,
        )

    def to_orm(
        self, domain_entity: ReceiptJob, orm_model: ReceiptJobModel | None = None
    ) -> ReceiptJobModel:
        if orm_model is None:
            orm_model = ReceiptJobModel(id=orm_id(domain_entity.id))
        orm_model.filename = domain_entity.filename
        orm_model.mime_type = domain_entity.mime_type
        orm_model.status = domain_entity.status.value
        orm_model.retry_count = domain_entity.retry_count
        orm_model.analysis_error = domain_entity.analysis_error
        orm_model.created_at = domain_entity.created_at
        orm_model.updated_at = domain_entity.updated_at
        orm_model.processed_at = domain_entity.processed_at
        return orm_model
