"""Rules that pick the account a receipt was paid from, based on its payee.

Some shops are always paid from the same account (for example groceries from a
household account). The first rule whose pattern matches the payee wins.
"""

import re
from dataclasses import dataclass

from src.domain.common.exceptions import ValidationError
from src.domain.common.value_object import ValueObject


@dataclass(frozen=True)
class PayeeAccountRule(ValueObject):
    """Pay receipts whose payee matches `payee_pattern` from `source_account`."""

    payee_pattern: str
    source_account: str
    description: str | None = None

    def __post_init__(self) -> None:
        try:
            re.compile(self.payee_pattern)
        except re.error as exc:
            raise ValidationError(
                f"Invalid payee pattern {self.payee_pattern!r}: {exc}", field="payee_pattern"
            ) from exc

    def matches(self, payee: str) -> bool:
        """Case-insensitive search, like the original JavaScript `RegExp(p, 'i')`."""
        return re.search(self.payee_pattern, payee, flags=re.IGNORECASE) is not None


@dataclass(frozen=True)
class PayeeAccountRules(ValueObject):
    """An ordered list of rules; the first match decides."""

    rules: tuple[PayeeAccountRule, ...] = ()

    def source_account_for(self, payee: str) -> PayeeAccountRule | None:
        """Return the first rule matching the payee, or None."""
        return next((rule for rule in self.rules if rule.matches(payee)), None)
