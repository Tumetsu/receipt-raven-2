"""
Beancount Ledger Service
FastAPI application that provides REST API access to beancount ledger
"""
from typing import Optional
from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from dependencies import get_ledger_repository
from repositories import ILedgerRepository
from models import (
    AccountsResponse,
    PayeesResponse,
    Transaction,
    ReceiptTransactionData,
    TransactionSubmitResponse,
    MonthlyExpensesResponse,
)
from services.accounts import get_accounts
from services.payees import get_payees
from services.transactions import (
    submit_transaction,
    submit_receipt_transaction,
)
from services.monthly_expenses import get_current_month_expenses
from utils.logging import setup_logging, get_logger
from middleware.error_handler import register_exception_handlers

# Load settings (validates configuration on startup)
settings = get_settings()

# Configure logging
setup_logging(settings.log_level)
logger = get_logger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Beancount Ledger Service",
    description="REST API for beancount ledger operations",
    version="1.0.0",
)

# Register exception handlers
register_exception_handlers(app)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins if settings.allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health_check(
    repository: ILedgerRepository = Depends(get_ledger_repository)
):
    """
    Health check endpoint
    """
    # Check if ledger file exists
    if not repository.ledger_exists():
        raise HTTPException(status_code=503, detail="Ledger file not found")

    return {"status": "ok"}


@app.get("/accounts", response_model=AccountsResponse)
async def get_accounts_endpoint(
    type: Optional[str] = Query(None, description="Filter by account type"),
    repository: ILedgerRepository = Depends(get_ledger_repository)
):
    """
    Get all accounts from the ledger

    Args:
        type: Optional filter by account type (e.g., "Expenses", "Assets")

    Returns:
        List of accounts
    """
    logger.debug("fetching_accounts", account_type_filter=type)
    accounts = get_accounts(repository, type)
    logger.info("accounts_fetched", count=len(accounts), account_type_filter=type)
    return AccountsResponse(accounts=accounts)


@app.get("/payees", response_model=PayeesResponse)
async def get_payees_endpoint(
    repository: ILedgerRepository = Depends(get_ledger_repository)
):
    """
    Get list of payees (shops, vendors) from the ledger

    Returns:
        List of payees
    """
    logger.debug("fetching_payees")
    payees = get_payees(repository)
    logger.info("payees_fetched", count=len(payees))
    return PayeesResponse(payees=payees)


@app.get("/monthly-expenses", response_model=MonthlyExpensesResponse)
async def get_monthly_expenses_endpoint(
    repository: ILedgerRepository = Depends(get_ledger_repository)
):
    """
    Get total expenses for the current month

    Returns:
        Total expenses by currency for the ongoing month
    """
    from datetime import datetime
    now = datetime.now()
    logger.debug("fetching_monthly_expenses", year=now.year, month=now.month)
    expenses = get_current_month_expenses(repository)
    logger.info("monthly_expenses_fetched", expenses=expenses, year=now.year, month=now.month)
    return MonthlyExpensesResponse(
        expenses_by_currency=expenses,
        year=now.year,
        month=now.month
    )


@app.post("/transactions", response_model=TransactionSubmitResponse)
async def submit_transaction_endpoint(
    transaction: Transaction,
    dry_run: bool = Query(False),
    repository: ILedgerRepository = Depends(get_ledger_repository)
):
    """
    Submit a transaction to the ledger

    Args:
        transaction: Transaction data
        dry_run: If True, only validate without writing to ledger

    Returns:
        Success status and transaction ID
    """
    logger.info("submitting_transaction", payee=transaction.payee, dry_run=dry_run, date=transaction.date)
    result = submit_transaction(transaction, repository, dry_run)
    logger.info("transaction_submitted", transaction_id=result.transaction_id, payee=transaction.payee, dry_run=dry_run)
    return result


@app.post("/transactions/receipt", response_model=TransactionSubmitResponse)
async def submit_receipt_transaction_endpoint(
    receipt_data: ReceiptTransactionData,
    dry_run: bool = Query(False),
    repository: ILedgerRepository = Depends(get_ledger_repository)
):
    """
    Convert receipt data to transaction and submit to ledger

    Args:
        receipt_data: Receipt transaction data
        dry_run: If True, only validate without writing to ledger

    Returns:
        Success status and transaction ID
    """
    logger.info("submitting_receipt_transaction", receipt_id=receipt_data.receipt_id, payee=receipt_data.payee, dry_run=dry_run)
    result = submit_receipt_transaction(receipt_data, repository, dry_run)
    logger.info("receipt_transaction_submitted", receipt_id=receipt_data.receipt_id, transaction_id=result.transaction_id, dry_run=dry_run)
    return result


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port)
