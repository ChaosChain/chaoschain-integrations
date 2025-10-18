"""ZeroG storage adapter implementing StorageBackend protocol."""

from typing import Any, Dict, Optional

from chaoschain_integrations.common.logging import get_logger
from chaoschain_integrations.storage.base import (
    StorageBackend,
    StorageProof,
    StorageResult,
)
from chaoschain_integrations.storage.zerog.client import ZeroGStorageClient

logger = get_logger(__name__)


class ZeroGStorageAdapter(StorageBackend):
    """
    ZeroG storage adapter for ChaosChain SDK.

    This adapter implements the StorageBackend protocol using ZeroG's
    decentralized storage network via a gRPC sidecar.
    """

    def __init__(
        self,
        *,
        grpc_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
    ) -> None:
        """
        Initialize ZeroG storage adapter.

        Args:
            grpc_url: ZeroG sidecar gRPC endpoint
            api_key: Optional API key for authentication
            timeout_seconds: Default timeout for operations
        """
        self.client = ZeroGStorageClient(
            grpc_url=grpc_url,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
        )
        logger.info("zerog_storage_adapter_initialized")

    def put(
        self,
        content: bytes,
        *,
        metadata: Optional[Dict[str, Any]] = None,
        timeout_s: int = 60,
    ) -> StorageResult:
        """Store content in ZeroG and return proof."""
        logger.info("zerog_storage_put_start", content_size=len(content))

        response = self.client.put(content, metadata=metadata, timeout_s=timeout_s)

        proof = StorageProof(
            method="merkle-proof",
            content_hash=response.root_hash,
            metadata={
                "merkle_proof": response.merkle_proof,
                "size_bytes": response.size_bytes,
                "file_id": response.file_id,
            },
            timestamp=response.timestamp,
            verifier_url=f"zerog://{response.file_id}",
        )

        result = StorageResult(
            uri=f"zerog://{response.file_id}",
            proof=proof,
            raw=response.model_dump(),
            alternative_uris=[
                f"zerog://{response.file_id}",
                f"0g://{response.file_id}",
            ],
        )

        logger.info(
            "zerog_storage_put_success",
            uri=result.uri,
            content_hash=proof.content_hash,
        )

        return result

    def get(
        self,
        uri: str,
        *,
        timeout_s: int = 60,
    ) -> bytes:
        """Retrieve content from ZeroG by URI."""
        file_id = self._extract_file_id(uri)
        logger.info("zerog_storage_get_start", uri=uri, file_id=file_id)

        response = self.client.get(file_id, timeout_s=timeout_s)

        logger.info(
            "zerog_storage_get_success",
            uri=uri,
            content_size=len(response.content),
        )

        return response.content

    def exists(
        self,
        uri: str,
        *,
        timeout_s: int = 30,
    ) -> bool:
        """Check if content exists at URI."""
        file_id = self._extract_file_id(uri)
        logger.info("zerog_storage_exists_check", uri=uri, file_id=file_id)

        response = self.client.exists(file_id, timeout_s=timeout_s)

        logger.info(
            "zerog_storage_exists_result",
            uri=uri,
            exists=response.exists,
        )

        return response.exists

    def get_proof(
        self,
        uri: str,
        *,
        timeout_s: int = 30,
    ) -> StorageProof:
        """Get proof for stored content."""
        file_id = self._extract_file_id(uri)
        logger.info("zerog_storage_get_proof_start", uri=uri, file_id=file_id)

        response = self.client.get_proof(file_id, timeout_s=timeout_s)

        proof = StorageProof(
            method="merkle-proof",
            content_hash=response.root_hash,
            metadata={
                "merkle_proof": response.merkle_proof,
                "file_id": response.file_id,
            },
            timestamp=response.timestamp,
            verifier_url=f"zerog://{response.file_id}",
        )

        logger.info(
            "zerog_storage_get_proof_success",
            uri=uri,
            content_hash=proof.content_hash,
        )

        return proof

    @staticmethod
    def _extract_file_id(uri: str) -> str:
        """Extract file ID from ZeroG URI."""
        # Handle both zerog:// and 0g:// schemes
        if uri.startswith("zerog://"):
            return uri[8:]
        elif uri.startswith("0g://"):
            return uri[5:]
        else:
            return uri

