"""API tests for reading the ledger's accounts and payees."""

from httpx import AsyncClient

from tests.fakes import FakeLedger

LEDGER = "/api/v1/ledger"


async def test_lists_accounts_of_the_requested_types(client: AsyncClient) -> None:
    response = await client.get(
        f"{LEDGER}/accounts", params=[("type", "Assets"), ("type", "Liabilities")]
    )

    assert response.status_code == 200
    assert response.json()["items"] == [
        {"name": "Assets:Checking", "type": "Assets"},
        {"name": "Liabilities:CreditCard", "type": "Liabilities"},
    ]


async def test_lists_every_account_without_a_type(client: AsyncClient) -> None:
    response = await client.get(f"{LEDGER}/accounts")

    assert len(response.json()["items"]) == 5


async def test_lists_payees_sorted_without_duplicates(client: AsyncClient) -> None:
    response = await client.get(f"{LEDGER}/payees")

    assert response.json()["items"] == ["Alko", "K-Market", "Prisma"]


async def test_unavailable_ledger_is_a_bad_gateway(client: AsyncClient, ledger: FakeLedger) -> None:
    ledger.unavailable = True

    response = await client.get(f"{LEDGER}/accounts")

    assert response.status_code == 502
    assert response.json()["error"] == "bad_gateway"
