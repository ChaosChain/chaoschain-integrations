"""
Base Protocol for Attestation adapters.

Attestation adapters provide verification and proof services
for compute and storage operations.
"""

from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol


@dataclass
class AttestationProof:
    """Attestation proof structure."""

    attestation_id: str  # Unique attestation identifier
    proof_type: str  # e.g., "chainlink-cre", "tee-attestation", "zk-proof"
    verified: bool  # Whether attestation passed verification
    proof_data: Dict[str, Any]  # Attestation-specific proof data
    verifier: str  # Who/what verified (e.g., "chainlink-cre", "sgx-dcap")
    timestamp: int  # Attestation timestamp
    metadata: Optional[Dict[str, Any]] = None


@dataclass
class AttestationResult:
    """Result from attestation operation."""

    success: bool
    proof: AttestationProof
    raw: Optional[Dict[str, Any]] = None  # Original response
    error: Optional[str] = None


class AttestationBackend(Protocol):
    """
    Protocol for attestation adapter implementations.

    Attestation adapters verify compute/storage integrity and
    provide proof that operations were executed correctly.
    """

    def attest(
        self,
        data: Dict[str, Any],
        *,
        proof_type: str = "default",
        timeout_s: int = 30,
    ) -> AttestationResult:
        """
        Create attestation for given data.

        Args:
            data: Data to attest (e.g., compute result, storage hash)
            proof_type: Type of proof to generate
            timeout_s: Operation timeout

        Returns:
            AttestationResult with proof

        Raises:
            ValidationError: If data format is invalid
            TimeoutError: If operation times out
            ConnectionError: If backend connection fails
        """
        ...

    def verify(
        self,
        attestation_id: str,
        *,
        expected_data: Optional[Dict[str, Any]] = None,
        timeout_s: int = 30,
    ) -> bool:
        """
        Verify an existing attestation.

        Args:
            attestation_id: Attestation identifier
            expected_data: Optional data to verify against
            timeout_s: Operation timeout

        Returns:
            True if valid, False otherwise

        Raises:
            ResourceNotFoundError: If attestation not found
            TimeoutError: If operation times out
            ConnectionError: If backend connection fails
        """
        ...

    def get_proof(
        self,
        attestation_id: str,
        *,
        timeout_s: int = 30,
    ) -> AttestationProof:
        """
        Retrieve proof for existing attestation.

        Args:
            attestation_id: Attestation identifier
            timeout_s: Operation timeout

        Returns:
            AttestationProof

        Raises:
            ResourceNotFoundError: If attestation not found
            TimeoutError: If operation times out
            ConnectionError: If backend connection fails
        """
        ...

