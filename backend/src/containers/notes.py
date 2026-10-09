from dependency_injector import containers, providers

from src.application.notes.commands.create_note_use_case import CreateNoteUseCase
from src.application.notes.commands.delete_note_use_case import DeleteNoteUseCase
from src.application.notes.commands.update_note_use_case import UpdateNoteUseCase
from src.application.notes.queries.get_note_use_case import GetNoteUseCase
from src.application.notes.queries.list_notes_use_case import ListNotesUseCase


class NotesContainer(containers.DeclarativeContainer):
    """Notes module use cases."""

    # Dependencies from the shared container
    note_repository = providers.Dependency()
    note_list_query = providers.Dependency()

    create_note_use_case = providers.Factory(CreateNoteUseCase, note_repository=note_repository)
    update_note_use_case = providers.Factory(UpdateNoteUseCase, note_repository=note_repository)
    delete_note_use_case = providers.Factory(DeleteNoteUseCase, note_repository=note_repository)
    get_note_use_case = providers.Factory(GetNoteUseCase, note_repository=note_repository)
    list_notes_use_case = providers.Factory(ListNotesUseCase, note_list_query=note_list_query)
