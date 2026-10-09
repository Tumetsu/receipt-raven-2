"""
Service for creating and submitting transactions to beancount ledger
"""
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from beancount.core import data, amount
from beancount.parser import printer
from beancount.core.getters import get_accounts
from models import Transaction, ReceiptTransactionData, TransactionSubmitResponse
from repositories import ILedgerRepository
from exceptions import TransactionValidationError, AccountNotFoundError


def create_beancount_transaction(txn: Transaction) -> data.Transaction:
    """
    Create a beancount Transaction object from our Transaction model

    Args:
        txn: Transaction model

    Returns:
        beancount Transaction object

    Raises:
        ValueError: If transaction data is invalid
    """
    # Parse the date
    date_parts = txn.date.split("-")
    txn_date = datetime(
        int(date_parts[0]), int(date_parts[1]), int(date_parts[2])
    ).date()

    # Create postings
    postings = []
    for posting in txn.postings:
        currency = posting.currency or "EUR"
        amt = amount.Amount(Decimal(str(posting.amount)), currency)

        # Create metadata for posting if there's a comment
        posting_meta = {}
        if posting.comment:
            posting_meta["comment"] = posting.comment

        bean_posting = data.Posting(
            account=posting.account,
            units=amt,
            cost=None,
            price=None,
            flag=None,
            meta=posting_meta if posting_meta else None,
        )
        postings.append(bean_posting)

    # Create tags and links
    tags = set(txn.tags) if txn.tags else set()
    links = set(txn.links) if txn.links else set()

    # Create metadata
    meta = {}
    if txn.metadata:
        meta.update(txn.metadata)

    # Create the transaction
    bean_txn = data.Transaction(
        meta=meta,
        date=txn_date,
        flag="*",
        payee=txn.payee,
        narration=txn.narration,
        tags=tags,
        links=links,
        postings=postings,
    )

    return bean_txn


def validate_transaction(bean_txn: data.Transaction) -> None:
    """
    Validate that a transaction balances correctly

    Args:
        bean_txn: beancount Transaction object

    Raises:
        TransactionValidationError: If the transaction doesn't balance
    """
    # Group postings by currency
    currency_totals = {}

    for posting in bean_txn.postings:
        if posting.units is None:
            # Empty posting - beancount will auto-balance this
            continue

        currency = posting.units.currency
        if currency not in currency_totals:
            currency_totals[currency] = Decimal("0")

        currency_totals[currency] += posting.units.number

    # Check that each currency balances (sums to zero)
    # Allow a small tolerance for rounding errors
    tolerance = Decimal("0.005")

    validation_errors = []
    for currency, total in currency_totals.items():
        if abs(total) > tolerance:
            validation_errors.append(
                f"Transaction does not balance for {currency}: sum is {total} (should be 0)"
            )

    if validation_errors:
        raise TransactionValidationError(
            message="Transaction does not balance",
            transaction_data={
                "payee": bean_txn.payee,
                "date": str(bean_txn.date),
                "narration": bean_txn.narration
            },
            validation_errors=validation_errors
        )


def validate_accounts_exist(
    bean_txn: data.Transaction, repository: ILedgerRepository
) -> None:
    """
    Validate that all accounts referenced in the transaction exist in the ledger

    Args:
        bean_txn: beancount Transaction object
        repository: Ledger repository instance

    Raises:
        AccountNotFoundError: If any accounts don't exist in the ledger
    """
    # Load the ledger to get all defined accounts
    entries, errors, options = repository.load_entries()

    # Get all account names that have been opened in the ledger
    valid_accounts = get_accounts(entries)

    # Check each posting's account
    invalid_accounts = []
    for posting in bean_txn.postings:
        if posting.account not in valid_accounts:
            invalid_accounts.append(posting.account)

    if invalid_accounts:
        raise AccountNotFoundError(accounts=invalid_accounts)


def create_receipt_transaction(receipt_data: ReceiptTransactionData) -> Transaction:
    """
    Convert receipt data into a beancount transaction

    Args:
        receipt_data: Receipt transaction data

    Returns:
        Transaction object
    """
    currency = receipt_data.currency or "EUR"
    postings = []

    # Create postings for each item
    for item in receipt_data.items:
        # Determine expense account
        postings.append(
            {
                "account": item.expense_account,
                "amount": item.price,
                "currency": currency,
                "comment": item.name,
            }
        )

    # Add the source account posting (negative, as money is leaving)
    postings.append(
        {
            "account": receipt_data.source_account,
            "amount": -receipt_data.total,
            "currency": currency,
        }
    )

    # Create transaction
    transaction = Transaction(
        date=receipt_data.date,
        payee=receipt_data.payee,
        narration=f"#{receipt_data.receipt_id} {receipt_data.description or 'Receipt'}",
        postings=postings,
        tags=["receipt-raven"],
        metadata={"receipt_id": str(receipt_data.receipt_id)},
    )

    return transaction


def submit_transaction(
    transaction: Transaction, repository: ILedgerRepository, dry_run: bool = False
) -> TransactionSubmitResponse:
    """
    Submit a transaction to the beancount ledger

    Args:
        transaction: Transaction to submit
        repository: Ledger repository instance
        dry_run: If True, only validate without writing

    Returns:
        TransactionSubmitResponse with success status

    Raises:
        TransactionValidationError: If the transaction doesn't balance
        AccountNotFoundError: If referenced accounts don't exist
        RepositoryError: If there's an error writing to the ledger
    """
    # Create beancount transaction object
    bean_txn = create_beancount_transaction(transaction)

    # Validate that the transaction balances (raises TransactionValidationError if not)
    validate_transaction(bean_txn)

    # Validate that all accounts exist in the ledger (raises AccountNotFoundError if not)
    validate_accounts_exist(bean_txn, repository)

    # Format using beancount's printer for proper formatting
    formatted_txn = printer.format_entry(bean_txn)

    if dry_run:
        # Just return the formatted transaction for validation
        return TransactionSubmitResponse(
            success=True,
            message="Dry run - transaction validated and balances correctly",
            transaction_id=None,
        )

    # Append to ledger file via repository (raises RepositoryError if it fails)
    repository.append_transaction(formatted_txn)

    # Generate transaction ID (using date + payee as identifier)
    transaction_id = f"{transaction.date}_{transaction.payee}"

    return TransactionSubmitResponse(
        success=True,
        message="Transaction submitted successfully",
        transaction_id=transaction_id,
    )


def submit_receipt_transaction(
    receipt_data: ReceiptTransactionData, repository: ILedgerRepository, dry_run: bool = False
) -> TransactionSubmitResponse:
    """
    Convert receipt data to transaction and submit to ledger

    Args:
        receipt_data: Receipt transaction data
        repository: Ledger repository instance
        dry_run: If True, only validate without writing

    Returns:
        TransactionSubmitResponse with success status

    Raises:
        TransactionValidationError: If the transaction doesn't balance
        AccountNotFoundError: If referenced accounts don't exist
        RepositoryError: If there's an error writing to the ledger
    """
    # Create transaction from receipt data
    transaction = create_receipt_transaction(receipt_data)

    # Submit the transaction (exceptions will propagate)
    return submit_transaction(transaction, repository, dry_run)
