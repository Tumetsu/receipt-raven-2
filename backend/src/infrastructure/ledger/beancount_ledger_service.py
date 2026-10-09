"""Ledger adapter for the beancount service (`beancount-service/` in this repository).

Speaks the service's REST API: `GET /accounts`, `GET /payees` and
`POST /transactions/receipt`.
"""

from typing import Any

import httpx
import structlog

from src.domain.ledger.account import AccountType, LedgerAccount
from src.domain.ledger.exceptions import LedgerRejectedTransactionError, LedgerUnavailableError
from src.domain.ledger.receipt_transaction import ReceiptTransaction

logger = structlog.get_logger(__name__)

HTTP_CLIENT_ERROR = 400
HTTP_SERVER_ERROR = 500


def _error_reason(response: httpx.Response) -> str:
    """The service answers `{"message": ...}`, FastAPI itself `{"detail": ...}`."""
    try:
        body: Any = response.json()
    except ValueError:
        return response.text or f"HTTP {response.status_code}"
    if isinstance(body, dict):
        for key in ("message", "detail", "error"):
            value = body.get(key)
            if isinstance(value, str) and value:
                return value
            if value:
                return str(value)
    return f"HTTP {response.status_code}"


def receipt_transaction_payload(transaction: ReceiptTransaction) -> dict[str, Any]:
    """The service's `ReceiptTransactionData` model."""
    return {
        "receipt_id": transaction.receipt_id,
        "description": transaction.description,
        "payee": transaction.payee,
        "source_account": transaction.source_account,
        "date": transaction.receipt_date.isoformat(),
        "total": transaction.total,
        "currency": transaction.currency,
        "items": [
            {
                "name": posting.name,
                "price": posting.price,
                "expense_account": posting.expense_account,
            }
            for posting in transaction.postings
        ],
    }


class BeancountLedgerService:
    """HTTP client of the beancount service."""

    def __init__(
        self,
        base_url: str,
        timeout_seconds: float,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout_seconds
        self.transport = transport

    async def _request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, str] | None = None,
        json: dict[str, object] | None = None,
    ) -> httpx.Response:
        try:
            async with httpx.AsyncClient(
                base_url=self.base_url, timeout=self.timeout, transport=self.transport
            ) as client:
                response = await client.request(method, path, params=params, json=json)
        except httpx.HTTPError as exc:
            logger.error("ledger_unreachable", url=self.base_url + path, error=str(exc))
            raise LedgerUnavailableError(str(exc)) from exc
        if response.status_code >= HTTP_SERVER_ERROR:
            reason = _error_reason(response)
            logger.error("ledger_error", path=path, status=response.status_code, reason=reason)
            raise LedgerUnavailableError(reason)
        return response

    async def _get_json(self, path: str, params: dict[str, str] | None = None) -> dict[str, Any]:
        response = await self._request("GET", path, params=params)
        if response.status_code >= HTTP_CLIENT_ERROR:
            raise LedgerUnavailableError(_error_reason(response))
        return response.json()

    async def list_accounts(self, account_type: AccountType | None = None) -> list[LedgerAccount]:
        params = {"type": account_type.value} if account_type else None
        body = await self._get_json("/accounts", params)
        accounts: list[LedgerAccount] = []
        for account in body.get("accounts", []):
            try:
                accounts.append(
                    LedgerAccount(name=str(account["name"]), type=AccountType(account["type"]))
                )
            except (KeyError, ValueError):
                logger.warning("ledger_account_skipped", account=account)
        return accounts

    async def list_payees(self) -> list[str]:
        body = await self._get_json("/payees")
        return [str(payee["name"]) for payee in body.get("payees", []) if payee.get("name")]

    async def submit_receipt(self, transaction: ReceiptTransaction) -> None:
        response = await self._request(
            "POST", "/transactions/receipt", json=receipt_transaction_payload(transaction)
        )
        if response.status_code >= HTTP_CLIENT_ERROR:
            raise LedgerRejectedTransactionError(_error_reason(response))
        body: Any = response.json()
        if not body.get("success", False):
            raise LedgerRejectedTransactionError(
                str(body.get("message") or "the service did not accept it")
            )
        logger.info(
            "ledger_receipt_submitted",
            receipt_id=transaction.receipt_id,
            transaction_id=body.get("transaction_id"),
        )
