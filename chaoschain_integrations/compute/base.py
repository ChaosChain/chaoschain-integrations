"""
Base Protocol for Compute adapters.

This mirrors the ComputeBackend interface from chaoschain-sdk to maintain
loose coupling between the SDK and integrations.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol


@dataclass
class ComputeProof:
    """Proof/attestation for compute operation."""

    method: str  # e.g., "tee-ml", "zk-ml", "op-ml"
    docker_digest: Optional[str] = None  # Image identity
    enclave_pubkey: Optional[str] = None  # TEE public key
    attestation: Optional[Dict[str, Any]] = None  # Raw attestation data
    execution_hash: Optional[str] = None  # Hash of inputs/code
    signature: Optional[str] = None  # Signature by enclave/verifier
    timestamp: Optional[int] = None  # Execution timestamp
    metadata: Optional[Dict[str, Any]] = None  # Additional proof data


@dataclass
class ComputeResult:
    """Result from compute operation."""

    output: Any  # Computation result (can be dict, list, str, etc.)
    proof: ComputeProof
    raw: Optional[Dict[str, Any]] = None  # Original response from backend
    job_id: Optional[str] = None  # Job identifier for tracking


class ComputeBackend(Protocol):
    """
    Protocol for compute adapter implementations.

    All compute adapters must implement these methods to be compatible
    with ChaosChainAgentSDK.
    """

    def submit(self, task: Dict[str, Any]) -> str:
        """
        Submit a compute job.

        Args:
            task: Task specification (format depends on backend)
                  Common fields: model, prompt, inputs, verification, etc.

        Returns:
            Job ID for tracking

        Raises:
            ValidationError: If task format is invalid
            ConnectionError: If backend connection fails
        """
        ...

    def status(self, job_id: str) -> Dict[str, Any]:
        """
        Get job status.

        Args:
            job_id: Job identifier

        Returns:
            Status dict with at least 'status' field
            (e.g., pending, running, completed, failed)

        Raises:
            ResourceNotFoundError: If job not found
            ConnectionError: If backend connection fails
        """
        ...

    def result(
        self,
        job_id: str,
        *,
        wait: bool = True,
        timeout_s: int = 300,
    ) -> ComputeResult:
        """
        Get job result.

        Args:
            job_id: Job identifier
            wait: If True, poll until completion
            timeout_s: Maximum wait time in seconds

        Returns:
            ComputeResult with output and proof

        Raises:
            ResourceNotFoundError: If job not found
            TimeoutError: If wait exceeds timeout
            ConnectionError: If backend connection fails
        """
        ...

    def cancel(self, job_id: str) -> bool:
        """
        Cancel a running job.

        Args:
            job_id: Job identifier

        Returns:
            True if cancelled, False if already completed/failed

        Raises:
            ResourceNotFoundError: If job not found
            ConnectionError: If backend connection fails
        """
        ...

