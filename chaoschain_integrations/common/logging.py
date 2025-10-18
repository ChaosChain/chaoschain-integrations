"""Structured logging utilities for adapters."""

import logging
import sys
from typing import Any, Dict, Optional

import structlog


def configure_logging(
    log_level: str = "INFO",
    log_format: str = "json",
    correlation_id: Optional[str] = None,
) -> None:
    """
    Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_format: Output format ('json' or 'console')
        correlation_id: Optional correlation ID to include in all logs
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure structlog processors
    processors = [
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
    ]

    if correlation_id:
        processors.insert(0, structlog.processors.CallsiteParameterAdder())

    if log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.extend(
            [
                structlog.dev.ConsoleRenderer(colors=sys.stderr.isatty()),
            ]
        )

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )

    # Configure standard logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stderr,
        level=level,
    )


def get_logger(name: str, **context: Any) -> structlog.stdlib.BoundLogger:
    """
    Get a structured logger with optional context.

    Args:
        name: Logger name (usually __name__)
        **context: Additional context to bind to the logger

    Returns:
        Configured structured logger
    """
    logger = structlog.get_logger(name)
    if context:
        logger = logger.bind(**context)
    return logger


def add_context(**context: Dict[str, Any]) -> None:
    """
    Add context to be included in all subsequent log messages.

    Args:
        **context: Key-value pairs to add to logging context
    """
    structlog.contextvars.bind_contextvars(**context)


def clear_context(*keys: str) -> None:
    """
    Clear specific keys from the logging context.

    Args:
        *keys: Keys to remove from context
    """
    structlog.contextvars.unbind_contextvars(*keys)

