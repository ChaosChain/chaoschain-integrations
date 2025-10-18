"""Pinata storage adapter implementing StorageBackend protocol."""

import asyncio
from typing import Any, Dict, Optional

from chaoschain_integrations.common.logging import get_logger
from chaoschain_integrations.storage.base import (
    StorageBackend,
    StorageProof,
    StorageResult,
)
from chaoschain_integrations.storage.ipfs_pinata.client import PinataClient
from chaoschain_integrations.storage.ipfs_pinata.schemas import (
    PinataMetadata,
    PinataOptions,
)

logger = get_logger(__name__)


class PinataStorageAdapter(StorageBackend):
    """
    Pinata (IPFS) storage adapter for ChaosChain SDK.

    This adapter implements the StorageBackend protocol using Pinata's
    IPFS pinning service via HTTP API.
    """

    def __init__(
        self,
        *,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        jwt: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
    ) -> None:
        """
        Initialize Pinata storage adapter.

        Args:
            api_url: Pinata API base URL
            api_key: Pinata API key (for key+secret auth)
            api_secret: Pinata API secret (for key+secret auth)
            jwt: Pinata JWT token (preferred auth method)
            timeout_seconds: Default timeout for operations
        """
        self.client = PinataClient(
            api_url=api_url,
            api_key=api_key,
            api_secret=api_secret,
            jwt=jwt,
            timeout_seconds=timeout_seconds,
        )
        logger.info("pinata_storage_adapter_initialized")

    def put(
        self,
        content: bytes,
        *,
        metadata: Optional[Dict[str, Any]] = None,
        timeout_s: int = 60,
    ) -> StorageResult:
        """Store content on IPFS via Pinata and return proof."""
        logger.info("pinata_storage_put_start", content_size=len(content))

        # Convert metadata to Pinata format
        pinata_metadata = None
        if metadata:
            pinata_metadata = PinataMetadata(
                name=metadata.get("name"),
                keyvalues=metadata.get("keyvalues") or metadata,
            )

        # Pin file (async operation, but we expose sync interface)
        response = asyncio.run(
            self.client.pin_file(
                content=content,
                metadata=pinata_metadata,
                options=PinataOptions(cidVersion=1),
                timeout_s=timeout_s,
            )
        )

        # Create proof with IPFS CID
        proof = StorageProof(
            method="ipfs-cid",
            content_hash=response.IpfsHash,
            metadata={
                "pin_size": response.PinSize,
                "timestamp": response.Timestamp,
                "is_duplicate": response.isDuplicate,
            },
            verifier_url=f"https://gateway.pinata.cloud/ipfs/{response.IpfsHash}",
        )

        result = StorageResult(
            uri=f"ipfs://{response.IpfsHash}",
            proof=proof,
            raw=response.model_dump(),
            alternative_uris=[
                f"ipfs://{response.IpfsHash}",
                f"https://gateway.pinata.cloud/ipfs/{response.IpfsHash}",
                f"https://ipfs.io/ipfs/{response.IpfsHash}",
            ],
        )

        logger.info(
            "pinata_storage_put_success",
            uri=result.uri,
            cid=response.IpfsHash,
        )

        return result

    def get(
        self,
        uri: str,
        *,
        timeout_s: int = 60,
    ) -> bytes:
        """Retrieve content from IPFS by URI."""
        cid = self._extract_cid(uri)
        logger.info("pinata_storage_get_start", uri=uri, cid=cid)

        content = asyncio.run(self.client.get_file(cid, timeout_s=timeout_s))

        logger.info(
            "pinata_storage_get_success",
            uri=uri,
            content_size=len(content),
        )

        return content

    def exists(
        self,
        uri: str,
        *,
        timeout_s: int = 30,
    ) -> bool:
        """Check if content exists at URI."""
        cid = self._extract_cid(uri)
        logger.info("pinata_storage_exists_check", uri=uri, cid=cid)

        exists = asyncio.run(self.client.pin_exists(cid, timeout_s=timeout_s))

        logger.info(
            "pinata_storage_exists_result",
            uri=uri,
            exists=exists,
        )

        return exists

    def get_proof(
        self,
        uri: str,
        *,
        timeout_s: int = 30,
    ) -> StorageProof:
        """Get proof for stored content."""
        cid = self._extract_cid(uri)
        logger.info("pinata_storage_get_proof_start", uri=uri, cid=cid)

        # For IPFS, the CID itself is the proof (content-addressed)
        proof = StorageProof(
            method="ipfs-cid",
            content_hash=cid,
            metadata={
                "uri": uri,
            },
            verifier_url=f"https://gateway.pinata.cloud/ipfs/{cid}",
        )

        logger.info(
            "pinata_storage_get_proof_success",
            uri=uri,
            cid=cid,
        )

        return proof

    @staticmethod
    def _extract_cid(uri: str) -> str:
        """Extract CID from IPFS URI."""
        if uri.startswith("ipfs://"):
            return uri[7:]
        elif uri.startswith("https://") and "/ipfs/" in uri:
            # Extract from gateway URL
            return uri.split("/ipfs/")[1].split("/")[0]
        else:
            # Assume it's already a CID
            return uri

