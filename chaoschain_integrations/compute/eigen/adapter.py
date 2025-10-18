"""Eigen compute adapter implementing ComputeBackend protocol."""

import time
from typing import Any, Dict, Optional

from chaoschain_integrations.common.logging import get_logger
from chaoschain_integrations.compute.base import (
    ComputeBackend,
    ComputeProof,
    ComputeResult,
)
from chaoschain_integrations.compute.eigen.client import EigenComputeClient

logger = get_logger(__name__)


class EigenComputeAdapter(ComputeBackend):
    """
    Eigen compute adapter for ChaosChain SDK.

    This adapter implements the ComputeBackend protocol using Eigen's
    TEE-based ML inference service.
    """

    def __init__(
        self,
        *,
        api_url: Optional[str] = None,
        api_key: Optional[str] = None,
        use_grpc: bool = True,
        timeout_seconds: Optional[int] = None,
    ) -> None:
        """
        Initialize Eigen compute adapter.

        Args:
            api_url: Eigen API endpoint
            api_key: Optional API key
            use_grpc: Use gRPC instead of HTTP
            timeout_seconds: Default timeout for operations
        """
        self.client = EigenComputeClient(
            api_url=api_url,
            api_key=api_key,
            use_grpc=use_grpc,
            timeout_seconds=timeout_seconds,
        )
        self.default_timeout = timeout_seconds or 600
        logger.info("eigen_compute_adapter_initialized")

    def submit(self, task: Dict[str, Any]) -> str:
        """Submit compute job to Eigen."""
        logger.info("eigen_compute_submit_start", task=task.get("task"))

        response = self.client.submit_job_sync(task)

        logger.info("eigen_compute_submit_success", job_id=response.job_id)

        return response.job_id

    def status(self, job_id: str) -> Dict[str, Any]:
        """Get job status."""
        logger.info("eigen_compute_status_check", job_id=job_id)

        response = self.client.get_status_sync(job_id)

        status_dict = {
            "job_id": response.job_id,
            "status": response.status,
            "progress": response.progress,
            "error": response.error,
            "updated_at": response.updated_at,
        }

        logger.info(
            "eigen_compute_status_result",
            job_id=job_id,
            status=response.status,
        )

        return status_dict

    def result(
        self,
        job_id: str,
        *,
        wait: bool = True,
        timeout_s: int = 300,
    ) -> ComputeResult:
        """Get job result with proof."""
        logger.info("eigen_compute_result_start", job_id=job_id, wait=wait)

        timeout = timeout_s or self.default_timeout

        # Poll for completion if wait=True
        if wait:
            start_time = time.time()
            while time.time() - start_time < timeout:
                status = self.client.get_status_sync(job_id)
                if status.status in ("completed", "failed"):
                    break
                time.sleep(1.0)

        # Fetch result
        response = self.client.get_result_sync(job_id)

        # Build proof from attestation and metadata
        proof = ComputeProof(
            method=response.metadata.get("verification_method", "tee-ml"),
            docker_digest=response.metadata.get("docker_digest"),
            enclave_pubkey=response.metadata.get("enclave_pubkey"),
            attestation=response.attestation,
            execution_hash=response.metadata.get("execution_hash"),
            signature=response.metadata.get("signed_result"),
            timestamp=response.completed_at,
            metadata=response.metadata,
        )

        result = ComputeResult(
            output=response.output,
            proof=proof,
            raw=response.model_dump(),
            job_id=job_id,
        )

        logger.info(
            "eigen_compute_result_success",
            job_id=job_id,
            status=response.status,
        )

        return result

    def cancel(self, job_id: str) -> bool:
        """Cancel job."""
        logger.info("eigen_compute_cancel", job_id=job_id)

        response = self.client.cancel_job_sync(job_id)

        logger.info(
            "eigen_compute_cancel_result",
            job_id=job_id,
            cancelled=response.cancelled,
        )

        return response.cancelled

