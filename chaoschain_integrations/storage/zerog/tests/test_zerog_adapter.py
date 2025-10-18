"""Unit tests for ZeroG storage adapter."""

import pytest
from unittest.mock import MagicMock, patch

from chaoschain_integrations.storage.zerog.adapter import ZeroGStorageAdapter
from chaoschain_integrations.storage.zerog.schemas import (
    ZeroGPutResponse,
    ZeroGGetResponse,
    ZeroGExistsResponse,
    ZeroGProofResponse,
)
from chaoschain_integrations.storage.tests.test_contract_storage import (
    run_storage_contract_tests,
)


@pytest.fixture
def mock_zerog_client():
    """Create mock ZeroG client."""
    with patch("chaoschain_integrations.storage.zerog.adapter.ZeroGStorageClient") as mock:
        client = MagicMock()

        # Mock put response
        client.put.return_value = ZeroGPutResponse(
            file_id="zerog_abc123",
            root_hash="0xdef456",
            merkle_proof={"layers": [], "indices": []},
            size_bytes=1024,
            timestamp=1234567890,
        )

        # Mock get response
        client.get.return_value = ZeroGGetResponse(
            content=b"test content",
            metadata={},
            size_bytes=1024,
        )

        # Mock exists response
        client.exists.return_value = ZeroGExistsResponse(
            exists=True,
            size_bytes=1024,
        )

        # Mock get_proof response
        client.get_proof.return_value = ZeroGProofResponse(
            file_id="zerog_abc123",
            root_hash="0xdef456",
            merkle_proof={"layers": [], "indices": []},
            timestamp=1234567890,
        )

        mock.return_value = client
        yield client


@pytest.mark.unit
def test_zerog_adapter_put(mock_zerog_client):
    """Test put operation."""
    adapter = ZeroGStorageAdapter()
    content = b"test content"

    result = adapter.put(content)

    assert result.uri == "zerog://zerog_abc123"
    assert result.proof.method == "merkle-proof"
    assert result.proof.content_hash == "0xdef456"
    assert "zerog://" in result.uri
    mock_zerog_client.put.assert_called_once()


@pytest.mark.unit
def test_zerog_adapter_get(mock_zerog_client):
    """Test get operation."""
    adapter = ZeroGStorageAdapter()
    uri = "zerog://zerog_abc123"

    content = adapter.get(uri)

    assert content == b"test content"
    mock_zerog_client.get.assert_called_once_with("zerog_abc123", timeout_s=60)


@pytest.mark.unit
def test_zerog_adapter_exists(mock_zerog_client):
    """Test exists check."""
    adapter = ZeroGStorageAdapter()
    uri = "zerog://zerog_abc123"

    exists = adapter.exists(uri)

    assert exists is True
    mock_zerog_client.exists.assert_called_once()


@pytest.mark.unit
def test_zerog_adapter_get_proof(mock_zerog_client):
    """Test get_proof operation."""
    adapter = ZeroGStorageAdapter()
    uri = "zerog://zerog_abc123"

    proof = adapter.get_proof(uri)

    assert proof.method == "merkle-proof"
    assert proof.content_hash == "0xdef456"
    mock_zerog_client.get_proof.assert_called_once()


@pytest.mark.unit
def test_zerog_extract_file_id():
    """Test URI parsing."""
    adapter = ZeroGStorageAdapter()

    # Test zerog:// scheme
    file_id = adapter._extract_file_id("zerog://file123")
    assert file_id == "file123"

    # Test 0g:// scheme
    file_id = adapter._extract_file_id("0g://file456")
    assert file_id == "file456"

    # Test raw file ID
    file_id = adapter._extract_file_id("file789")
    assert file_id == "file789"


@pytest.mark.contract
def test_zerog_adapter_contract(mock_zerog_client):
    """Test ZeroG adapter conforms to StorageBackend contract."""
    adapter = ZeroGStorageAdapter()
    run_storage_contract_tests(adapter)

