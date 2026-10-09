"""Payee account rules read from a JSON file.

Format (the same as the original app's `config/payee-account-rules.json`):

    {"rules": [{"payeePattern": "K-Market|Prisma",
                "sourceAccount": "Assets:Bank:Checking",
                "description": "optional"}]}
"""

from pathlib import Path

import structlog
from pydantic import BaseModel, ValidationError

from src.domain.common.exceptions import ValidationError as DomainValidationError
from src.domain.receipts.payee_account_rules import PayeeAccountRule, PayeeAccountRules

logger = structlog.get_logger(__name__)


class _Rule(BaseModel):
    payeePattern: str  # noqa: N815 - the file's field names
    sourceAccount: str  # noqa: N815
    description: str | None = None


class _RulesFile(BaseModel):
    rules: list[_Rule]


class PayeeAccountRulesFile:
    """Loads the rules once; a missing or invalid file means no rules."""

    def __init__(self, path: Path) -> None:
        self.path = path
        self._rules: PayeeAccountRules | None = None

    def load(self) -> PayeeAccountRules:
        if self._rules is None:
            self._rules = self._read()
        return self._rules

    def _read(self) -> PayeeAccountRules:
        if not self.path.is_file():
            logger.info("payee_rules_not_found", path=str(self.path))
            return PayeeAccountRules()
        try:
            parsed = _RulesFile.model_validate_json(self.path.read_text(encoding="utf-8"))
            rules = PayeeAccountRules(
                rules=tuple(
                    PayeeAccountRule(
                        payee_pattern=rule.payeePattern,
                        source_account=rule.sourceAccount,
                        description=rule.description,
                    )
                    for rule in parsed.rules
                )
            )
        except (OSError, ValidationError, DomainValidationError) as exc:
            logger.error("payee_rules_invalid", path=str(self.path), error=str(exc))
            return PayeeAccountRules()
        logger.info("payee_rules_loaded", count=len(rules.rules))
        return rules
