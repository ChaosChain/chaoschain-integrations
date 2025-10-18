# Eigen Sidecar (Go)

gRPC sidecar service that bridges Python adapters to Eigen's compute service.

## Architecture

```
Python Adapter → gRPC → Go Sidecar → Eigen API/SDK
```

## Service

**Compute Bridge** (port 50053): Implements Eigen compute operations with TEE attestation

## Building

```bash
# Generate proto code and build binary
make build

# Just generate proto code
make proto

# Run tests
make test
```

## Running

```bash
# Run compute bridge
make run
# Or directly:
./bin/eigen-compute-bridge --port 50053
```

## Development

### Adding Eigen SDK Integration

1. Add Eigen SDK/client as dependency in `go.mod`

2. Implement service handlers in `internal/compute/`

3. Wire up handlers in `cmd/compute-bridge/main.go`

### Testing with grpcurl

```bash
# List services
grpcurl -plaintext localhost:50053 list

# Call health check
grpcurl -plaintext localhost:50053 eigen.compute.v1.EigenCompute/Health

# Submit job
grpcurl -plaintext -d '{"task": "inference", "model": "llama-3", "prompt": "hello"}' \
  localhost:50053 eigen.compute.v1.EigenCompute/SubmitJob
```

## Configuration

Set environment variables:

```bash
EIGEN_API_URL=https://api.eigen.xyz
EIGEN_API_KEY=your_key
EIGEN_TEE_MODE=sgx  # or tdx
```

## Status

**Current**: Stub implementation with proto definitions

**TODO**:
- [ ] Integrate Eigen API client
- [ ] Implement service handlers
- [ ] Add TEE attestation handling
- [ ] Add comprehensive error handling
- [ ] Add metrics/monitoring
- [ ] Add configuration management
- [ ] Add Docker support
- [ ] Add integration tests

## Dependencies

- Go 1.21+
- Protocol Buffers compiler (`protoc`)
- gRPC Go plugins

