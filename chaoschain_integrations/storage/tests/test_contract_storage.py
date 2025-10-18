"""
Contract tests for StorageBackend protocol.

All storage adapters must pass these tests to ensure they
correctly implement the StorageBackend interface.
"""

import pytest

from chaoschain_integrations.storage.base import StorageBackend, StorageResult


def run_storage_contract_tests(backend: StorageBackend) -> None:
    """
    Run contract tests for any StorageBackend implementation.

    Args:
        backend: Storage adapter to test
    """
    # Test 1: put() returns StorageResult with required fields
    content = b"test content"
    result = backend.put(content, timeout_s=30)

    assert isinstance(result, StorageResult)
    assert result.uri, "URI must be non-empty"
    assert result.proof, "Proof must be present"
    assert result.proof.method in [
        "ipfs-cid",
        "merkle-proof",
        "keccak-256",
        "signature",
    ], f"Invalid proof method: {result.proof.method}"
    assert result.proof.content_hash, "Content hash must be present"

    # Test 2: exists() returns bool
    exists = backend.exists(result.uri, timeout_s=30)
    assert isinstance(exists, bool)

    # Test 3: get_proof() returns proof for existing content
    proof = backend.get_proof(result.uri, timeout_s=30)
    assert proof.method == result.proof.method
    assert proof.content_hash == result.proof.content_hash


@pytest.mark.contract
def test_dummy_storage_backend_contract() -> None:
    """Test contract with a dummy implementation."""

    class DummyStorageBackend:
        def put(self, content: bytes, *, metadata=None, timeout_s: int = 60):
            from chaoschain_integrations.storage.base import StorageProof, StorageResult

            return StorageResult(
                uri="dummy://test",
                proof=StorageProof(
                    method="keccak-256",
                    content_hash="0xabc123",
                    metadata={},
                ),
            )

        def get(self, uri: str, *, timeout_s: int = 60) -> bytes:
            return b"test content"

        def exists(self, uri: str, *, timeout_s: int = 30) -> bool:
            return True

        def get_proof(self, uri: str, *, timeout_s: int = 30):
            from chaoschain_integrations.storage.base import StorageProof

            return StorageProof(
                method="keccak-256",
                content_hash="0xabc123",
                metadata={},
            )

    backend = DummyStorageBackend()
    run_storage_contract_tests(backend)

