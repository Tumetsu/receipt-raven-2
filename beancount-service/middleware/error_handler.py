"""
Error handler middleware for FastAPI

This module provides centralized exception handling for all custom exceptions,
converting them to appropriate HTTP responses with structured error information.
"""
from typing import Dict, Any
from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from exceptions import (
    BeancountServiceError,
    LedgerNotFoundError,
    LedgerParseError,
    TransactionValidationError,
    AccountNotFoundError,
    RepositoryError,
)
from utils.logging import get_logger

logger = get_logger(__name__)


class ErrorResponse(BaseModel):
    """Standard error response model"""
    error: str
    message: str
    details: Dict[str, Any] = {}
    code: str


async def ledger_not_found_handler(
    request: Request, exc: LedgerNotFoundError
) -> JSONResponse:
    """
    Handle LedgerNotFoundError exceptions.

    Returns 503 Service Unavailable since the ledger is required for operation.
    """
    logger.error(
        "ledger_not_found",
        ledger_path=exc.ledger_path,
        path=request.url.path,
        method=request.method
    )

    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "error": "Ledger Not Found",
            "message": exc.message,
            "details": exc.details,
            "code": "LEDGER_NOT_FOUND"
        }
    )


async def ledger_parse_error_handler(
    request: Request, exc: LedgerParseError
) -> JSONResponse:
    """
    Handle LedgerParseError exceptions.

    Returns 500 Internal Server Error since the ledger has syntax errors.
    """
    logger.error(
        "ledger_parse_error",
        ledger_path=exc.ledger_path,
        error_count=len(exc.parse_errors),
        path=request.url.path,
        method=request.method
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Ledger Parse Error",
            "message": exc.message,
            "details": exc.details,
            "code": "LEDGER_PARSE_ERROR"
        }
    )


async def transaction_validation_error_handler(
    request: Request, exc: TransactionValidationError
) -> JSONResponse:
    """
    Handle TransactionValidationError exceptions.

    Returns 400 Bad Request since the transaction data is invalid.
    """
    logger.warning(
        "transaction_validation_error",
        message=exc.message,
        validation_errors=exc.validation_errors,
        path=request.url.path,
        method=request.method
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Transaction Validation Error",
            "message": exc.message,
            "details": exc.details,
            "code": "TRANSACTION_VALIDATION_ERROR"
        }
    )


async def account_not_found_error_handler(
    request: Request, exc: AccountNotFoundError
) -> JSONResponse:
    """
    Handle AccountNotFoundError exceptions.

    Returns 400 Bad Request since the referenced accounts don't exist.
    """
    logger.warning(
        "account_not_found_error",
        accounts=exc.accounts,
        path=request.url.path,
        method=request.method
    )

    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": "Account Not Found",
            "message": exc.message,
            "details": exc.details,
            "code": "ACCOUNT_NOT_FOUND"
        }
    )


async def repository_error_handler(
    request: Request, exc: RepositoryError
) -> JSONResponse:
    """
    Handle RepositoryError exceptions.

    Returns 500 Internal Server Error for repository failures.
    """
    logger.error(
        "repository_error",
        operation=exc.operation,
        message=exc.message,
        original_error=str(exc.original_error) if exc.original_error else None,
        path=request.url.path,
        method=request.method
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Repository Error",
            "message": exc.message,
            "details": exc.details,
            "code": "REPOSITORY_ERROR"
        }
    )


async def generic_beancount_service_error_handler(
    request: Request, exc: BeancountServiceError
) -> JSONResponse:
    """
    Handle generic BeancountServiceError exceptions.

    This is a catch-all for any BeancountServiceError subclasses
    that don't have their own specific handler.
    """
    logger.error(
        "beancount_service_error",
        error_type=type(exc).__name__,
        message=exc.message,
        details=exc.details,
        path=request.url.path,
        method=request.method
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Service Error",
            "message": exc.message,
            "details": exc.details,
            "code": "SERVICE_ERROR"
        }
    )


def register_exception_handlers(app: FastAPI) -> None:
    """
    Register all custom exception handlers with the FastAPI application.

    This should be called during application startup, after the app is created.

    Args:
        app: FastAPI application instance
    """
    # Register specific exception handlers
    app.add_exception_handler(LedgerNotFoundError, ledger_not_found_handler)
    app.add_exception_handler(LedgerParseError, ledger_parse_error_handler)
    app.add_exception_handler(
        TransactionValidationError, transaction_validation_error_handler
    )
    app.add_exception_handler(AccountNotFoundError, account_not_found_error_handler)
    app.add_exception_handler(RepositoryError, repository_error_handler)

    # Register generic handler as fallback
    app.add_exception_handler(
        BeancountServiceError, generic_beancount_service_error_handler
    )

    # Logging is done after app startup in main.py to avoid initialization issues
    # logger.info("exception_handlers_registered", handler_count=6)
