"""Pinata HTTP client for IPFS operations."""

import hashlib
import io
from typing import Optional

import httpx

from chaoschain_integrations.common.config import PinataConfig
from chaoschain_integrations.common.errors import (
    AuthenticationError,
    ConnectionError,
    ResourceNotFoundError,
    TimeoutError,
    ValidationError,
)
from chaoschain_integrations.common.logging import get_logger
from chaoschain_integrations.storage.ipfs_pinata.schemas import (
    PinataMetadata,
    PinataOptions,
    PinFileResponse,
)

logger = get_logger(__name__)


class PinataClient:
    """
    HTTP client for Pinata API.

    Pinata provides IPFS pinning services with a simple REST API.
    """

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        jwt: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
    ) -> None:
        """
        Initialize Pinata client.

        Args:
            api_url: Pinata API base URL
            api_key: Pinata API key (for key+secret auth)
            api_secret: Pinata API secret (for key+secret auth)
            jwt: Pinata JWT token (preferred auth method)
            timeout_seconds: Request timeout
        """
        config = PinataConfig()
        self.api_url = (api_url or config.api_url).rstrip("/")
        self.api_key = api_key or config.api_key
        self.api_secret = api_secret or config.api_secret
        self.jwt = jwt or config.jwt
        self.timeout = timeout_seconds or config.timeout_seconds

        # Prefer JWT over API key+secret
        if self.jwt:
            self.headers = {
                "Authorization": f"Bearer {self.jwt}",
            }
        elif self.api_key and self.api_secret:
            self.headers = {
                "pinata_api_key": self.api_key,
                "pinata_secret_api_key": self.api_secret,
            }
        else:
            raise ValidationError(
                "Must provide either JWT or API key+secret",
                adapter_name="pinata",
            )

        logger.info(
            "pinata_client_init",
            api_url=self.api_url,
            auth_method="jwt" if self.jwt else "api_key",
        )

    async def pin_file(
        self,
        content: bytes,
        name: Optional[str] = None,
        metadata: Optional[PinataMetadata] = None,
        options: Optional[PinataOptions] = None,
        timeout_s: Optional[int] = None,
    ) -> PinFileResponse:
        """
        Pin file to IPFS via Pinata.

        Args:
            content: File content bytes
            name: Optional name for the pin
            metadata: Optional metadata
            options: Optional pin options
            timeout_s: Request timeout

        Returns:
            Pin response with IPFS CID

        Raises:
            AuthenticationError: If credentials are invalid
            TimeoutError: If request times out
            ConnectionError: If request fails
        """
        timeout = timeout_s or self.timeout

        # Compute local hash for logging
        content_hash = hashlib.sha256(content).hexdigest()
        logger.info(
            "pinata_pin_file_start",
            content_size=len(content),
            content_hash=content_hash[:16],
            name=name,
        )

        # Prepare multipart form data
        files = {
            "file": ("file", io.BytesIO(content)),
        }

        # Add metadata if provided
        data = {}
        if metadata or name:
            meta = metadata or PinataMetadata()
            if name:
                meta.name = name
            data["pinataMetadata"] = meta.model_dump_json()

        if options:
            data["pinataOptions"] = options.model_dump_json()

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.api_url}/pinning/pinFileToIPFS",
                    headers=self.headers,
                    files=files,
                    data=data,
                    timeout=timeout,
                )

                if response.status_code == 401:
                    raise AuthenticationError(
                        "Invalid Pinata credentials",
                        adapter_name="pinata",
                        details={"status_code": response.status_code},
                    )

                response.raise_for_status()
                result = PinFileResponse(**response.json())

                logger.info(
                    "pinata_pin_file_success",
                    cid=result.IpfsHash,
                    size=result.PinSize,
                    is_duplicate=result.isDuplicate,
                )

                return result

        except httpx.TimeoutException as e:
            logger.error("pinata_pin_file_timeout", timeout=timeout)
            raise TimeoutError(
                f"Pin request timed out after {timeout}s",
                adapter_name="pinata",
                details={"timeout": timeout},
            ) from e

        except httpx.HTTPStatusError as e:
            logger.error(
                "pinata_pin_file_error",
                status_code=e.response.status_code,
                error=str(e),
            )
            raise ConnectionError(
                f"Pinata API error: {e}",
                adapter_name="pinata",
                details={"status_code": e.response.status_code},
            ) from e

    async def get_file(
        self,
        cid: str,
        timeout_s: Optional[int] = None,
    ) -> bytes:
        """
        Retrieve file from IPFS by CID.

        Args:
            cid: IPFS Content Identifier
            timeout_s: Request timeout

        Returns:
            File content bytes

        Raises:
            ResourceNotFoundError: If CID not found
            TimeoutError: If request times out
            ConnectionError: If request fails
        """
        timeout = timeout_s or self.timeout

        logger.info("pinata_get_file_start", cid=cid)

        # Use Pinata gateway
        gateway_url = f"https://gateway.pinata.cloud/ipfs/{cid}"

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(gateway_url, timeout=timeout)

                if response.status_code == 404:
                    raise ResourceNotFoundError(
                        f"CID not found: {cid}",
                        adapter_name="pinata",
                        details={"cid": cid},
                    )

                response.raise_for_status()

                logger.info(
                    "pinata_get_file_success",
                    cid=cid,
                    size=len(response.content),
                )

                return response.content

        except httpx.TimeoutException as e:
            logger.error("pinata_get_file_timeout", cid=cid, timeout=timeout)
            raise TimeoutError(
                f"Get request timed out after {timeout}s",
                adapter_name="pinata",
                details={"cid": cid, "timeout": timeout},
            ) from e

        except httpx.HTTPStatusError as e:
            logger.error(
                "pinata_get_file_error",
                cid=cid,
                status_code=e.response.status_code,
            )
            raise ConnectionError(
                f"Failed to retrieve {cid}: {e}",
                adapter_name="pinata",
                details={"cid": cid, "status_code": e.response.status_code},
            ) from e

    async def pin_exists(
        self,
        cid: str,
        timeout_s: Optional[int] = None,
    ) -> bool:
        """
        Check if CID is pinned.

        Args:
            cid: IPFS Content Identifier
            timeout_s: Request timeout

        Returns:
            True if pinned, False otherwise
        """
        timeout = timeout_s or self.timeout

        logger.info("pinata_pin_exists_check", cid=cid)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.api_url}/data/pinList",
                    headers=self.headers,
                    params={"hashContains": cid, "status": "pinned"},
                    timeout=timeout,
                )

                response.raise_for_status()
                data = response.json()

                exists = data.get("count", 0) > 0

                logger.info("pinata_pin_exists_result", cid=cid, exists=exists)

                return exists

        except Exception as e:
            logger.warning("pinata_pin_exists_error", cid=cid, error=str(e))
            return False

