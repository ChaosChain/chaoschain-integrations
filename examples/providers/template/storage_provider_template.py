"""
Template for creating a ChaosChain Storage Provider

Replace "YourProvider" with your provider name (e.g., "Arweave", "Filecoin", "Storj")
"""

from chaoschain_sdk.providers import StorageBackend, StorageResult
from typing import Tuple, Dict, Optional, List, Any
import hashlib


class YourProviderStorage(StorageBackend):
    """
    Your Provider storage backend for ChaosChain.
    
    This provider enables AI agents to use [Your Provider] for decentralized storage.
    
    Example:
        >>> from chaoschain_sdk.providers import register_storage_provider
        >>> register_storage_provider("yourprovider", YourProviderStorage)
        >>> 
        >>> sdk = ChaosChainSDK(
        ...     storage_provider="yourprovider",
        ...     storage_config={"api_key": "your-api-key"}
        ... )
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        **config
    ):
        """
        Initialize Your Provider storage backend.
        
        Args:
            api_key: API key for Your Provider
            base_url: Base URL for Your Provider API (optional)
            **config: Additional configuration options
        """
        self.api_key = api_key or config.get("api_key")
        self.base_url = base_url or config.get("base_url", "https://api.yourprovider.com")
        
        # Add your initialization logic here
        # e.g., create HTTP client, validate credentials, etc.
    
    def put(
        self,
        blob: bytes,
        *,
        mime: Optional[str] = None,
        tags: Optional[Dict[str, str]] = None,
        idempotency_key: Optional[str] = None
    ) -> StorageResult:
        """
        Store data on Your Provider.
        
        Args:
            blob: Data to store
            mime: MIME type (optional, e.g., "application/json")
            tags: Metadata tags (optional)
            idempotency_key: For retry safety (optional)
        
        Returns:
            StorageResult with URI and hash
        """
        # TODO: Implement data upload to your provider
        # 1. Upload blob to your provider's API
        # 2. Get content identifier (CID, transaction ID, etc.)
        # 3. Compute hash for integrity verification
        # 4. Return StorageResult
        
        # Example implementation:
        # response = requests.post(
        #     f"{self.base_url}/upload",
        #     data=blob,
        #     headers={
        #         "Authorization": f"Bearer {self.api_key}",
        #         "Content-Type": mime or "application/octet-stream"
        #     }
        # )
        # content_id = response.json()["id"]
        
        # Compute hash
        content_hash = hashlib.sha256(blob).hexdigest()
        
        # TODO: Replace with actual implementation
        return StorageResult(
            success=False,
            uri="yourprovider://TODO",
            hash=content_hash,
            provider=self.provider_name,
            error="Not implemented"
        )
    
    def get(self, uri: str) -> Tuple[bytes, Optional[Dict]]:
        """
        Retrieve data from Your Provider.
        
        Args:
            uri: Storage URI (e.g., "yourprovider://content_id")
        
        Returns:
            Tuple of (data bytes, metadata dict)
        """
        # TODO: Implement data retrieval
        # 1. Parse URI to extract content identifier
        # 2. Fetch data from your provider's API
        # 3. Return data and metadata
        
        # Example:
        # content_id = uri.replace("yourprovider://", "")
        # response = requests.get(
        #     f"{self.base_url}/content/{content_id}",
        #     headers={"Authorization": f"Bearer {self.api_key}"}
        # )
        # return response.content, response.headers
        
        raise NotImplementedError("Implement get() for your provider")
    
    def verify(self, uri: str, expected_hash: str) -> bool:
        """
        Verify data integrity.
        
        Args:
            uri: Storage URI
            expected_hash: Expected hash (SHA-256 or provider-specific)
        
        Returns:
            True if data matches expected hash
        """
        # TODO: Implement verification
        # 1. Retrieve data
        # 2. Compute hash
        # 3. Compare with expected_hash
        
        try:
            data, _ = self.get(uri)
            actual_hash = hashlib.sha256(data).hexdigest()
            return actual_hash == expected_hash
        except Exception:
            return False
    
    def delete(self, uri: str) -> bool:
        """
        Delete data (if supported by provider).
        
        Note: Some providers (Arweave, IPFS) may not support deletion.
        
        Args:
            uri: Storage URI
        
        Returns:
            True if deleted successfully, False if not supported/failed
        """
        # TODO: Implement deletion if your provider supports it
        # If not supported, return False
        
        return False  # Change to True if deletion is supported
    
    def pin(self, uri: str, name: Optional[str] = None) -> bool:
        """
        Pin content to ensure persistence (for IPFS-like providers).
        
        Args:
            uri: Storage URI
            name: Optional name for the pin
        
        Returns:
            True if pinned successfully or not applicable
        """
        # TODO: Implement pinning if applicable
        # For non-IPFS providers, this may not be relevant
        
        return True  # Not applicable for most providers
    
    def list_content(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        List stored content (if supported by provider).
        
        Args:
            limit: Maximum number of items to return
        
        Returns:
            List of content information dicts
        """
        # TODO: Implement content listing if your provider supports it
        # Return list of dicts with: uri, hash, size, timestamp, etc.
        
        return []
    
    def get_gateway_url(self, uri: str) -> Optional[str]:
        """
        Get HTTPS gateway URL for viewing content.
        
        Args:
            uri: Storage URI
        
        Returns:
            HTTPS URL for viewing, or None if not applicable
        """
        # TODO: Implement gateway URL generation
        # e.g., for Arweave: "https://arweave.net/{tx_id}"
        
        # Example:
        # content_id = uri.replace("yourprovider://", "")
        # return f"https://gateway.yourprovider.com/{content_id}"
        
        return None
    
    @property
    def provider_name(self) -> str:
        """Get provider name."""
        return "yourprovider"  # TODO: Change to your provider name
    
    @property
    def is_available(self) -> bool:
        """Check if provider is available and configured."""
        # TODO: Add more sophisticated availability check if needed
        return self.api_key is not None
    
    @property
    def is_free(self) -> bool:
        """Check if provider is free to use."""
        return False  # TODO: Change if your provider is free
    
    @property
    def requires_api_key(self) -> bool:
        """Check if provider requires an API key."""
        return True  # TODO: Change based on your provider


# ============================================================================
# REGISTRATION
# ============================================================================

def register():
    """Register this provider with ChaosChain SDK."""
    from chaoschain_sdk.providers import register_storage_provider
    
    register_storage_provider(
        "yourprovider",  # TODO: Change to your provider name
        YourProviderStorage,
        aliases=["your-provider", "yp"]  # TODO: Add aliases if desired
    )


# Auto-register when imported
register()

