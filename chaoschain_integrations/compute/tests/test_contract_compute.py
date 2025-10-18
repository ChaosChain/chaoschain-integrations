"""
Contract tests for ComputeBackend protocol.

All compute adapters must pass these tests to ensure they
correctly implement the ComputeBackend interface.
"""

import pytest

from chaoschain_integrations.compute.base import ComputeBackend, ComputeResult


def run_compute_contract_tests(backend: ComputeBackend) -> None:
    """
    Run contract tests for any ComputeBackend implementation.

    Args:
        backend: Compute adapter to test
    """
    # Test 1: submit() returns job_id string
    task = {"task": "test", "inputs": {"data": "test"}}
    job_id = backend.submit(task)

    assert isinstance(job_id, str)
    assert len(job_id) > 0

    # Test 2: status() returns dict with status field
    status = backend.status(job_id)

    assert isinstance(status, dict)
    assert "status" in status
    assert status["status"] in ["pending", "running", "completed", "failed"]

    # Test 3: result() returns ComputeResult with proof
    result = backend.result(job_id, wait=False)

    assert isinstance(result, ComputeResult)
    assert result.output is not None
    assert result.proof is not None
    assert result.proof.method in ["tee-ml", "zk-ml", "op-ml"]

    # Test 4: cancel() returns bool
    cancelled = backend.cancel(job_id)
    assert isinstance(cancelled, bool)


@pytest.mark.contract
def test_dummy_compute_backend_contract() -> None:
    """Test contract with a dummy implementation."""

    class DummyComputeBackend:
        def submit(self, task):
            return "job-123"

        def status(self, job_id):
            return {"status": "completed", "progress": 100}

        def result(self, job_id, *, wait=True, timeout_s=300):
            from chaoschain_integrations.compute.base import ComputeProof, ComputeResult

            return ComputeResult(
                output={"result": "test"},
                proof=ComputeProof(
                    method="tee-ml",
                    docker_digest="sha256:abc",
                    enclave_pubkey="0xpub",
                    attestation={},
                    execution_hash="0xexec",
                    signature="0xsig",
                ),
                job_id=job_id,
            )

        def cancel(self, job_id):
            return True

    backend = DummyComputeBackend()
    run_compute_contract_tests(backend)

