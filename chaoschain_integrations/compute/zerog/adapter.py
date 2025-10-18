"""ZeroG compute adapter implementing ComputeBackend protocol."""

import time
from typing import Any, Dict, Optional

from chaoschain_integrations.common.logging import get_logger
from chaoschain_integrations.compute.base import (
    ComputeBackend,
    ComputeProof,
    ComputeResult,
)
from chaoschain_integrations.compute.zerog.client import ZeroGComputeClient

logger = get_logger(__name__)


class ZeroGComputeAdapter(ComputeBackend):
    """
    ZeroG compute adapter for ChaosChain SDK.

    This adapter implements the ComputeBackend protocol using ZeroG's
    decentralized compute network with TEE verification.
    """

    def __init__(
        self,
        *,
        grpc_url: Optional[str] = None,
        api_key: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
    ) -> None:
        """
        Initialize ZeroG compute adapter.

        Args:
            grpc_url: ZeroG sidecar gRPC endpoint
            api_key: Optional API key
            timeout_seconds: Default timeout for operations
        """
        self.client = ZeroGComputeClient(
            grpc_url=grpc_url,
            api_key=api_key,
            timeout_seconds=timeout_seconds,
        )
        self.default_timeout = timeout_seconds or 300
        logger.info("zerog_compute_adapter_initialized")

    def submit(self, task: Dict[str, Any]) -> str:
        """Submit compute job to ZeroG."""
        logger.info("zerog_compute_submit_start", task_type=task.get("task_type"))

        response = self.client.submit_job(task)

        logger.info("zerog_compute_submit_success", job_id=response.job_id)

        return response.job_id

    def status(self, job_id: str) -> Dict[str, Any]:
        """Get job status."""
        logger.info("zerog_compute_status_check", job_id=job_id)

        response = self.client.get_status(job_id)

        status_dict = {
            "job_id": response.job_id,
            "status": response.status,
            "progress": response.progress,
            "message": response.message,
            "updated_at": response.updated_at,
        }

        logger.info(
            "zerog_compute_status_result",
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
        logger.info("zerog_compute_result_start", job_id=job_id, wait=wait)

        timeout = timeout_s or self.default_timeout

        # Poll for completion if wait=True
        if wait:
            start_time = time.time()
            while time.time() - start_time < timeout:
                status = self.client.get_status(job_id)
                if status.status in ("completed", "failed"):
                    break
                time.sleep(1.0)

        # Fetch result
        response = self.client.get_result(job_id)

        # Build proof from attestation and metadata
        proof = ComputeProof(
            method="tee-ml",
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
            "zerog_compute_result_success",
            job_id=job_id,
            status=response.status,
        )

        return result

    def cancel(self, job_id: str) -> bool:
        """Cancel job."""
        logger.info("zerog_compute_cancel", job_id=job_id)

        response = self.client.cancel_job(job_id)

        logger.info(
            "zerog_compute_cancel_result",
            job_id=job_id,
            cancelled=response.cancelled,
        )

        return response.cancelled

