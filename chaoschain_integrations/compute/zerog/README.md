# ZeroG Compute Adapter

This adapter integrates [0G (ZeroGravity)](https://0g.ai/) decentralized compute with ChaosChain SDK.

## Features

- **TEE Verification**: Trusted Execution Environment attestation for compute integrity
- **Async Job Management**: Submit, poll, and retrieve results
- **gRPC Sidecar**: Uses a Go sidecar service to interface with the native 0G SDK
- **Process Integrity**: Full attestation chain for verifiable compute

## Installation

```bash
pip install chaoschain-integrations[zerog]
```

## Configuration

Set these environment variables (or use `.env` file):

```bash
ZEROG_GRPC_URL=localhost:50051  # ZeroG compute sidecar gRPC endpoint
ZEROG_API_KEY=your_api_key       # Optional API key
ZEROG_TIMEOUT_SECONDS=60         # Request timeout
```

## Usage

```python
from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig
from chaoschain_integrations.compute.zerog import ZeroGComputeAdapter

# Initialize adapter
zerog = ZeroGComputeAdapter(
    grpc_url="localhost:50051",
    api_key="your_api_key",
)

# Use with ChaosChain SDK
sdk = ChaosChainAgentSDK(
    agent_name="MyAgent",
    agent_domain="example.com",
    agent_role="server",
    network=NetworkConfig.ETHEREUM_SEPOLIA,
    compute_provider=zerog,  # Inject ZeroG compute adapter
    enable_process_integrity=True,
)

# Submit compute task
task = {
    "task_type": "inference",
    "model": "llama-3-8b",
    "inputs": {"prompt": "What is blockchain?"},
    "verification": "tee-ml",
}

job_id = zerog.submit(task)
print(f"Job submitted: {job_id}")

# Check status
status = zerog.status(job_id)
print(f"Status: {status['status']}")

# Get result (wait for completion)
result = zerog.result(job_id, wait=True, timeout_s=600)
print(f"Output: {result.output}")
print(f"Proof method: {result.proof.method}")
print(f"Enclave pubkey: {result.proof.enclave_pubkey}")
print(f"Attestation: {result.proof.attestation}")
```

## Architecture

```
┌─────────────────────┐
│ ChaosChain SDK      │
└──────────┬──────────┘
           │
           │ ComputeBackend Protocol
           │
┌──────────▼──────────┐
│ ZeroGComputeAdapter │  (Python)
└──────────┬──────────┘
           │
           │ gRPC
           │
┌──────────▼──────────┐
│ ZeroG Compute       │  (Go)
│ Sidecar             │
└──────────┬──────────┘
           │
           │ Native SDK
           │
┌──────────▼──────────┐
│ 0G Compute Network  │
│ (TEE Nodes)         │
└─────────────────────┘
```

## Task Specification

Tasks are submitted as dictionaries with the following structure:

```python
task = {
    "task_type": "inference",  # or "training", "fine-tuning"
    "model": "model-identifier",
    "inputs": {
        "prompt": "...",
        # ... other inputs
    },
    "verification": "tee-ml",  # or "zk-ml", "op-ml"
    "docker_image": "optional-custom-image",
    "resources": {
        "gpu": "A100",
        "memory": "16GB",
    }
}
```

## Proof Structure

The adapter returns a `ComputeProof` with:

- `method`: Verification method (e.g., "tee-ml")
- `docker_digest`: Docker image SHA256 hash
- `enclave_pubkey`: TEE public key
- `attestation`: Raw TEE attestation report
- `execution_hash`: Hash of inputs + code
- `signature`: Signature by enclave wallet
- `timestamp`: Execution timestamp

## Running the Sidecar

```bash
cd sidecars/zerog/go
make build
./bin/zerog-compute-bridge --port 50051
```

Or use Docker:

```bash
docker run -p 50051:50051 chaoschain/zerog-compute-bridge:latest
```

## Development

Run tests:

```bash
pytest chaoschain_integrations/compute/zerog/tests/
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
- [0G Compute Network](https://docs.0g.ai/compute)

