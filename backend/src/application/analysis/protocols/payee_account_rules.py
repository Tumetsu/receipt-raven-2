"""Port to the configured payee-to-source-account rules."""

from typing import Protocol

from src.domain.receipts.payee_account_rules import PayeeAccountRules


class PayeeAccountRulesProviderProtocol(Protocol):
    """Supplies the current rules; an absent or broken configuration means no rules."""

    def load(self) -> PayeeAccountRules: ...
