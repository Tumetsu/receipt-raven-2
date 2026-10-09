"""The beancount service adapter against a scripted HTTP transport.

These pin the wire format of `beancount-service/` (models.py): paths, query
parameters, the receipt payload and both error body shapes.
"""

import json
from datetime import date

import httpx
import pytest

from src.domain.ledger.account import AccountType, LedgerAccount
from src.domain.ledger.exceptions import LedgerRejectedTransactionError, LedgerUnavailableError
from src.domain.ledger.receipt_transaction import ReceiptPosting, ReceiptTransaction
from src.infrastructure.ledger.beancount_ledger_service import BeancountLedgerService

TRANSACTION = ReceiptTransaction(
    receipt_id=42,
    payee="Prisma",
    description=None,
    receipt_date=date(2026, 10, 9),
    source_account="Assets:Checking",
    total=1500,
    currency="JPY",
    postings=(ReceiptPosting("Coffee, Onigiri", "Expenses:Groceries", 1500),),
)


def service(handler: object) -> tuple[BeancountLedgerService, list[httpx.Request]]:
    requests: list[httpx.Request] = []

    def record(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return handler(request)  # type: ignore[operator]

    return BeancountLedgerService(
        "http://beancount:8000/", 5, transport=httpx.MockTransport(record)
    ), requests


async def test_lists_accounts_by_type() -> None:
    ledger, requests = service(
        lambda _: httpx.Response(
            200,
            json={
                "accounts": [
                    {"name": "Expenses:Food", "type": "Expenses", "display_name": None},
                    {"name": "Weird", "type": "Unknown"},
                ]
            },
        )
    )

    accounts = await ledger.list_accounts(AccountType.EXPENSES)

    assert accounts == [LedgerAccount("Expenses:Food", AccountType.EXPENSES)]
    assert str(requests[0].url) == "http://beancount:8000/accounts?type=Expenses"


async def test_lists_payees() -> None:
    ledger, _ = service(
        lambda _: httpx.Response(200, json={"payees": [{"name": "Alko"}, {"name": "Prisma"}]})
    )

    assert await ledger.list_payees() == ["Alko", "Prisma"]


async def test_submits_the_receipt_transaction_payload() -> None:
    ledger, requests = service(
        lambda _: httpx.Response(200, json={"success": True, "transaction_id": "abc"})
    )

    await ledger.submit_receipt(TRANSACTION)

    assert requests[0].url.path == "/transactions/receipt"
    assert json.loads(requests[0].content) == {
        "receipt_id": 42,
        "description": None,
        "payee": "Prisma",
        "source_account": "Assets:Checking",
        "date": "2026-10-09",
        "total": 1500,
        "currency": "JPY",
        "items": [
            {"name": "Coffee, Onigiri", "price": 1500, "expense_account": "Expenses:Groceries"}
        ],
    }


@pytest.mark.parametrize(
    ("response", "reason"),
    [
        (
            httpx.Response(400, json={"error": "Account Not Found", "message": "No such account"}),
            "No such account",
        ),
        (httpx.Response(422, json={"detail": [{"msg": "bad date"}]}), "[{'msg': 'bad date'}]"),
        (httpx.Response(200, json={"success": False, "message": "Duplicate"}), "Duplicate"),
    ],
)
async def test_rejection_carries_the_services_reason(response: httpx.Response, reason: str) -> None:
    ledger, _ = service(lambda _: response)

    with pytest.raises(LedgerRejectedTransactionError) as raised:
        await ledger.submit_receipt(TRANSACTION)

    assert raised.value.reason == reason


async def test_server_errors_and_connection_failures_mean_unavailable() -> None:
    def refuse(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("refused", request=request)

    broken, _ = service(lambda _: httpx.Response(503, json={"message": "Ledger file not found"}))
    unreachable, _ = service(refuse)

    with pytest.raises(LedgerUnavailableError):
        await broken.list_accounts()
    with pytest.raises(LedgerUnavailableError):
        await unreachable.submit_receipt(TRANSACTION)
