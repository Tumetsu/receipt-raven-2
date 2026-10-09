"""
Custom exceptions for the beancount service

This module defines a hierarchy of exceptions that provide better error handling
and more specific error information than generic Python exceptions.
"""
from typing import List, Optional, Dict, Any


class BeancountServiceError(Exception):
    """
    Base exception for all beancount service errors.

    All custom exceptions should inherit from this class.
    """

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        """
        Initialize the exception.

        Args:
            message: Human-readable error message
            details: Optional dictionary with additional error context
        """
        super().__init__(message)
        self.message = message
        self.details = details or {}


class LedgerNotFoundError(BeancountServiceError):
    """
    Raised when the ledger file cannot be found.

    This typically indicates a configuration issue or missing ledger file.
    """

    def __init__(self, ledger_path: str):
        super().__init__(
            message=f"Ledger file not found: {ledger_path}",
            details={"ledger_path": ledger_path}
        )
        self.ledger_path = ledger_path


class LedgerParseError(BeancountServiceError):
    """
    Raised when the ledger file cannot be parsed.

    This indicates syntax errors or invalid beancount format in the ledger.
    """

    def __init__(self, ledger_path: str, parse_errors: List[str]):
        error_summary = f"{len(parse_errors)} parse error(s) in ledger"
        super().__init__(
            message=f"Failed to parse ledger: {error_summary}",
            details={
                "ledger_path": ledger_path,
                "error_count": len(parse_errors),
                "errors": parse_errors[:5]  # Limit to first 5 errors
            }
        )
        self.ledger_path = ledger_path
        self.parse_errors = parse_errors


class TransactionValidationError(BeancountServiceError):
    """
    Raised when a transaction fails validation.

    This includes issues like unbalanced transactions, invalid dates, etc.
    """

    def __init__(
        self,
        message: str,
        transaction_data: Optional[Dict[str, Any]] = None,
        validation_errors: Optional[List[str]] = None
    ):
        details = {}
        if transaction_data:
            details["transaction"] = transaction_data
        if validation_errors:
            details["validation_errors"] = validation_errors

        super().__init__(message=message, details=details)
        self.validation_errors = validation_errors or []


class AccountNotFoundError(BeancountServiceError):
    """
    Raised when referenced accounts do not exist in the ledger.

    This typically happens when trying to use an account that hasn't been
    opened with an 'open' directive in the ledger.
    """

    def __init__(self, accounts: List[str], ledger_path: Optional[str] = None):
        account_list = ", ".join(accounts)
        super().__init__(
            message=f"Account(s) not found in ledger: {account_list}",
            details={
                "accounts": accounts,
                "ledger_path": ledger_path
            }
        )
        self.accounts = accounts
        self.ledger_path = ledger_path


class RepositoryError(BeancountServiceError):
    """
    Raised when a repository operation fails.

    This includes file I/O errors, cache errors, etc.
    """

    def __init__(self, operation: str, message: str, original_error: Optional[Exception] = None):
        details = {"operation": operation}
        if original_error:
            details["original_error"] = str(original_error)
            details["error_type"] = type(original_error).__name__

        super().__init__(
            message=f"Repository operation '{operation}' failed: {message}",
            details=details
        )
        self.operation = operation
        self.original_error = original_error
