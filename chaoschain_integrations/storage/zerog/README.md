# ZeroG Storage Adapter

This adapter integrates [0G (ZeroGravity)](https://0g.ai/) decentralized storage with ChaosChain SDK.

## Features

- **Merkle Proof Verification**: Every stored file includes a merkle proof for data integrity
- **gRPC Sidecar**: Uses a Go sidecar service to interface with the native 0G SDK
- **Environment Configuration**: All settings configurable via environment variables

## Installation

```bash
pip install chaoschain-integrations[zerog]
```

## Configuration

Set these environment variables (or use `.env` file):

```bash
ZEROG_GRPC_URL=localhost:50051  # ZeroG sidecar gRPC endpoint
ZEROG_API_KEY=your_api_key       # Optional API key
ZEROG_TIMEOUT_SECONDS=60         # Request timeout
```

## Usage

```python
from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig
from chaoschain_integrations.storage.zerog import ZeroGStorageAdapter

# Initialize adapter
zerog = ZeroGStorageAdapter(
    grpc_url="localhost:50051",
    api_key="your_api_key",
)

# Use with ChaosChain SDK
sdk = ChaosChainAgentSDK(
    agent_name="MyAgent",
    agent_domain="example.com",
    agent_role="server",
    network=NetworkConfig.ETHEREUM_SEPOLIA,
    storage_provider=zerog,  # Inject ZeroG adapter
)

# Store data
content = b"Hello, ZeroG!"
result = zerog.put(content)
print(f"Stored at: {result.uri}")
print(f"Proof: {result.proof.content_hash}")

# Retrieve data
retrieved = zerog.get(result.uri)
assert retrieved == content

# Check existence
exists = zerog.exists(result.uri)
print(f"Exists: {exists}")

# Get proof only (without fetching content)
proof = zerog.get_proof(result.uri)
print(f"Merkle root: {proof.content_hash}")
```

## Architecture

```
┌─────────────────────┐
│ ChaosChain SDK      │
└──────────┬──────────┘
           │
           │ StorageBackend Protocol
           │
┌──────────▼──────────┐
│ ZeroGStorageAdapter │  (Python)
└──────────┬──────────┘
           │
           │ gRPC
           │
┌──────────▼──────────┐
│ ZeroG Sidecar       │  (Go)
│ (sidecars/zerog/)   │
└──────────┬──────────┘
           │
           │ Native SDK
           │
┌──────────▼──────────┐
│ 0G Network          │
└─────────────────────┘
```

## Running the Sidecar

The ZeroG adapter requires a sidecar service to be running:

```bash
cd sidecars/zerog/go
make build
./bin/zerog-bridge --port 50051
```

Or use Docker:

```bash
docker run -p 50051:50051 chaoschain/zerog-bridge:latest
```

## Development

See [CONTRIBUTING.md](../../../CONTRIBUTING.md) for development guidelines.

Run tests:

```bash
pytest chaoschain_integrations/storage/zerog/tests/
```

## Status

**Current Status**: Alpha / Mock Implementation

- ✅ Protocol interface defined
- ✅ Mock client for testing
- 🔄 gRPC proto definitions (in progress)
- 🔄 Go sidecar implementation (in progress)
- ❌ Production 0G SDK integration (TODO)

## References

- [0G Documentation](https://docs.0g.ai/)
- [0G GitHub](https://github.com/0glabs)

