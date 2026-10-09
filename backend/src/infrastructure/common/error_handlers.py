"""Translate domain exceptions into HTTP responses."""

import structlog
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from src.domain.common.exceptions import (
    AuthenticationError,
    AuthorizationError,
    BusinessRuleViolationError,
    ConflictError,
    DomainError,
    EntityNotFoundError,
    ExternalServiceError,
    ValidationError,
)

logger = structlog.get_logger(__name__)

# First match wins, so subclasses go before their bases.
DOMAIN_ERROR_STATUS_MAP: list[tuple[type[DomainError], int, str]] = [
    (EntityNotFoundError, 404, "not_found"),
    (ValidationError, 400, "bad_request"),
    (ConflictError, 409, "conflict"),
    (AuthenticationError, 401, "authentication_error"),
    (AuthorizationError, 403, "authorization_error"),
    (BusinessRuleViolationError, 400, "bad_request"),
    (ExternalServiceError, 502, "bad_gateway"),
]

# Generic messages: a domain error's own message can name internals, so it goes
# to the log, never to the client, unless its type is listed below.
SAFE_MESSAGES: dict[int, str] = {
    400: "The request could not be processed.",
    401: "Authentication failed.",
    403: "You do not have permission to perform this action.",
    404: "The requested resource was not found.",
    409: "The resource already exists or conflicts with current state.",
    502: "A service the app depends on failed.",
    500: "An unexpected error occurred.",
}

# Domain errors whose message is written for the end user and safe to return.
# This app's business-rule, conflict and ledger messages tell the user what to fix.
PUBLIC_MESSAGE_ERRORS: tuple[type[DomainError], ...] = (
    ValidationError,
    BusinessRuleViolationError,
    ConflictError,
    ExternalServiceError,
)

SERVER_ERROR = 500


async def domain_error_handler(_request: Request, exc: Exception) -> JSONResponse:
    """Map a domain exception to a status code and a safe message."""
    assert isinstance(exc, DomainError)  # noqa: S101 - registered for DomainError only
    status_code, error_key = SERVER_ERROR, "internal_error"
    for exc_type, code, key in DOMAIN_ERROR_STATUS_MAP:
        if isinstance(exc, exc_type):
            status_code, error_key = code, key
            break

    log = logger.error if status_code == SERVER_ERROR else logger.warning
    log("domain_error", error_type=type(exc).__name__, status_code=status_code, detail=exc.message)

    message = exc.message if isinstance(exc, PUBLIC_MESSAGE_ERRORS) else SAFE_MESSAGES[status_code]
    headers = {"WWW-Authenticate": "Bearer"} if isinstance(exc, AuthenticationError) else None
    return JSONResponse(
        status_code=status_code,
        content={"error": error_key, "message": message},
        headers=headers,
    )


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Catch-all for unexpected exceptions: log them, return a generic 500."""
    logger.error(
        "unhandled_exception",
        exception_type=type(exc).__name__,
        path=request.url.path,
        exc_info=exc,
    )
    return JSONResponse(
        status_code=SERVER_ERROR,
        content={"error": "internal_error", "message": SAFE_MESSAGES[SERVER_ERROR]},
    )


def register_error_handlers(app: FastAPI) -> None:
    """Install the domain and catch-all exception handlers."""
    app.add_exception_handler(DomainError, domain_error_handler)
    app.add_exception_handler(Exception, unhandled_exception_handler)
