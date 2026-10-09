"""API tests for cross-cutting app behaviour: health, error shape, headers."""

from httpx import AsyncClient


async def test_health(client: AsyncClient) -> None:
    response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


async def test_responses_carry_request_id_and_security_headers(client: AsyncClient) -> None:
    response = await client.get("/api/v1/receipts")

    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert len(response.headers["X-Request-ID"]) == 36


async def test_not_found_hides_internal_message(client: AsyncClient) -> None:
    response = await client.get("/api/v1/receipts/12345")

    assert response.status_code == 404
    assert response.json() == {
        "error": "not_found",
        "message": "The requested resource was not found.",
    }
