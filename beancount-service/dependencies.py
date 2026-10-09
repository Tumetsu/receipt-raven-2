"""
Dependency injection for FastAPI
"""
from functools import lru_cache

from config import Settings, get_settings
from repositories import ILedgerRepository, BeancountFileRepository


@lru_cache()
def get_ledger_repository() -> ILedgerRepository:
    """
    Get the ledger repository instance (cached).

    This function is cached so that the same repository instance
    is reused across requests, maintaining cache state.

    Returns:
        ILedgerRepository instance
    """
    settings: Settings = get_settings()
    return BeancountFileRepository(
        ledger_path=settings.beancount_ledger_path,
        cache_ttl_seconds=60  # Cache for 60 seconds
    )
