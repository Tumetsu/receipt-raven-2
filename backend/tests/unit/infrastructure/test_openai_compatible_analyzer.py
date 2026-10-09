"""The AI analyzer against a scripted chat completions endpoint."""

import json
from datetime import date

import httpx
import pytest

from src.application.analysis.protocols.receipt_analyzer import ReceiptAnalysisError
from src.infrastructure.analysis.openai_compatible_analyzer import (
    OpenAICompatibleReceiptAnalyzer,
)


def completion(content: str) -> httpx.Response:
    return httpx.Response(
        200,
        json={
            "model": "anthropic/claude-haiku-4.5",
            "choices": [{"message": {"content": content}}],
        },
    )


def analyzer(
    response: httpx.Response, *, structured: bool = True
) -> tuple[OpenAICompatibleReceiptAnalyzer, list[httpx.Request]]:
    requests: list[httpx.Request] = []

    def handle(request: httpx.Request) -> httpx.Response:
        requests.append(request)
        return response

    return OpenAICompatibleReceiptAnalyzer(
        base_url="https://openrouter.test/api/v1",
        api_key="secret",
        model="anthropic/claude-haiku-4.5",
        timeout_seconds=5,
        structured_output=structured,
        transport=httpx.MockTransport(handle),
    ), requests


ANSWER = json.dumps(
    {
        "payee": "Alko",
        "description": None,
        "date": "2026-10-08",
        "products": [{"name": "Viini", "expenseAccount": "Expenses:Drinks", "price": 12.9}],
        "total": 12.9,
    }
)


async def test_sends_a_pdf_as_a_file_part_with_the_schema_and_accounts() -> None:
    subject, requests = analyzer(completion(ANSWER))

    result = await subject.analyze(b"%PDF", "application/pdf", ["Expenses:Drinks", "Expenses:Food"])

    body = json.loads(requests[0].content)
    document, prompt = body["messages"][0]["content"]
    assert requests[0].url.path == "/api/v1/chat/completions"
    assert requests[0].headers["Authorization"] == "Bearer secret"
    assert document["type"] == "file"
    assert document["file"]["file_data"].startswith("data:application/pdf;base64,")
    assert "Expenses:Drinks,Expenses:Food" in prompt["text"]
    assert body["response_format"]["type"] == "json_schema"
    assert (result.payee, result.receipt_date, result.total) == ("Alko", date(2026, 10, 8), 12.9)
    assert result.model == "anthropic/claude-haiku-4.5"


async def test_sends_an_image_as_image_url_in_json_mode() -> None:
    subject, requests = analyzer(completion(ANSWER), structured=False)

    await subject.analyze(b"\xff\xd8", "image/jpeg", [])

    body = json.loads(requests[0].content)
    assert body["messages"][0]["content"][0]["type"] == "image_url"
    assert body["response_format"] == {"type": "json_object"}


async def test_unreadable_date_becomes_none() -> None:
    subject, _ = analyzer(completion(ANSWER.replace("2026-10-08", "8.10.2026")))

    assert (await subject.analyze(b"x", "image/png", [])).receipt_date is None


@pytest.mark.parametrize(
    "response",
    [
        completion("not json"),
        completion(json.dumps({"payee": "Alko"})),
        httpx.Response(429, text="rate limited"),
        httpx.Response(200, json={"choices": []}),
    ],
)
async def test_unusable_answers_are_analysis_errors(response: httpx.Response) -> None:
    subject, _ = analyzer(response)

    with pytest.raises(ReceiptAnalysisError):
        await subject.analyze(b"x", "image/png", [])
