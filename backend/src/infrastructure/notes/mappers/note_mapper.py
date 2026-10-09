"""Mapper for Note ORM <-> domain conversion."""

from src.domain.common.value_objects import NoteId
from src.domain.notes.entities.note import Note
from src.infrastructure.common.mappers import orm_id
from src.infrastructure.notes.orm.note_model import NoteModel


class NoteMapper:
    """Convert between the Note aggregate and its ORM row."""

    def to_domain(self, orm_model: NoteModel) -> Note:
        return Note.create_with_id(
            id=NoteId(orm_model.id),
            title=orm_model.title,
            body=orm_model.body,
            created_at=orm_model.created_at,
            updated_at=orm_model.updated_at,
        )

    def to_orm(self, domain_entity: Note, orm_model: NoteModel | None = None) -> NoteModel:
        if orm_model is None:
            orm_model = NoteModel(id=orm_id(domain_entity.id))
        orm_model.title = domain_entity.title
        orm_model.body = domain_entity.body
        return orm_model
