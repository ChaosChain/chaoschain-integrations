"""Shared type definitions for adapters."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional


class ProofMethod(str, Enum):
    """Verification method for compute/storage operations."""

    TEE_ML = "tee-ml"  # Trusted Execution Environment for ML
    ZK_ML = "zk-ml"  # Zero-Knowledge proof for ML
    OP_ML = "op-ml"  # Optimistic proof for ML
    IPFS_CID = "ipfs-cid"  # IPFS Content Identifier
    MERKLE_PROOF = "merkle-proof"  # Merkle tree proof
    SIGNATURE = "signature"  # Cryptographic signature
    ATTESTATION = "attestation"  # Generic attestation
    NONE = "none"  # No proof available


@dataclass
class Proof:
    """Generic proof structure for verification."""

    method: ProofMethod
    data: Dict[str, Any] = field(default_factory=dict)
    signature: Optional[str] = None
    timestamp: Optional[int] = None
    verifier: Optional[str] = None  # Who/what can verify this proof

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "method": self.method.value,
            "data": self.data,
            "signature": self.signature,
            "timestamp": self.timestamp,
            "verifier": self.verifier,
        }


@dataclass
class ComputeProof:
    """Proof structure for compute operations (EigenCompute, 0G, etc.)."""
    
    method: str                    # e.g., "tee-ml", "zk-ml"
    docker_digest: Optional[str] = None  # Image identity
    enclave_pubkey: Optional[str] = None  # TEE public key
    attestation: Optional[Dict[str, Any]] = None  # TEE attestation data
    execution_hash: Optional[str] = None  # Hash of execution
    signature: Optional[str] = None  # Result signature


@dataclass
class ComputeResult:
    """Result structure for compute operations."""
    
    output: Any
    proof: ComputeProof
    raw: Optional[Dict[str, Any]] = None


@dataclass
class AdapterResult:
    """Generic result wrapper for adapter operations."""

    success: bool
    data: Any
    proof: Optional[Proof] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result: Dict[str, Any] = {
            "success": self.success,
            "data": self.data,
            "metadata": self.metadata,
        }
        if self.proof:
            result["proof"] = self.proof.to_dict()
        if self.error:
            result["error"] = self.error
        return result

