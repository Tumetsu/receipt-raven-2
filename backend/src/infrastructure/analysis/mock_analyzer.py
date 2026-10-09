"""A stand-in analyzer for development and tests: no API key, no cost."""

import asyncio
import json
from datetime import UTC, datetime

from src.application.analysis.protocols.receipt_analyzer import ReceiptAnalysis
from src.infrastructure.analysis.receipt_prompt import parse_answer


def _pick(accounts: list[str], keywords: tuple[str, ...], fallback: str) -> str:
    """The first account whose name contains a keyword, else the first account."""
    for keyword in keywords:
        for account in accounts:
            if keyword in account.lower():
                return account
    return accounts[0] if accounts else fallback


class MockReceiptAnalyzer:
    """Answers every document with the same small grocery receipt, dated today.

    It picks the products' accounts from the ledger's own expense accounts so
    the result can be approved against whatever ledger is configured.
    """

    def __init__(self, delay_seconds: float) -> None:
        self.delay_seconds = delay_seconds

    async def analyze(
        self, document: bytes, mime_type: str, expense_accounts: list[str]
    ) -> ReceiptAnalysis:
        await asyncio.sleep(self.delay_seconds)
        food = _pick(expense_accounts, ("groceries", "food", "ruoka"), "Expenses:Groceries")
        clothes = _pick(expense_accounts, ("clothes", "clothing", "vaatteet"), "Expenses:Clothes")
        answer = {
            "payee": "K-Market",
            "description": "Ruokaa ja paita",
            "date": datetime.now(UTC).astimezone().date().isoformat(),
            "products": [
                {"name": "Banaani", "expenseAccount": food, "price": 0.8},
                {"name": "T-paita", "expenseAccount": clothes, "price": 14.99},
            ],
            "total": 15.79,
        }
        return parse_answer(json.dumps(answer), "mock")
