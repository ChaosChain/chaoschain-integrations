# ChaosChain Integrations

Partner adapters for [ChaosChain SDK](https://github.com/ChaosChain/chaoschain) - enabling decentralized storage, compute, and attestation services.

[![CI](https://github.com/ChaosChain/chaoschain-integrations/actions/workflows/ci.yml/badge.svg)](https://github.com/ChaosChain/chaoschain-integrations/actions)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This repository contains **adapters** (plugins) that integrate partner services with the ChaosChain SDK. Each adapter implements a standard protocol (`StorageBackend`, `ComputeBackend`, `AttestationBackend`) allowing seamless swapping of providers.

### Supported Integrations

| Category | Provider | Status | Install |
|----------|----------|--------|---------|
| **Storage** | ZeroG (0G) | Alpha | `[zerog]` |
| **Storage** | IPFS (Pinata) | Alpha | `[pinata]` |
| **Compute** | ZeroG (0G) | Alpha | `[zerog]` |
| **Compute** | Eigen | Alpha | `[eigen]` |
| **Attestation** | Chainlink CRE | Stub | `[cre]` |

## Installation

### Base Install

```bash
pip install chaoschain-integrations
```

### With Specific Adapters

```bash
# Install with ZeroG support (storage + compute)
pip install chaoschain-integrations[zerog]

# Install with Eigen compute support
pip install chaoschain-integrations[eigen]

# Install with Pinata IPFS support
pip install chaoschain-integrations[pinata]

# Install with Chainlink CRE support
pip install chaoschain-integrations[cre]

# Install all adapters
pip install chaoschain-integrations[all]

# Install with dev tools
pip install chaoschain-integrations[dev]
```

## Quick Start

### Storage: ZeroG Example

```python
from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig
from chaoschain_integrations.storage.zerog import ZeroGStorageAdapter

# Initialize ZeroG storage adapter
storage = ZeroGStorageAdapter(
    grpc_url="localhost:50051",
    api_key="your_api_key",
)

# Use with ChaosChain SDK
sdk = ChaosChainAgentSDK(
    agent_name="MyAgent",
    agent_domain="example.com",
    agent_role="server",
    network=NetworkConfig.ETHEREUM_SEPOLIA,
    storage_provider=storage,  # Inject adapter
)

# Store evidence
content = b"Important evidence data"
result = storage.put(content)
print(f"Stored at: {result.uri}")
print(f"Proof: {result.proof.content_hash}")

# Retrieve evidence
retrieved = storage.get(result.uri)
assert retrieved == content
```

### Storage: Pinata IPFS Example

```python
from chaoschain_integrations.storage.ipfs_pinata import PinataStorageAdapter

# Initialize with JWT
storage = PinataStorageAdapter(jwt="your_pinata_jwt")

# Store to IPFS
result = storage.put(
    b"Hello IPFS!",
    metadata={"name": "greeting.txt"}
)
print(f"IPFS CID: {result.proof.content_hash}")
print(f"Gateway URLs: {result.alternative_uris}")
```

### Compute: Eigen Example

```python
from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig
from chaoschain_integrations.compute.eigen import EigenComputeAdapter

# Initialize Eigen compute adapter
compute = EigenComputeAdapter(
    api_url="http://localhost:8082",
    api_key="your_api_key",
    use_grpc=True,
)

# Use with ChaosChain SDK
sdk = ChaosChainAgentSDK(
    agent_name="EigenAgent",
    agent_domain="example.com",
    agent_role="server",
    network=NetworkConfig.ETHEREUM_SEPOLIA,
    compute_provider=compute,  # Inject adapter
    enable_process_integrity=True,
)

# Submit ML inference job
task = {
    "task": "inference",
    "model": "llama-3-70b",
    "prompt": "Explain blockchain in simple terms",
    "verification": "tee-ml",
}

job_id = compute.submit(task)
result = compute.result(job_id, wait=True, timeout_s=600)

print(f"Output: {result.output}")
print(f"TEE Attestation: {result.proof.attestation}")
print(f"Enclave Key: {result.proof.enclave_pubkey}")
```

### Switching Providers

Adapters are **pluggable** - swap providers without changing your application code:

```python
# Use ZeroG storage
from chaoschain_integrations.storage.zerog import ZeroGStorageAdapter
storage = ZeroGStorageAdapter(grpc_url="localhost:50051")

# Or use Pinata IPFS
from chaoschain_integrations.storage.ipfs_pinata import PinataStorageAdapter
storage = PinataStorageAdapter(jwt="your_jwt")

# Your SDK code remains the same!
sdk = ChaosChainAgentSDK(..., storage_provider=storage)
```

## Configuration

All adapters support environment-based configuration via `.env` files:

```bash
# ZeroG
ZEROG_GRPC_URL=localhost:50051
ZEROG_API_KEY=your_key
ZEROG_TIMEOUT_SECONDS=60

# Eigen
EIGEN_API_URL=http://localhost:8082
EIGEN_API_KEY=your_key
EIGEN_USE_GRPC=true
EIGEN_TIMEOUT_SECONDS=600

# Pinata
PINATA_JWT=your_jwt_token
PINATA_TIMEOUT_SECONDS=60

# Chainlink CRE
CRE_API_URL=https://cre-api.chainlink.com
CRE_API_KEY=your_key
CRE_TIMEOUT_SECONDS=30

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
```

See [`.env.example`](.env.example) for complete configuration options.

## Architecture

```
┌─────────────────────────────────────┐
│      ChaosChain Agent SDK           │
│   (chaoschain-sdk)                  │
└──────────┬──────────────────────────┘
           │
           │ Protocol Interfaces:
           │ - StorageBackend
           │ - ComputeBackend
           │ - AttestationBackend
           │
┌──────────▼──────────────────────────┐
│  ChaosChain Integrations (THIS)     │
│  ┌────────────┐  ┌────────────┐    │
│  │  Storage   │  │  Compute   │    │
│  │  Adapters  │  │  Adapters  │    │
│  ├────────────┤  ├────────────┤    │
│  │ • ZeroG    │  │ • ZeroG    │    │
│  │ • Pinata   │  │ • Eigen    │    │
│  └────────────┘  └────────────┘    │
│  ┌────────────┐                     │
│  │Attestation │                     │
│  ├────────────┤                     │
│  │ • CRE      │                     │
│  └────────────┘                     │
└──────────┬──────────────────────────┘
           │
           │ gRPC/HTTP/Native SDKs
           │
┌──────────▼──────────────────────────┐
│    Partner Services                 │
│  • 0G Network                       │
│  • Eigen                            │
│  • Pinata / IPFS                    │
│  • Chainlink                        │
└─────────────────────────────────────┘
```

## Sidecars

Some adapters use **sidecar services** (Go/Rust) to interface with native SDKs:

### ZeroG Sidecar (gRPC)

```bash
cd sidecars/zerog/go
make build
./bin/zerog-storage-bridge --port 50051
./bin/zerog-compute-bridge --port 50052
```

### Eigen Sidecar (gRPC)

```bash
cd sidecars/eigen/go
make build
./bin/eigen-compute-bridge --port 50053
```

See [`sidecars/` documentation](sidecars/) for details.

## Development

### Setup

```bash
# Clone repository
git clone https://github.com/ChaosChain/chaoschain-integrations.git
cd chaoschain-integrations

# Create virtual environment
make venv
source venv/bin/activate

# Install with dev dependencies
make install-dev
```

### Testing

```bash
# Run all tests
make test

# Run unit tests only
make test-unit

# Run contract tests
make test-contract

# Run with coverage
make test-cov
```

### Code Quality

```bash
# Format code
make fmt

# Lint code
make lint

# Type check
make typecheck
```

### Building

```bash
# Build distribution packages
make build

# Publish to PyPI (requires credentials)
make publish
```

## Documentation

- [Architecture & Design](docs/architecture.md)
- [Adding New Adapters](CONTRIBUTING.md)
- [ZeroG Storage Adapter](chaoschain_integrations/storage/zerog/README.md)
- [Pinata Storage Adapter](chaoschain_integrations/storage/ipfs_pinata/README.md)
- [ZeroG Compute Adapter](chaoschain_integrations/compute/zerog/README.md)
- [Eigen Compute Adapter](chaoschain_integrations/compute/eigen/README.md)
- [Chainlink CRE Adapter](chaoschain_integrations/attest/chainlink_cre/README.md)

## Compatibility Matrix

| Integration Version | ChaosChain SDK | Python | Status |
|---------------------|----------------|--------|--------|
| 0.1.0 | >=0.2.0 | 3.9-3.12 | Alpha |

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Adding a New Adapter

1. Create adapter module: `chaoschain_integrations/<category>/<provider>/`
2. Implement protocol: `StorageBackend`, `ComputeBackend`, or `AttestationBackend`
3. Add tests (unit + contract tests)
4. Update `pyproject.toml` with optional dependencies
5. Submit PR

## Support

- **Issues**: [GitHub Issues](https://github.com/ChaosChain/chaoschain-integrations/issues)
- **Discussions**: [GitHub Discussions](https://github.com/ChaosChain/chaoschain-integrations/discussions)
- **Documentation**: [docs.chaoschain.io](https://docs.chaoschain.io)

## License

[MIT License](LICENSE)

## Acknowledgments

- [0G Labs](https://0g.ai/) - Decentralized storage and compute
- [EigenLayer](https://www.eigenlayer.xyz/) - Restaking and compute
- [Pinata](https://pinata.cloud/) - IPFS pinning services
- [Chainlink](https://chain.link/) - Decentralized oracle network

---

Built with ❤️ by the [ChaosChain Labs](https://chaoschain.io) team