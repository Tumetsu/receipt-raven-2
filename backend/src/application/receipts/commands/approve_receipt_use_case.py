"""Use case for approving a receipt: save the user's corrections, then book it."""

import structlog

from src.application.ledger.protocols.ledger_service import LedgerServiceProtocol
from src.application.receipts.commands.receipt_fields import ReceiptFields
from src.application.receipts.protocols.receipt_repository import ReceiptRepositoryProtocol
from src.domain.common.value_objects import ReceiptId
from src.domain.ledger.receipt_transaction import ReceiptPosting, ReceiptTransaction
from src.domain.receipts.entities.receipt import Receipt
from src.domain.receipts.exceptions import ReceiptNotApprovableError, ReceiptNotFoundError

logger = structlog.get_logger(__name__)

# Currencies the ledger can take. The ledger's accounts are opened for EUR
# only, and how foreign-currency receipts should be booked is not decided
# yet, so other currencies are recorded but wait unapproved.
BOOKABLE_CURRENCIES = frozenset({"EUR"})


def _to_transaction(receipt: Receipt) -> ReceiptTransaction:
    return ReceiptTransaction.from_items(
        receipt_id=receipt.id.value,
        payee=receipt.payee,
        description=receipt.description,
        receipt_date=receipt.receipt_date,
        source_account=receipt.source_account or "",
        total=receipt.total_sum,
        currency=receipt.currency,
        items=[
            ReceiptPosting(name=item.name, expense_account=item.expense_account, price=item.price)
            for item in receipt.items
        ],
    )


class ApproveReceiptUseCase:
    """Apply the user's edits and write the receipt to the ledger.

    The edits are saved before the ledger is called, so a rejected receipt
    keeps them and the user can fix the problem and approve again.
    """

    def __init__(
        self,
        receipt_repository: ReceiptRepositoryProtocol,
        ledger_service: LedgerServiceProtocol,
    ) -> None:
        self.receipt_repository = receipt_repository
        self.ledger_service = ledger_service

    async def approve_receipt(self, receipt_id: int, fields: ReceiptFields) -> Receipt:
        """Update and approve the receipt.

        Raises:
            ReceiptNotFoundError: If there is no such receipt.
            ReceiptAlreadyApprovedError: If it was approved before.
            ReceiptNotApprovableError: If the edited receipt breaks an approval rule,
                or is in a currency the ledger does not take yet.
            ExternalServiceError: If the ledger is down or rejects the receipt.
        """
        receipt = await self.receipt_repository.find_by_id(ReceiptId(receipt_id))
        if receipt is None:
            raise ReceiptNotFoundError(receipt_id)

        receipt.update_details(
            payee=fields.payee,
            receipt_date=fields.receipt_date,
            total_sum=fields.total_sum,
            description=fields.description,
            source_account=fields.source_account,
            currency=fields.currency,
        )
        receipt.replace_items(fields.lines)
        receipt = await self.receipt_repository.save(receipt)
        receipt.ensure_approvable()
        if receipt.currency not in BOOKABLE_CURRENCIES:
            raise ReceiptNotApprovableError(
                f"Receipts in {receipt.currency} cannot be booked to the ledger yet. "
                "Leave it unapproved for now."
            )

        await self.ledger_service.submit_receipt(_to_transaction(receipt))

        receipt.approve()
        receipt = await self.receipt_repository.save(receipt)
        logger.info("receipt_approved", receipt_id=receipt_id)
        return receipt
