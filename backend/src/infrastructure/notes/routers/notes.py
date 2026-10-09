"""API routes for notes.

Routers convert between Pydantic schemas and what the use cases take and
return (primitives in, domain entities or view DTOs out). They hold no logic.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status

from src.application.notes.commands.create_note_use_case import CreateNoteUseCase
from src.application.notes.commands.delete_note_use_case import DeleteNoteUseCase
from src.application.notes.commands.update_note_use_case import UpdateNoteUseCase
from src.application.notes.queries.get_note_use_case import GetNoteUseCase
from src.application.notes.queries.list_notes_use_case import ListNotesUseCase
from src.containers import container
from src.domain.notes.entities.note import Note as NoteEntity
from src.infrastructure.common.di import inject_use_case
from src.infrastructure.common.schemas import CollectionResponse
from src.infrastructure.notes.schemas import Note, NoteListItem, NoteRequest

router = APIRouter(prefix="/notes", tags=["notes"])


def note_to_schema(note: NoteEntity) -> Note:
    """Convert a Note aggregate to its response schema."""
    return Note(
        id=note.id.value,
        title=note.title,
        body=note.body,
        created_at=note.created_at,
        updated_at=note.updated_at,
    )


@router.get("", response_model=CollectionResponse[NoteListItem])
async def list_notes(
    search: Annotated[str | None, Query(max_length=200)] = None,
    use_case: ListNotesUseCase = Depends(inject_use_case(container.notes.list_notes_use_case)),
) -> CollectionResponse[NoteListItem]:
    views = await use_case.list_notes(search=search)
    return CollectionResponse(
        items=[
            NoteListItem(
                id=view.id,
                title=view.title,
                body_preview=view.body_preview,
                updated_at=view.updated_at,
            )
            for view in views
        ]
    )


@router.post("", response_model=Note, status_code=status.HTTP_201_CREATED)
async def create_note(
    request: NoteRequest,
    use_case: CreateNoteUseCase = Depends(inject_use_case(container.notes.create_note_use_case)),
) -> Note:
    note = await use_case.create_note(title=request.title, body=request.body)
    return note_to_schema(note)


@router.get("/{note_id}", response_model=Note)
async def get_note(
    note_id: int,
    use_case: GetNoteUseCase = Depends(inject_use_case(container.notes.get_note_use_case)),
) -> Note:
    return note_to_schema(await use_case.get_note(note_id))


@router.put("/{note_id}", response_model=Note)
async def update_note(
    note_id: int,
    request: NoteRequest,
    use_case: UpdateNoteUseCase = Depends(inject_use_case(container.notes.update_note_use_case)),
) -> Note:
    note = await use_case.update_note(note_id=note_id, title=request.title, body=request.body)
    return note_to_schema(note)


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note(
    note_id: int,
    use_case: DeleteNoteUseCase = Depends(inject_use_case(container.notes.delete_note_use_case)),
) -> None:
    await use_case.delete_note(note_id)
