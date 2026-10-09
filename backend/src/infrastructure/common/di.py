"""Bridge between FastAPI dependencies and the dependency-injector container."""

from collections.abc import Awaitable, Callable

from dependency_injector.providers import Provider

from src.database import DatabaseSession, bind_db_session


def inject_use_case[T](provider: Provider[T]) -> Callable[[DatabaseSession], Awaitable[T]]:
    """
    Create a FastAPI dependency for a container provider.

    Binds the request-scoped database session while the use case is built,
    which is when the container reads it. Async so it runs in the request's own
    task, whose context no other request can see.
    """

    async def dependency(db: DatabaseSession) -> T:
        with bind_db_session(db):
            return provider()

    return dependency
