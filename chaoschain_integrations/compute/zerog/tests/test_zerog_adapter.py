"""Unit tests for ZeroG compute adapter."""

import pytest
from unittest.mock import MagicMock, patch

from chaoschain_integrations.compute.zerog.adapter import ZeroGComputeAdapter
from chaoschain_integrations.compute.zerog.schemas import (
    ZeroGSubmitResponse,
    ZeroGStatusResponse,
    ZeroGResultResponse,
    ZeroGCancelResponse,
)
from chaoschain_integrations.compute.tests.test_contract_compute import (
    run_compute_contract_tests,
)


@pytest.fixture
def mock_zerog_client():
    """Create mock ZeroG compute client."""
    with patch("chaoschain_integrations.compute.zerog.adapter.ZeroGComputeClient") as mock:
        client = MagicMock()

        # Mock submit
        client.submit_job.return_value = ZeroGSubmitResponse(
            job_id="zerog_job_123",
            status="pending",
            submitted_at=1234567890,
        )

        # Mock status
        client.get_status.return_value = ZeroGStatusResponse(
            job_id="zerog_job_123",
            status="completed",
            progress=100.0,
            message="Job completed",
            updated_at=1234567890,
        )

        # Mock result
        client.get_result.return_value = ZeroGResultResponse(
            job_id="zerog_job_123",
            status="completed",
            output={"result": "test_output", "score": 0.95},
            attestation={"tee_report": "mock_report", "quote": "mock_quote"},
            metadata={
                "docker_digest": "sha256:abc123",
                "enclave_pubkey": "0xpubkey",
                "execution_hash": "0xexechash",
                "signed_result": "0xsignature",
            },
            completed_at=1234567890,
        )

        # Mock cancel
        client.cancel_job.return_value = ZeroGCancelResponse(
            job_id="zerog_job_123",
            cancelled=True,
            message="Job cancelled",
        )

        mock.return_value = client
        yield client


@pytest.mark.unit
def test_zerog_compute_submit(mock_zerog_client):
    """Test job submission."""
    adapter = ZeroGComputeAdapter()
    task = {"task_type": "inference", "inputs": {"prompt": "test"}}

    job_id = adapter.submit(task)

    assert job_id == "zerog_job_123"
    mock_zerog_client.submit_job.assert_called_once()


@pytest.mark.unit
def test_zerog_compute_status(mock_zerog_client):
    """Test status check."""
    adapter = ZeroGComputeAdapter()
    job_id = "zerog_job_123"

    status = adapter.status(job_id)

    assert status["status"] == "completed"
    assert status["progress"] == 100.0
    mock_zerog_client.get_status.assert_called_once()


@pytest.mark.unit
def test_zerog_compute_result(mock_zerog_client):
    """Test result retrieval."""
    adapter = ZeroGComputeAdapter()
    job_id = "zerog_job_123"

    result = adapter.result(job_id, wait=False)

    assert result.output["result"] == "test_output"
    assert result.proof.method == "tee-ml"
    assert result.proof.docker_digest == "sha256:abc123"
    assert result.proof.enclave_pubkey == "0xpubkey"
    mock_zerog_client.get_result.assert_called_once()


@pytest.mark.unit
def test_zerog_compute_cancel(mock_zerog_client):
    """Test job cancellation."""
    adapter = ZeroGComputeAdapter()
    job_id = "zerog_job_123"

    cancelled = adapter.cancel(job_id)

    assert cancelled is True
    mock_zerog_client.cancel_job.assert_called_once()


@pytest.mark.contract
def test_zerog_compute_adapter_contract(mock_zerog_client):
    """Test ZeroG compute adapter conforms to ComputeBackend contract."""
    adapter = ZeroGComputeAdapter()
    run_compute_contract_tests(adapter)

