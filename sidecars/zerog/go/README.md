# ZeroG Sidecar (Go)

gRPC sidecar service that bridges Python adapters to the native 0G SDK (Go).

## Architecture

```
Python Adapter → gRPC → Go Sidecar → 0G Native SDK
```

## Services

1. **Storage Bridge** (port 50051): Implements ZeroG storage operations
2. **Compute Bridge** (port 50052): Implements ZeroG compute operations

## Building

```bash
# Generate proto code and build binaries
make build

# Just generate proto code
make proto

# Run tests
make test
```

## Running

```bash
# Run storage bridge
make run-storage
# Or directly:
./bin/zerog-storage-bridge --port 50051

# Run compute bridge
make run-compute
# Or directly:
./bin/zerog-compute-bridge --port 50052
```

## Development

### Adding 0G SDK Integration

1. Add 0G SDK as dependency in `go.mod`:
   ```bash
   go get github.com/0glabs/0g-storage-client
   ```

2. Implement service handlers in `internal/storage/` and `internal/compute/`

3. Wire up handlers in `cmd/*/main.go`

### Testing with grpcurl

```bash
# List services
grpcurl -plaintext localhost:50051 list

# Call health check
grpcurl -plaintext localhost:50051 zerog.storage.v1.ZeroGStorage/Health

# Put data
grpcurl -plaintext -d '{"content": "aGVsbG8=", "metadata": {"key": "value"}}' \
  localhost:50051 zerog.storage.v1.ZeroGStorage/Put
```

## Status

**Current**: Stub implementation with proto definitions

**TODO**:
- [ ] Integrate 0G storage SDK
- [ ] Integrate 0G compute SDK
- [ ] Implement service handlers
- [ ] Add comprehensive error handling
- [ ] Add metrics/monitoring
- [ ] Add configuration management
- [ ] Add Docker support
- [ ] Add integration tests

## Dependencies

- Go 1.21+
- Protocol Buffers compiler (`protoc`)
- gRPC Go plugins

