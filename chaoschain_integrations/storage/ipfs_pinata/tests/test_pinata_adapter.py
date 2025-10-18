"""Unit tests for Pinata storage adapter."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from chaoschain_integrations.storage.ipfs_pinata.adapter import PinataStorageAdapter
from chaoschain_integrations.storage.ipfs_pinata.schemas import PinFileResponse
from chaoschain_integrations.storage.tests.test_contract_storage import (
    run_storage_contract_tests,
)


@pytest.fixture
def mock_pinata_client():
    """Create mock Pinata client."""
    with patch("chaoschain_integrations.storage.ipfs_pinata.adapter.PinataClient") as mock:
        client = MagicMock()

        # Mock async pin_file
        async def mock_pin_file(*args, **kwargs):
            return PinFileResponse(
                IpfsHash="QmTest123456",
                PinSize=1024,
                Timestamp="2024-01-01T00:00:00Z",
                isDuplicate=False,
            )

        client.pin_file = AsyncMock(side_effect=mock_pin_file)

        # Mock async get_file
        async def mock_get_file(*args, **kwargs):
            return b"test content"

        client.get_file = AsyncMock(side_effect=mock_get_file)

        # Mock async pin_exists
        async def mock_pin_exists(*args, **kwargs):
            return True

        client.pin_exists = AsyncMock(side_effect=mock_pin_exists)

        mock.return_value = client
        yield client


@pytest.mark.unit
def test_pinata_adapter_put(mock_pinata_client):
    """Test put operation."""
    adapter = PinataStorageAdapter(jwt="test_jwt")
    content = b"test content"

    result = adapter.put(content)

    assert result.uri == "ipfs://QmTest123456"
    assert result.proof.method == "ipfs-cid"
    assert result.proof.content_hash == "QmTest123456"
    assert len(result.alternative_uris) == 3
    mock_pinata_client.pin_file.assert_called_once()


@pytest.mark.unit
def test_pinata_adapter_get(mock_pinata_client):
    """Test get operation."""
    adapter = PinataStorageAdapter(jwt="test_jwt")
    uri = "ipfs://QmTest123456"

    content = adapter.get(uri)

    assert content == b"test content"
    mock_pinata_client.get_file.assert_called_once()


@pytest.mark.unit
def test_pinata_adapter_exists(mock_pinata_client):
    """Test exists check."""
    adapter = PinataStorageAdapter(jwt="test_jwt")
    uri = "ipfs://QmTest123456"

    exists = adapter.exists(uri)

    assert exists is True
    mock_pinata_client.pin_exists.assert_called_once()


@pytest.mark.unit
def test_pinata_adapter_get_proof(mock_pinata_client):
    """Test get_proof operation."""
    adapter = PinataStorageAdapter(jwt="test_jwt")
    uri = "ipfs://QmTest123456"

    proof = adapter.get_proof(uri)

    assert proof.method == "ipfs-cid"
    assert proof.content_hash == "QmTest123456"


@pytest.mark.unit
def test_pinata_extract_cid():
    """Test CID extraction from various URI formats."""
    adapter = PinataStorageAdapter(jwt="test_jwt")

    # Test ipfs:// scheme
    cid = adapter._extract_cid("ipfs://QmTest123")
    assert cid == "QmTest123"

    # Test gateway URL
    cid = adapter._extract_cid("https://gateway.pinata.cloud/ipfs/QmTest456/file.txt")
    assert cid == "QmTest456"

    # Test raw CID
    cid = adapter._extract_cid("QmTest789")
    assert cid == "QmTest789"


@pytest.mark.contract
def test_pinata_adapter_contract(mock_pinata_client):
    """Test Pinata adapter conforms to StorageBackend contract."""
    adapter = PinataStorageAdapter(jwt="test_jwt")
    run_storage_contract_tests(adapter)

