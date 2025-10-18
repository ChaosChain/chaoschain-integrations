"""Unit tests for Eigen compute adapter."""

import pytest
from unittest.mock import MagicMock, patch

from chaoschain_integrations.compute.eigen.adapter import EigenComputeAdapter
from chaoschain_integrations.compute.eigen.schemas import (
    EigenSubmitResponse,
    EigenStatusResponse,
    EigenResultResponse,
    EigenCancelResponse,
)
from chaoschain_integrations.compute.tests.test_contract_compute import (
    run_compute_contract_tests,
)


@pytest.fixture
def mock_eigen_client():
    """Create mock Eigen compute client."""
    with patch("chaoschain_integrations.compute.eigen.adapter.EigenComputeClient") as mock:
        client = MagicMock()

        # Mock submit
        client.submit_job_sync.return_value = EigenSubmitResponse(
            job_id="eigen_job_456",
            status="pending",
            created_at=1234567890,
        )

        # Mock status
        client.get_status_sync.return_value = EigenStatusResponse(
            job_id="eigen_job_456",
            status="completed",
            progress=100,
            error=None,
            updated_at=1234567890,
        )

        # Mock result
        client.get_result_sync.return_value = EigenResultResponse(
            job_id="eigen_job_456",
            status="completed",
            output={"answer": "hi", "confidence": 0.98},
            attestation={"quote": "mock_quote", "report": "mock_report"},
            metadata={
                "docker_digest": "sha256:def456",
                "enclave_pubkey": "0xeigenkey",
                "execution_hash": "0xeigenhash",
                "signed_result": "0xeigensig",
                "verification_method": "tee-ml",
            },
            completed_at=1234567890,
        )

        # Mock cancel
        client.cancel_job_sync.return_value = EigenCancelResponse(
            job_id="eigen_job_456",
            cancelled=True,
            message="Job cancelled",
        )

        mock.return_value = client
        yield client


@pytest.mark.unit
def test_eigen_compute_submit(mock_eigen_client):
    """Test job submission."""
    adapter = EigenComputeAdapter()
    task = {"task": "inference", "prompt": "test"}

    job_id = adapter.submit(task)

    assert job_id == "eigen_job_456"
    mock_eigen_client.submit_job_sync.assert_called_once()


@pytest.mark.unit
def test_eigen_compute_status(mock_eigen_client):
    """Test status check."""
    adapter = EigenComputeAdapter()
    job_id = "eigen_job_456"

    status = adapter.status(job_id)

    assert status["status"] == "completed"
    assert status["progress"] == 100
    mock_eigen_client.get_status_sync.assert_called_once()


@pytest.mark.unit
def test_eigen_compute_result(mock_eigen_client):
    """Test result retrieval."""
    adapter = EigenComputeAdapter()
    job_id = "eigen_job_456"

    result = adapter.result(job_id, wait=False)

    assert result.output["answer"] == "hi"
    assert result.proof.method == "tee-ml"
    assert result.proof.docker_digest == "sha256:def456"
    assert result.proof.enclave_pubkey == "0xeigenkey"
    mock_eigen_client.get_result_sync.assert_called_once()


@pytest.mark.unit
def test_eigen_compute_cancel(mock_eigen_client):
    """Test job cancellation."""
    adapter = EigenComputeAdapter()
    job_id = "eigen_job_456"

    cancelled = adapter.cancel(job_id)

    assert cancelled is True
    mock_eigen_client.cancel_job_sync.assert_called_once()


@pytest.mark.contract
def test_eigen_compute_adapter_contract(mock_eigen_client):
    """Test Eigen compute adapter conforms to ComputeBackend contract."""
    adapter = EigenComputeAdapter()
    run_compute_contract_tests(adapter)

