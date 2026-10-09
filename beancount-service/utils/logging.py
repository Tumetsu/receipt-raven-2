"""
Structured logging configuration using structlog
"""
import logging
import sys
from typing import Any

import structlog


def setup_logging(log_level: str = "INFO") -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    # Configure standard library logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper()),
    )

    # Configure structlog
    structlog.configure(
        processors=[
            # Merge thread-local context
            structlog.contextvars.merge_contextvars,
            # Add log level to event dict
            structlog.stdlib.add_log_level,
            # Add logger name to event dict (requires stdlib logger factory)
            structlog.stdlib.add_logger_name,
            # Add timestamp
            structlog.processors.TimeStamper(fmt="iso"),
            # Add exception info if present
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            # Render as JSON for production, colored console for development
            structlog.processors.JSONRenderer()
            if log_level.upper() != "DEBUG"
            else structlog.dev.ConsoleRenderer(colors=True),
        ],
        # Wrapper class for the logger
        wrapper_class=structlog.stdlib.BoundLogger,
        # Use stdlib logger factory to ensure compatibility with add_logger_name
        logger_factory=structlog.stdlib.LoggerFactory(),
        # Cache logger instances
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = __name__) -> structlog.stdlib.BoundLogger:
    """
    Get a configured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured logger instance
    """
    return structlog.get_logger(name)
