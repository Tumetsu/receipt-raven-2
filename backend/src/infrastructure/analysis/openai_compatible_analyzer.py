"""Receipt analysis through an OpenAI-compatible chat completions API.

Serves both OpenRouter and OpenAI. OpenRouter accepts PDFs as file parts and
enforces the JSON schema; OpenAI gets JSON mode and images.
"""

import base64
from typing import Any

import httpx
import structlog

from src.application.analysis.protocols.receipt_analyzer import (
    ReceiptAnalysis,
    ReceiptAnalysisError,
)
from src.infrastructure.analysis.receipt_prompt import (
    RECEIPT_JSON_SCHEMA,
    build_prompt,
    parse_answer,
)

logger = structlog.get_logger(__name__)

MAX_COMPLETION_TOKENS = 4000


class OpenAICompatibleReceiptAnalyzer:
    """Sends the document and prompt to `{base_url}/chat/completions`."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str,
        model: str,
        timeout_seconds: float,
        structured_output: bool,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout_seconds
        self.structured_output = structured_output
        self.transport = transport

    def _document_part(self, document: bytes, mime_type: str) -> dict[str, Any]:
        data_url = f"data:{mime_type};base64,{base64.b64encode(document).decode('ascii')}"
        if mime_type == "application/pdf":
            return {"type": "file", "file": {"filename": "receipt.pdf", "file_data": data_url}}
        return {"type": "image_url", "image_url": {"url": data_url}}

    def _request_body(
        self, document: bytes, mime_type: str, expense_accounts: list[str]
    ) -> dict[str, Any]:
        response_format: dict[str, Any] = (
            {
                "type": "json_schema",
                "json_schema": {"name": "receipt", "strict": True, "schema": RECEIPT_JSON_SCHEMA},
            }
            if self.structured_output
            else {"type": "json_object"}
        )
        return {
            "model": self.model,
            "max_completion_tokens": MAX_COMPLETION_TOKENS,
            "response_format": response_format,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        self._document_part(document, mime_type),
                        {"type": "text", "text": build_prompt(expense_accounts)},
                    ],
                }
            ],
        }

    async def analyze(
        self, document: bytes, mime_type: str, expense_accounts: list[str]
    ) -> ReceiptAnalysis:
        if not self.api_key:
            raise ReceiptAnalysisError("No API key is configured for the AI provider")
        try:
            async with httpx.AsyncClient(timeout=self.timeout, transport=self.transport) as client:
                response = await client.post(
                    f"{self.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.api_key}"},
                    json=self._request_body(document, mime_type, expense_accounts),
                )
                response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise ReceiptAnalysisError(
                f"AI provider answered {exc.response.status_code}: {exc.response.text[:500]}"
            ) from exc
        except httpx.HTTPError as exc:
            raise ReceiptAnalysisError(f"AI provider not reachable: {exc}") from exc

        body: Any = response.json()
        try:
            content = body["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise ReceiptAnalysisError("No content in the AI provider's answer") from exc
        if not content:
            raise ReceiptAnalysisError("No content in the AI provider's answer")
        usage = body.get("usage") or {}
        logger.info("receipt_analysed", model=body.get("model"), tokens=usage.get("total_tokens"))
        return parse_answer(str(content), str(body.get("model") or self.model))
