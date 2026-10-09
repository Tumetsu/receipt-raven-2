from dependency_injector import containers, providers

from src.config import get_settings
from src.containers.notes import NotesContainer
from src.containers.shared import SharedContainer
from src.database import current_db_session


class RootContainer(containers.DeclarativeContainer):
    """Root DI container composing the module sub-containers."""

    # Resolved per call from the context-bound session rather than overridden on
    # this process-wide container: an override is visible to every concurrent
    # request, so two in flight at once could resolve each other's session.
    db = providers.Callable(current_db_session)

    settings = providers.Object(get_settings())

    shared = providers.Container(SharedContainer, db=db, settings=settings)

    notes = providers.Container(
        NotesContainer,
        note_repository=shared.note_repository,
        note_list_query=shared.note_list_query,
    )
