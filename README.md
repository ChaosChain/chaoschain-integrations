# ChaosChain Integrations

Partner adapters for [ChaosChain SDK](https://github.com/ChaosChain/chaoschain) - enabling decentralized storage, compute, and attestation for the Triple-Verified Stack.

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Overview

This repository provides **production-ready adapters** for integrating partner services with ChaosChain's Triple-Verified Stack:

- **Layer 1 (Intent)**: AP2 intent and cart mandates
- **Layer 2 (Process)**: EigenCompute TEE + EigenAI verified inference
- **Layer 3 (Data)**: 0G decentralized storage

### Supported Integrations

| Category | Provider | Status | Features |
|----------|----------|--------|----------|
| **Compute (TEE)** | EigenCompute | ✅ Production | Intel TDX, multi-agent support |
| **Compute (LLM)** | EigenAI | ✅ Production | Deterministic inference, signed outputs |
| **Storage** | 0G Network | ✅ Production | Decentralized KV store |
| **Attestation** | Chainlink CRE | 🚧 Coming | Cross-chain verification |

## Installation

```bash
# Install from source
git clone https://github.com/ChaosChain/chaoschain-integrations.git
cd chaoschain-integrations
pip install -e .
```

## Quick Start

### EigenCompute + EigenAI Process Integrity

Run multi-agent TEE application:

```bash
# 1. Set up environment
cp .env.example .env
# Add your keys: EIGEN_API_KEY, BASE_SEPOLIA_PRIVATE_KEY, BASE_SEPOLIA_RPC_URL

# 2. Start EigenCompute sidecar
cd sidecars/eigencompute/go
./start.sh &

# 3. Run Genesis Studio demo
python3 genesis_studio.py
```

**What it does:**
- Alice (shopping analyst) runs in EigenCompute TEE
- Bob (validator) verifies analysis in TEE
- Charlie (market analyst) provides context
- All agents call EigenAI from within TEE
- Complete ProcessProof with signatures

### Direct TEE Endpoints

Test deployed agents directly:

```bash
# Health check
curl http://136.117.37.251:8080/health

# Alice: Shopping analysis
curl -X POST http://136.117.37.251:8080/alice/analyze_shopping \
  -H 'Content-Type: application/json' \
  -d '{
    "item_type": "winter_jacket",
    "color": "green",
    "budget": 150,
    "premium_tolerance": 0.20
  }'

# Bob: Validate analysis
curl -X POST http://136.117.37.251:8080/bob/validate_analysis \
  -H 'Content-Type: application/json' \
  -d '{
    "item_type": "winter_jacket",
    "final_price": 135.50,
    "confidence": 0.92
  }'

# Charlie: Market analysis
curl -X POST http://136.117.37.251:8080/charlie/market_analysis \
  -H 'Content-Type: application/json' \
  -d '{
    "product_category": "winter_jackets",
    "region": "US"
  }'
```

## Architecture

### Triple-Verified Stack

```
┌─────────────────────────────────────────────────────────────┐
│ Layer 1: Intent Verification (AP2)                         │
│ • ERC-8004 agent identity registry                         │
│ • Intent mandates with cryptographic commitments           │
│ • Cart mandates for transaction approval                   │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 2: Process Integrity (EigenCompute + EigenAI)        │
│ • Intel TDX TEE execution                                   │
│ • Deterministic LLM inference                               │
│ • Hardware attestations                                     │
│ • Signed execution proofs                                   │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│ Layer 3: Data Verifiability (0G Network)                   │
│ • Decentralized storage                                     │
│ • Merkle proofs                                             │
│ • Immutable audit trail                                     │
└─────────────────────────────────────────────────────────────┘
```

### EigenCompute Integration

**Multi-Agent TEE Application:**
- Docker image: `sumeetchaos/chaoschain-genesis-agents:v3`
- App ID: `0xb29Ec00fF0D6C1349E6DFcD16234082aE60e64bb`
- Enclave Wallet: `0x05d39048EDB42183ABaf609f4D5eda3A2a2eDcA3`
- IP: `136.117.37.251`

**Agents:**
- **Alice**: Shopping analysis with EigenAI
- **Bob**: Validation and quality scoring
- **Charlie**: Market analysis and trends

## Development

### Project Structure

```
chaoschain-integrations/
├── chaoschain_integrations/
│   ├── compute/
│   │   └── eigencompute/      # EigenCompute TEE adapter
│   ├── storage/
│   │   └── zerog/              # 0G storage adapter
│   └── common/                 # Shared types
├── docker/
│   └── genesis-agents/         # Multi-agent TEE application
├── sidecars/
│   └── eigencompute/go/        # EigenCompute REST API bridge
├── agents/
│   └── server_agent_sdk.py    # Agent SDK with TEE support
└── genesis_studio.py           # Full stack demo

```

### Running Tests

```bash
# Test EigenAI process integrity
python3 test_eigenai_process_integrity.py

# Test Genesis Studio workflow
export COMPUTE_PROVIDER=eigencompute
python3 genesis_studio.py
```

### Deploying to EigenCompute

```bash
# 1. Build and push Docker image
cd docker/genesis-agents
docker build --platform linux/amd64 -t your-username/app:tag .
docker push your-username/app:tag

# 2. Deploy to TEE
eigenx app deploy --name your-app --log-visibility public your-username/app:tag

# 3. Update Go sidecar
cd sidecars/eigencompute/go
# Edit main.go: update appRegistry with new app ID and IP
go build -o eigenbridge .
./start.sh &
```

## Production Deployment

### Environment Variables

```bash
# EigenAI
EIGEN_API_KEY=sk-...
EIGEN_API_URL=https://eigenai.eigencloud.xyz

# Base Sepolia
BASE_SEPOLIA_RPC_URL=https://base-sepolia.g.alchemy.com/v2/...
BASE_SEPOLIA_PRIVATE_KEY=0x...
BASE_SEPOLIA_CHAIN_ID=84532

# 0G Network
ZG_FLOW_ADDRESS=0x...
ZG_INDEXER_RPC=https://rpc-testnet.0g.ai
```

### Security

- All secrets encrypted via EigenCompute KMS
- Private keys never exposed in logs
- TEE-bound enclave wallets
- Hardware attestations (Intel TDX)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Resources

- [ChaosChain SDK](https://github.com/ChaosChain/chaoschain)
- [EigenCompute Docs](https://docs.eigencloud.xyz)
- [EigenAI API](https://eigenai.eigencloud.xyz)
- [0G Network](https://0g.ai)

## Support

- Issues: [GitHub Issues](https://github.com/ChaosChain/chaoschain-integrations/issues)
- Discussions: [GitHub Discussions](https://github.com/ChaosChain/chaoschain-integrations/discussions)
