"""
Application settings using Pydantic Settings for type-safe configuration
"""
import os
from functools import lru_cache
from typing import List, Union

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings with validation"""

    # Beancount Configuration
    beancount_ledger_path: str = Field(
        ...,  # Required field
        description="Path to the beancount ledger file",
    )

    # Server Configuration
    host: str = Field(
        default="0.0.0.0",
        description="Server host address",
    )
    port: int = Field(
        default=8000,
        description="Server port",
        ge=1,
        le=65535,
    )

    # CORS Configuration
    allowed_origins: Union[str, List[str]] = Field(
        default="",
        description="List of allowed CORS origins (comma-separated string or JSON array)",
    )

    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging level",
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra fields in .env
    )

    @field_validator("beancount_ledger_path")
    @classmethod
    def validate_ledger_path(cls, v: str) -> str:
        """Validate that the ledger path is set"""
        if not v:
            raise ValueError("BEANCOUNT_LEDGER_PATH must be set")
        return v

    @field_validator("allowed_origins")
    @classmethod
    def parse_allowed_origins(cls, v) -> List[str]:
        """Parse comma-separated allowed origins or JSON array"""
        if isinstance(v, str):
            # Handle empty string
            if not v.strip():
                return []
            # Split by comma and filter out empty strings
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        if isinstance(v, list):
            return v
        return []

    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level"""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(
                f"Invalid log level: {v}. Must be one of {valid_levels}"
            )
        return v_upper


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached settings instance.

    This function is cached so that the settings are loaded only once.
    Useful for dependency injection in FastAPI.

    Returns:
        Settings instance
    """
    return Settings()
