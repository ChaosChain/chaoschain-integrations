"""
Eigen Compute HTTP client for EigenCloud.

Real production implementation for EigenCloud's compute API.
Based on EigenCloud documentation: https://docs.eigencloud.xyz/
"""

import asyncio
import json
import time
from typing import Any, Dict, List, Optional
from enum import Enum

import httpx

from chaoschain_integrations.common.config import EigenConfig
from chaoschain_integrations.common.errors import (
    AuthenticationError,
    ConnectionError,
    ResourceNotFoundError,
    TimeoutError,
    ValidationError,
)
from chaoschain_integrations.common.logging import get_logger
from chaoschain_integrations.compute.eigen.schemas import (
    EigenCancelResponse,
    EigenResultResponse,
    EigenStatusResponse,
    EigenSubmitResponse,
)

logger = get_logger(__name__)


class EigenComputeClient:
    """
    Production HTTP client for EigenCloud Compute API.
    
    EigenCloud provides TEE-based AI inference with verifiable compute.
    API Documentation: https://docs.eigencloud.xyz/products/eigencompute/
    """

    # EigenAI API endpoints (OpenAI-compatible)
    CHAT_COMPLETIONS_ENDPOINT = "/v1/chat/completions"
    MODELS_ENDPOINT = "/v1/models"

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        use_grpc: bool = False,  # EigenAI uses HTTP REST
        timeout_seconds: Optional[int] = None,
        max_retries: int = 3,
    ) -> None:
        """
        Initialize EigenAI compute client.

        Args:
            api_url: EigenAI API base URL (default: https://eigenai.eigencloud.xyz)
            api_key: EigenAI API key (starts with sk-)
            use_grpc: Reserved for future support (currently HTTP only)
            timeout_seconds: Default timeout for requests
            max_retries: Maximum retry attempts for failed requests
        """
        config = EigenConfig()
        # Use EigenAI endpoint if not specified
        default_url = "https://eigenai.eigencloud.xyz"
        self.api_url = (api_url or config.api_url or default_url).rstrip("/")
        self.api_key = api_key or config.api_key
        self.use_grpc = use_grpc
        self.timeout = timeout_seconds or config.timeout_seconds
        self.max_retries = max_retries

        if not self.api_key:
            raise ValidationError(
                "EigenAI API key is required. Set EIGEN_API_KEY environment variable.",
                adapter_name="eigen",
            )

        # EigenAI uses X-API-Key header (not Bearer)
        self.headers = {
            "X-API-Key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "ChaosChain-Integrations/0.1.0",
        }

        # Job cache for status/result queries (since EigenAI is synchronous)
        self._job_cache: Dict[str, Dict[str, Any]] = {}

        logger.info(
            "eigenai_client_init",
            api_url=self.api_url,
            timeout=self.timeout,
            max_retries=self.max_retries,
        )
    
    async def submit_job(
        self,
        task: Dict[str, Any],
        timeout_s: Optional[int] = None,
    ) -> EigenSubmitResponse:
        """
        Submit inference request to EigenAI (synchronous chat completions).

        Args:
            task: Task specification with fields:
                - model: Model name (default: "gpt-oss-120b-f16")
                - prompt: Input prompt for inference
                - max_tokens: Maximum output tokens
                - temperature: Sampling temperature (optional)
                - seed: Random seed for deterministic results (optional)
            timeout_s: Request timeout

        Returns:
            EigenSubmitResponse with job_id (generated locally)

        Raises:
            AuthenticationError: If API key is invalid
            ValidationError: If task format is invalid
            ConnectionError: If request fails
            TimeoutError: If request times out
        """
        timeout = timeout_s or self.timeout

        logger.info(
            "eigenai_chat_completion",
            model=task.get("model"),
            prompt_length=len(task.get("prompt", "")),
        )

        # Format payload for EigenAI Chat Completions API
        payload = self._format_chat_payload(task)

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.post(
                    f"{self.api_url}{self.CHAT_COMPLETIONS_ENDPOINT}",
                    headers=self.headers,
                    json=payload,
                )

                if response.status_code == 401 or response.status_code == 403:
                    raise AuthenticationError(
                        "Invalid EigenAI API key",
                        adapter_name="eigen",
                        details={"status_code": response.status_code},
                    )

                if response.status_code == 400:
                    error_detail = response.json().get("error", "Invalid request")
                    raise ValidationError(
                        f"Invalid task format: {error_detail}",
                        adapter_name="eigen",
                        details=response.json(),
                    )

                response.raise_for_status()
                data = response.json()

                # Use EigenAI's real job ID (not generated locally!)
                job_id = data.get("id", f"eigen_fallback_{int(time.time())}")

                # Cache the result for status/result queries
                self._job_cache[job_id] = {
                    "status": "completed",
                    "output": data,
                    "created_at": data.get("created", int(time.time())),
                    "completed_at": data.get("created", int(time.time())),
                }

                result = EigenSubmitResponse(
                    job_id=job_id,  # Real EigenAI job ID
                    status="completed",  # EigenAI returns immediately
                    created_at=data.get("created", int(time.time())),
                )

                logger.info(
                    "eigenai_chat_completion_success",
                    job_id=job_id,
                    model=data.get("model"),
                )

                return result

        except httpx.TimeoutException as e:
            logger.error("eigenai_timeout", timeout=timeout, job_id=job_id)
            raise TimeoutError(
                f"Request timed out after {timeout}s",
                adapter_name="eigen",
                details={"timeout": timeout},
            ) from e

        except httpx.HTTPStatusError as e:
            logger.error(
                "eigenai_error",
                status_code=e.response.status_code,
                error=str(e),
                job_id=job_id,
            )
            raise ConnectionError(
                f"EigenAI API error: {e}",
                adapter_name="eigen",
                details={"status_code": e.response.status_code},
            ) from e

    async def get_status(
        self,
        job_id: str,
        timeout_s: Optional[int] = None,
    ) -> EigenStatusResponse:
        """
        Get job status from cache (EigenAI completes immediately).

        Args:
            job_id: Job identifier returned from submit_job

        Returns:
            EigenStatusResponse with job status

        Raises:
            ResourceNotFoundError: If job_id doesn't exist in cache
        """
        logger.info("eigenai_status", job_id=job_id)

        if job_id not in self._job_cache:
            raise ResourceNotFoundError(
                f"Job not found: {job_id}",
                adapter_name="eigen",
                details={"job_id": job_id},
            )

        cached = self._job_cache[job_id]
        
        result = EigenStatusResponse(
            job_id=job_id,
            status=cached["status"],
            progress=100 if cached["status"] == "completed" else 0,
            error=None,
            updated_at=cached.get("completed_at", int(time.time())),
        )

        logger.info(
            "eigenai_status_success",
            job_id=job_id,
            status=result.status,
        )

        return result

    async def get_result(
        self,
        job_id: str,
        timeout_s: Optional[int] = None,
    ) -> EigenResultResponse:
        """
        Get job result from cache (EigenAI returns results immediately).

        Args:
            job_id: Job identifier

        Returns:
            EigenResultResponse with output and TEE attestation

        Raises:
            ResourceNotFoundError: If job doesn't exist in cache
        """
        logger.info("eigenai_result", job_id=job_id)

        if job_id not in self._job_cache:
            raise ResourceNotFoundError(
                f"Job not found: {job_id}",
                adapter_name="eigen",
                details={"job_id": job_id},
            )

        cached = self._job_cache[job_id]
        output_data = cached["output"]

        # Extract text from OpenAI-style response
        choices = output_data.get("choices", [])
        text_output = choices[0].get("message", {}).get("content", "") if choices else ""

        # EigenAI provides TEE signature (cryptographic proof)
        signature = output_data.get("signature")
        system_fingerprint = output_data.get("system_fingerprint")
        
        # Build attestation proof
        attestation = {
            "signature": signature,
            "system_fingerprint": system_fingerprint,
            "id": output_data.get("id"),
            "created": output_data.get("created"),
        } if signature else None
        
        result = EigenResultResponse(
            job_id=job_id,
            status="completed",
            output=text_output,
            attestation=attestation,
            metadata={
                "model": output_data.get("model"),
                "usage": output_data.get("usage"),
                "system_fingerprint": system_fingerprint,
                "signature": signature,
                "full_response": output_data,
            },
            completed_at=cached.get("completed_at"),
        )

        logger.info(
            "eigenai_result_success",
            job_id=job_id,
            has_attestation=bool(result.attestation),
        )

        return result

    async def cancel_job(
        self,
        job_id: str,
        timeout_s: Optional[int] = None,
    ) -> EigenCancelResponse:
        """
        Cancel job (no-op for EigenAI since jobs complete immediately).

        Args:
            job_id: Job identifier

        Returns:
            EigenCancelResponse indicating job is already completed

        Raises:
            ResourceNotFoundError: If job doesn't exist
        """
        logger.info("eigenai_cancel", job_id=job_id)

        if job_id not in self._job_cache:
            raise ResourceNotFoundError(
                f"Job not found: {job_id}",
                adapter_name="eigen",
                details={"job_id": job_id},
            )

        # EigenAI jobs complete immediately, so can't be cancelled
        result = EigenCancelResponse(
            job_id=job_id,
            cancelled=False,
            message="Job already completed (EigenAI returns results synchronously)",
        )

        logger.info("eigenai_cancel_noop", job_id=job_id)
        return result

    async def list_models(self, timeout_s: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        List available models on EigenCloud.

        Returns:
            List of available models with capabilities

        Raises:
            ConnectionError: If request fails
        """
        timeout = timeout_s or self.timeout

        try:
            async with httpx.AsyncClient(timeout=timeout) as client:
                response = await client.get(
                    f"{self.api_url}{self.MODELS_ENDPOINT}",
                    headers=self.headers,
                )

                response.raise_for_status()
                data = response.json()

                logger.info(
                    "eigen_compute_list_models_success",
                    model_count=len(data.get("models", [])),
                )

                return data.get("models", [])

        except httpx.HTTPStatusError as e:
            logger.error(
                "eigen_compute_list_models_error",
                status_code=e.response.status_code,
            )
            raise ConnectionError(
                f"Failed to list models: {e}",
                adapter_name="eigen",
            ) from e

    def _format_chat_payload(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Format task for EigenAI Chat Completions API (OpenAI-compatible).

        Args:
            task: Task specification from user

        Returns:
            Formatted payload for EigenAI API
        """
        # Convert prompt to messages format
        prompt = task.get("prompt", "")
        if isinstance(prompt, str):
            messages = [{"role": "user", "content": prompt}]
        else:
            messages = prompt  # Already in messages format

        # Required fields for EigenAI
        payload = {
            "model": task.get("model", "gpt-oss-120b-f16"),  # Default EigenAI model
            "messages": messages,
        }

        # Optional fields
        if "max_tokens" in task:
            payload["max_tokens"] = task["max_tokens"]

        if "temperature" in task:
            payload["temperature"] = task["temperature"]

        if "seed" in task:
            payload["seed"] = task["seed"]
        else:
            payload["seed"] = 42  # For deterministic results

        # EigenAI-specific fields
        if "top_p" in task:
            payload["top_p"] = task["top_p"]

        if "frequency_penalty" in task:
            payload["frequency_penalty"] = task["frequency_penalty"]

        if "presence_penalty" in task:
            payload["presence_penalty"] = task["presence_penalty"]

        return payload

    # Synchronous wrappers for compatibility
    def submit_job_sync(
        self,
        task: Dict[str, Any],
        timeout_s: Optional[int] = None,
    ) -> EigenSubmitResponse:
        """Synchronous wrapper for submit_job."""
        return asyncio.run(self.submit_job(task, timeout_s))

    def get_status_sync(
        self,
        job_id: str,
        timeout_s: Optional[int] = None,
    ) -> EigenStatusResponse:
        """Synchronous wrapper for get_status."""
        return asyncio.run(self.get_status(job_id, timeout_s))

    def get_result_sync(
        self,
        job_id: str,
        timeout_s: Optional[int] = None,
    ) -> EigenResultResponse:
        """Synchronous wrapper for get_result."""
        return asyncio.run(self.get_result(job_id, timeout_s))

    def cancel_job_sync(
        self,
        job_id: str,
        timeout_s: Optional[int] = None,
    ) -> EigenCancelResponse:
        """Synchronous wrapper for cancel_job."""
        return asyncio.run(self.cancel_job(job_id, timeout_s))

    def list_models_sync(self, timeout_s: Optional[int] = None) -> List[Dict[str, Any]]:
        """Synchronous wrapper for list_models."""
        return asyncio.run(self.list_models(timeout_s))

