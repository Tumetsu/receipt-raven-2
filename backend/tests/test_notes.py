"""API tests for the notes endpoints."""

from httpx import AsyncClient

NOTES = "/api/v1/notes"


async def create_note(client: AsyncClient, title: str, body: str = "") -> dict[str, object]:
    response = await client.post(NOTES, json={"title": title, "body": body})
    assert response.status_code == 201, response.text
    return response.json()


class TestCreateNote:
    async def test_creates_note_with_trimmed_title(self, client: AsyncClient) -> None:
        created = await create_note(client, "  Shopping list  ", "milk, eggs")

        assert created["title"] == "Shopping list"
        assert created["body"] == "milk, eggs"

        fetched = await client.get(f"{NOTES}/{created['id']}")
        assert fetched.status_code == 200
        assert fetched.json()["title"] == "Shopping list"

    async def test_rejects_blank_title_with_domain_message(self, client: AsyncClient) -> None:
        response = await client.post(NOTES, json={"title": "   ", "body": ""})

        assert response.status_code == 400
        assert response.json() == {
            "error": "bad_request",
            "message": "Note title cannot be empty",
        }


class TestListNotes:
    async def test_lists_most_recently_created_first_with_preview(
        self, client: AsyncClient
    ) -> None:
        await create_note(client, "First", "a" * 500)
        await create_note(client, "Second")

        response = await client.get(NOTES)

        assert response.status_code == 200
        items = response.json()["items"]
        assert [item["title"] for item in items] == ["Second", "First"]
        assert items[1]["body_preview"] == "a" * 140

    async def test_filters_by_title_case_insensitively(self, client: AsyncClient) -> None:
        await create_note(client, "Groceries")
        await create_note(client, "Meeting notes")
        await create_note(client, "100% done")

        groceries = await client.get(NOTES, params={"search": "GROC"})
        percent = await client.get(NOTES, params={"search": "%"})

        assert [item["title"] for item in groceries.json()["items"]] == ["Groceries"]
        assert [item["title"] for item in percent.json()["items"]] == ["100% done"]


class TestUpdateNote:
    async def test_replaces_title_and_body(self, client: AsyncClient) -> None:
        created = await create_note(client, "Draft", "old")

        response = await client.put(
            f"{NOTES}/{created['id']}", json={"title": "Final", "body": "new"}
        )

        assert response.status_code == 200
        fetched = (await client.get(f"{NOTES}/{created['id']}")).json()
        assert (fetched["title"], fetched["body"]) == ("Final", "new")

    async def test_unknown_note_is_not_found(self, client: AsyncClient) -> None:
        response = await client.put(f"{NOTES}/999", json={"title": "x", "body": ""})

        assert response.status_code == 404
        assert response.json()["error"] == "not_found"


class TestDeleteNote:
    async def test_deletes_note(self, client: AsyncClient) -> None:
        created = await create_note(client, "Temporary")

        response = await client.delete(f"{NOTES}/{created['id']}")

        assert response.status_code == 204
        assert (await client.get(f"{NOTES}/{created['id']}")).status_code == 404

    async def test_unknown_note_is_not_found(self, client: AsyncClient) -> None:
        response = await client.delete(f"{NOTES}/999")

        assert response.status_code == 404
