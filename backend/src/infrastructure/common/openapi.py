"""OpenAPI operation id generation."""

from fastapi.routing import APIRoute


def operation_id(route: APIRoute) -> str:
    """
    Use the route handler's own name as its OpenAPI operationId.

    FastAPI's default appends the path and method to the handler name, so
    `list_notes` becomes `list_notes_api_v1_notes_get`, and orval carries that
    into hook names such as `useListNotesApiV1NotesGet`. The handler name alone
    already says what the operation is.

    This makes handler names an API-visible contract: two handlers sharing a
    name would collide into one operationId and silently drop an operation from
    the generated client. `tests/test_openapi.py` asserts they stay unique.
    """
    return route.name
