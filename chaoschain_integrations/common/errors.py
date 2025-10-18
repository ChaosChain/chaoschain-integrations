"""Custom error types for ChaosChain integrations."""

from typing import Any, Dict, Optional


class AdapterError(Exception):
    """Base exception for all adapter errors."""

    def __init__(
        self,
        message: str,
        *,
        adapter_name: str = "unknown",
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.adapter_name = adapter_name
        self.details = details or {}

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(adapter={self.adapter_name}, message={self.message})"


class ConfigurationError(AdapterError):
    """Raised when adapter configuration is invalid or missing."""

    pass


class ConnectionError(AdapterError):
    """Raised when connection to backend service fails."""

    pass


class TimeoutError(AdapterError):
    """Raised when operation exceeds timeout threshold."""

    pass


class ValidationError(AdapterError):
    """Raised when request or response validation fails."""

    pass


class AuthenticationError(AdapterError):
    """Raised when authentication with backend service fails."""

    pass


class ResourceNotFoundError(AdapterError):
    """Raised when requested resource is not found."""

    pass


class RateLimitError(AdapterError):
    """Raised when rate limit is exceeded."""

    def __init__(
        self,
        message: str,
        *,
        adapter_name: str = "unknown",
        retry_after: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message, adapter_name=adapter_name, details=details)
        self.retry_after = retry_after

