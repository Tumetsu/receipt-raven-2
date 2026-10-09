"""The prompt and answer format for receipt analysis, shared by every provider."""

import re
from datetime import date
from typing import Any

from pydantic import BaseModel, ValidationError

from src.application.analysis.protocols.receipt_analyzer import (
    AnalysedProduct,
    ReceiptAnalysis,
    ReceiptAnalysisError,
)
from src.domain.receipts.entities.receipt import DEFAULT_CURRENCY

PROMPT_TEMPLATE = """
Please read the details of the provided receipt and extract the following:
- payee: Name of the shop, restaurant or service provider
- description: Short summary of the receipt content, prefer Finnish if possible
- date: Date of purchase in YYYY-MM-DD format
- currency: ISO 4217 code of the currency the receipt is in, such as EUR or JPY
- products: Each line item with name, expenseAccount, and price in the receipt's currency
- total: Total sum paid, in the receipt's currency

The products' prices must add up to the total. If the receipt adds tax or a service
charge on top of the item prices (for example Japanese consumption tax, 消費税 / 外税),
add it to the prices of the items it applies to, so that they include it.

Write product names in Latin script: if the receipt is in another script, such as
Japanese, translate the names into English.

For expenseAccount, choose the most suitable from this list (consider both the item and the payee): {accounts}

If you cannot find information for a property, return null for it.
"""

# Strict structured-output schema: every property required, nulls typed explicitly.
RECEIPT_JSON_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "required": ["payee", "description", "date", "currency", "products", "total"],
    "properties": {
        "payee": {"type": "string"},
        "description": {"type": ["string", "null"]},
        "date": {"type": ["string", "null"]},
        "currency": {"type": ["string", "null"]},
        "products": {
            "type": "array",
            "items": {
                "type": "object",
                "additionalProperties": False,
                "required": ["name", "expenseAccount", "price"],
                "properties": {
                    "name": {"type": "string"},
                    "expenseAccount": {"type": "string"},
                    "price": {"type": "number"},
                },
            },
        },
        "total": {"type": "number"},
    },
}


def build_prompt(expense_accounts: list[str]) -> str:
    return PROMPT_TEMPLATE.format(accounts=",".join(expense_accounts))


class _Product(BaseModel):
    name: str
    expenseAccount: str | None = None  # noqa: N815 - the model's JSON field name
    price: float


class _Answer(BaseModel):
    payee: str
    description: str | None = None
    date: str | None = None
    currency: str | None = None
    products: list[_Product] = []
    total: float


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _parse_currency(value: str | None) -> str:
    code = (value or "").strip().upper()
    return code if re.fullmatch(r"[A-Z]{3}", code) else DEFAULT_CURRENCY


def parse_answer(content: str, model: str) -> ReceiptAnalysis:
    """Validate the model's JSON answer.

    An unreadable date becomes None; a missing or malformed currency, EUR.

    Raises:
        ReceiptAnalysisError: If the answer is not JSON of the expected shape.
    """
    try:
        answer = _Answer.model_validate_json(content)
    except ValidationError as exc:
        raise ReceiptAnalysisError(f"Invalid receipt analysis result: {exc}") from exc
    return ReceiptAnalysis(
        payee=answer.payee,
        description=answer.description,
        receipt_date=_parse_date(answer.date),
        products=tuple(
            AnalysedProduct(name=p.name, expense_account=p.expenseAccount or "", price=p.price)
            for p in answer.products
        ),
        total=answer.total,
        model=model,
        currency=_parse_currency(answer.currency),
    )
