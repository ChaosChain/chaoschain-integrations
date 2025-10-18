# Chainlink CRE Sidecar (Go)

HTTP/gRPC sidecar service that bridges Python adapters to Chainlink CRE (Cross-Chain Replayability Engine).

## Architecture

```
Python Adapter → HTTP/gRPC → Go Sidecar → Chainlink CRE API
```

## Note

Chainlink CRE uses HTTP REST API, so a Go sidecar may not be strictly necessary. The Python adapter can communicate directly with the CRE API.

This directory is reserved for future use if native Go SDK integration becomes available or if additional protocol translation is needed.

## Status

**Current**: Not implemented (Python adapter uses HTTP directly)

**Future**:
- [ ] Add if Chainlink releases native Go SDK
- [ ] Add if custom protocol translation is needed
- [ ] Add if performance optimization via Go is required

