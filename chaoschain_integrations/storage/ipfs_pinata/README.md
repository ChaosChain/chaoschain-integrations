# Pinata (IPFS) Storage Adapter

This adapter integrates [Pinata](https://pinata.cloud/) IPFS pinning service with ChaosChain SDK.

## Features

- **Content-Addressed Storage**: Uses IPFS Content Identifiers (CIDs) for immutable content addressing
- **HTTP API**: Simple REST API integration, no sidecar required
- **Multiple Gateways**: Provides multiple URI formats for content retrieval
- **Metadata Support**: Attach custom metadata to pinned content

## Installation

```bash
pip install chaoschain-integrations[pinata]
```

## Configuration

Set these environment variables (or use `.env` file):

```bash
PINATA_API_URL=https://api.pinata.cloud  # Pinata API endpoint
PINATA_JWT=your_jwt_token                 # JWT token (recommended)
# OR use API key + secret:
PINATA_API_KEY=your_api_key
PINATA_API_SECRET=your_api_secret
PINATA_TIMEOUT_SECONDS=60
```

## Usage

```python
from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig
from chaoschain_integrations.storage.ipfs_pinata import PinataStorageAdapter

# Initialize adapter
pinata = PinataStorageAdapter(
    jwt="your_jwt_token",
    # OR: api_key="key", api_secret="secret"
)

# Use with ChaosChain SDK
sdk = ChaosChainAgentSDK(
    agent_name="MyAgent",
    agent_domain="example.com",
    agent_role="server",
    network=NetworkConfig.ETHEREUM_SEPOLIA,
    storage_provider=pinata,  # Inject Pinata adapter
)

# Store data
content = b"Hello, IPFS!"
result = pinata.put(content, metadata={"name": "greeting.txt"})
print(f"Stored at: {result.uri}")
print(f"CID: {result.proof.content_hash}")
print(f"Gateways: {result.alternative_uris}")

# Retrieve data
retrieved = pinata.get(result.uri)
assert retrieved == content

# Check existence
exists = pinata.exists(result.uri)
print(f"Pinned: {exists}")

# Get proof (CID) without fetching content
proof = pinata.get_proof(result.uri)
print(f"CID: {proof.content_hash}")
```

## Authentication

Pinata supports two authentication methods:

### JWT (Recommended)

```python
pinata = PinataStorageAdapter(jwt="your_jwt_token")
```

### API Key + Secret

```python
pinata = PinataStorageAdapter(
    api_key="your_api_key",
    api_secret="your_api_secret"
)
```

## IPFS Gateways

The adapter provides multiple URI formats for accessing content:

- `ipfs://QmXyz...` - Standard IPFS URI
- `https://gateway.pinata.cloud/ipfs/QmXyz...` - Pinata gateway
- `https://ipfs.io/ipfs/QmXyz...` - Public IPFS gateway

## Metadata

You can attach metadata to pinned content:

```python
result = pinata.put(
    content=b"data",
    metadata={
        "name": "my-file.txt",
        "keyvalues": {
            "project": "chaoschain",
            "version": "1.0"
        }
    }
)
```

## Development

Run tests:

```bash
pytest chaoschain_integrations/storage/ipfs_pinata/tests/
```

## Status

**Current Status**: Alpha

- ✅ HTTP API integration
- ✅ Pin/unpin operations
- ✅ Content retrieval via gateways
- ✅ Metadata support
- ✅ JWT and API key authentication

## References

- [Pinata Documentation](https://docs.pinata.cloud/)
- [IPFS Documentation](https://docs.ipfs.tech/)
- [Pinata API Reference](https://docs.pinata.cloud/api-pinning)

