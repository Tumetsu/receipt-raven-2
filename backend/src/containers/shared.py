from dependency_injector import containers, providers

from src.infrastructure.notes.queries.note_list_query import NoteListQuery
from src.infrastructure.notes.repositories.note_repository import NoteRepository


class SharedContainer(containers.DeclarativeContainer):
    """Infrastructure adapters (repositories, query adapters, services).

    Adapters live here rather than in their module's container so that any
    module's use cases can be given any adapter they need.
    """

    db = providers.Dependency()
    settings = providers.Dependency()

    # Repositories
    note_repository = providers.Factory(NoteRepository, db=db)

    # Query adapters (read models)
    note_list_query = providers.Factory(NoteListQuery, db=db)
