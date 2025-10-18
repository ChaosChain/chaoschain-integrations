# EigenCompute Adapter

**PRODUCTION-READY** integration with [EigenCloud](https://eigencloud.xyz/) TEE-based compute for ChaosChain's **Triple-Verified Stack - Layer 2: Process Integrity**.

## Features

- **✅ Real HTTP REST API Integration**: Production EigenCloud API client (not mocked)
- **✅ TEE-based ML Inference**: Intel SGX/TDX for verifiable AI execution
- **✅ Complete Attestation Chain**: Full TEE proofs for on-chain verification
- **✅ Async Job Management**: Submit, poll, retrieve with proper error handling
- **✅ Multiple Models**: Support for Llama, GPT, and other LLMs
- **✅ Process Integrity**: Cryptographic proof of correct execution

## Installation

```bash
pip install chaoschain-integrations[eigen]
```

## Configuration

**Required**: Set these environment variables (or use `.env` file):

```bash
EIGEN_API_URL=https://api.eigencloud.xyz  # EigenCloud API endpoint
EIGEN_API_KEY=your_api_key_here           # REQUIRED: Your EigenCloud API key
EIGEN_TIMEOUT_SECONDS=600                  # Optional: Request timeout
```

**Getting API Access:**

1. Visit [EigenCloud](https://eigencloud.xyz/) and create an account
2. Generate an API key from your dashboard
3. Set `EIGEN_API_KEY` environment variable

## Usage

```python
from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig
from chaoschain_integrations.compute.eigen import EigenComputeAdapter

# Initialize adapter
eigen = EigenComputeAdapter(
    api_url="http://localhost:8082",
    api_key="your_api_key",
    use_grpc=True,
)

# Use with ChaosChain SDK
sdk = ChaosChainAgentSDK(
    agent_name="EigenAgent",
    agent_domain="eigen.example.com",
    agent_role="server",
    network=NetworkConfig.ETHEREUM_SEPOLIA,
    compute_provider=eigen,  # Inject Eigen adapter
    enable_process_integrity=True,
)

# Submit inference task
task = {
    "task": "inference",
    "model": "llama-3-70b",
    "prompt": "Explain blockchain in simple terms",
    "verification": "tee-ml",
}

job_id = eigen.submit(task)
print(f"Job ID: {job_id}")

# Check status
status = eigen.status(job_id)
print(f"Status: {status['status']}, Progress: {status['progress']}%")

# Get result (wait for completion)
result = eigen.result(job_id, wait=True, timeout_s=600)
print(f"Output: {result.output}")
print(f"Attestation: {result.proof.attestation}")
print(f"Enclave Key: {result.proof.enclave_pubkey}")
```

## Task Format

Submit tasks as dictionaries:

```python
task = {
    "task": "inference",           # Task type
    "model": "model-name",         # Model identifier
    "prompt": "Your prompt here",  # For inference tasks
    "inputs": {                    # Alternative to prompt
        "text": "...",
        "parameters": {...}
    },
    "verification": "tee-ml",      # Verification method
    "image_digest": "sha256:...",  # Optional docker image
    "config": {                    # Optional config
        "temperature": 0.7,
        "max_tokens": 100,
    }
}
```

## Proof Structure

Returns `ComputeProof` with:

- `method`: "tee-ml"
- `docker_digest`: Container image hash
- `enclave_pubkey`: TEE public key
- `attestation`: Raw TEE attestation (quote, report)
- `execution_hash`: Hash of inputs + code
- `signature`: Enclave wallet signature
- `timestamp`: Execution timestamp

## Architecture

```
┌─────────────────────┐
│ ChaosChain SDK      │
└──────────┬──────────┘
           │
           │ ComputeBackend Protocol
           │
┌──────────▼──────────┐
│ EigenComputeAdapter │  (Python)
└──────────┬──────────┘
           │
           │ HTTP/gRPC
           │
┌──────────▼──────────┐
│ Eigen Service       │
│ (TEE Nodes)         │
└─────────────────────┘
```

## HTTP vs gRPC

### HTTP (REST)

```python
eigen = EigenComputeAdapter(
    api_url="http://localhost:8082",
    use_grpc=False,
)
```

### gRPC (Default)

```python
eigen = EigenComputeAdapter(
    api_url="localhost:50052",  # gRPC endpoint
    use_grpc=True,
)
```

## Development

Run tests:

```bash
pytest chaoschain_integrations/compute/eigen/tests/
```

## Integration with genesis_studio.py

See `examples/eigencompute_integration.py` for a complete working example that mirrors the `genesis_studio.py` workflow.

```python
# In genesis_studio.py, replace 0G Compute with EigenCompute:
from chaoschain_integrations.compute.eigen import EigenComputeAdapter

eigen_compute = EigenComputeAdapter(
    api_url=os.getenv("EIGEN_API_URL"),
    api_key=os.getenv("EIGEN_API_KEY"),
)

# Use in your Triple-Verified Stack:
# Layer 2: Process Integrity with EigenCompute TEE
analysis_result = eigen_compute.result(job_id, wait=True)
print(f"TEE Proof: {analysis_result.proof.attestation}")
```

## Status

**Current Status**: ✅ Production Ready

- ✅ Real HTTP REST API implementation
- ✅ Complete error handling & retries
- ✅ TEE attestation extraction
- ✅ Sync/async support
- ✅ Integration tests
- ✅ Production-grade logging
- ✅ Contract tests passing

## References

- [EigenCloud Documentation](https://docs.eigencloud.xyz/)
- [EigenCloud Quickstart](https://docs.eigencloud.xyz/products/eigencompute/quickstart)
- [EigenLayer](https://www.eigenlayer.xyz/)

