"""
Base Protocol for Storage adapters.

This mirrors the StorageBackend interface from chaoschain-sdk to maintain
loose coupling between the SDK and integrations.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol


@dataclass
class StorageProof:
    """Proof/verification data for stored content."""

    method: str  # e.g., "ipfs-cid", "merkle-proof", "keccak-256"
    content_hash: str  # Primary content identifier (CID, hash, etc.)
    metadata: Optional[Dict[str, Any]] = None
    signature: Optional[str] = None
    timestamp: Optional[int] = None
    verifier_url: Optional[str] = None


@dataclass
class StorageResult:
    """Result from storage operation."""

    uri: str  # Primary URI (ipfs://, ar://, zerog://, etc.)
    proof: StorageProof
    raw: Optional[Dict[str, Any]] = None  # Original response from backend
    alternative_uris: Optional[list[str]] = None  # Alternative access methods


class StorageBackend(Protocol):
    """
    Protocol for storage adapter implementations.

    All storage adapters must implement these methods to be compatible
    with ChaosChainAgentSDK.
    """

    def put(
        self,
        content: bytes,
        *,
        metadata: Optional[Dict[str, Any]] = None,
        timeout_s: int = 60,
    ) -> StorageResult:
        """
        Store content and return proof.

        Args:
            content: Bytes to store
            metadata: Optional metadata to associate with content
            timeout_s: Operation timeout in seconds

        Returns:
            StorageResult with URI and proof

        Raises:
            TimeoutError: If operation exceeds timeout
            ValidationError: If content validation fails
            ConnectionError: If backend connection fails
        """
        ...

    def get(
        self,
        uri: str,
        *,
        timeout_s: int = 60,
    ) -> bytes:
        """
        Retrieve content by URI.

        Args:
            uri: Content URI (format depends on backend)
            timeout_s: Operation timeout in seconds

        Returns:
            Content bytes

        Raises:
            ResourceNotFoundError: If URI not found
            TimeoutError: If operation exceeds timeout
            ConnectionError: If backend connection fails
        """
        ...

    def exists(
        self,
        uri: str,
        *,
        timeout_s: int = 30,
    ) -> bool:
        """
        Check if content exists at URI.

        Args:
            uri: Content URI
            timeout_s: Operation timeout in seconds

        Returns:
            True if content exists, False otherwise

        Raises:
            TimeoutError: If operation exceeds timeout
            ConnectionError: If backend connection fails
        """
        ...

    def get_proof(
        self,
        uri: str,
        *,
        timeout_s: int = 30,
    ) -> StorageProof:
        """
        Get proof for stored content without fetching content.

        Args:
            uri: Content URI
            timeout_s: Operation timeout in seconds

        Returns:
            StorageProof for the content

        Raises:
            ResourceNotFoundError: If URI not found
            TimeoutError: If operation exceeds timeout
            ConnectionError: If backend connection fails
        """
        ...

