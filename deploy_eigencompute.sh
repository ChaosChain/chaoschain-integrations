#!/bin/bash
#
# EigenCompute Deployment Script
# This script sets up and deploys the complete EigenCompute stack
#

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Load .env file if it exists
if [ -f ".env" ]; then
    echo -e "${GREEN}🔐 Loading environment from .env file...${NC}"
    set -a  # Export all variables
    source .env
    set +a
fi

echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ChaosChain EigenCompute Deployment                  ║${NC}"
echo -e "${BLUE}║  Layer 2: Process Integrity                          ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

# Check Docker
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker not found. Please install Docker.${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker found${NC}"

# Check Go
if ! command -v go &> /dev/null; then
    echo -e "${RED}❌ Go not found. Please install Go 1.22+${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Go found ($(go version))${NC}"

# Check eigenx CLI
if ! command -v eigenx &> /dev/null; then
    echo -e "${RED}❌ eigenx CLI not found${NC}"
    echo -e "${YELLOW}💡 Install with: curl -sSfL https://eigencloud.xyz/install.sh | sh${NC}"
    exit 1
fi
echo -e "${GREEN}✅ eigenx CLI found ($(eigenx version 2>&1 | grep Version))${NC}"

# Check authentication
if ! eigenx auth whoami &> /dev/null; then
    echo -e "${RED}❌ eigenx not authenticated${NC}"
    echo -e "${YELLOW}💡 Authenticate with: eigenx auth login${NC}"
    exit 1
fi
echo -e "${GREEN}✅ eigenx authenticated ($(eigenx auth whoami | grep Address | awk '{print $2}'))${NC}"

# Check environment variables
if [ -z "$EIGEN_API_KEY" ]; then
    echo -e "${RED}❌ EIGEN_API_KEY not set${NC}"
    echo -e "${YELLOW}💡 Set with: export EIGEN_API_KEY=sk-...${NC}"
    exit 1
fi
echo -e "${GREEN}✅ EIGEN_API_KEY set${NC}"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Step 1: Building Alice Agent Docker Image${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo ""

cd docker/alice-shopping-agent

echo -e "${YELLOW}🐳 Building Docker image: chaoschain/alice-shopping-agent:latest${NC}"
docker build -t chaoschain/alice-shopping-agent:latest . || {
    echo -e "${RED}❌ Docker build failed${NC}"
    exit 1
}

echo -e "${GREEN}✅ Docker image built successfully${NC}"
echo -e "${BLUE}   Image: chaoschain/alice-shopping-agent:latest${NC}"
echo -e "${BLUE}   Digest: $(docker images --digests chaoschain/alice-shopping-agent:latest | tail -n 1 | awk '{print $3}')${NC}"

cd ../..

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Step 2: Building EigenCompute Sidecar${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo ""

cd sidecars/eigencompute/go

echo -e "${YELLOW}⚙️  Building Go sidecar...${NC}"
make build || {
    echo -e "${RED}❌ Sidecar build failed${NC}"
    exit 1
}

echo -e "${GREEN}✅ Sidecar built successfully${NC}"

cd ../../..

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Step 3: Starting EigenCompute Sidecar${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo ""

# Check if sidecar is already running
if lsof -Pi :8080 -sTCP:LISTEN -t >/dev/null ; then
    echo -e "${YELLOW}⚠️  Sidecar already running on port 8080${NC}"
    echo -e "${YELLOW}   Killing existing process...${NC}"
    kill $(lsof -t -i:8080) 2>/dev/null || true
    sleep 2
fi

echo -e "${YELLOW}🚀 Starting sidecar on http://localhost:8080${NC}"

cd sidecars/eigencompute/go
nohup ./start.sh > ../../../sidecar.log 2>&1 &
SIDECAR_PID=$!
cd ../../..

echo -e "${GREEN}✅ Sidecar started (PID: $SIDECAR_PID)${NC}"
echo -e "${BLUE}   Logs: tail -f sidecar.log${NC}"

# Wait for sidecar to be ready
echo -e "${YELLOW}⏳ Waiting for sidecar to be ready...${NC}"
for i in {1..10}; do
    if curl -s http://localhost:8080/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Sidecar is healthy${NC}"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}❌ Sidecar failed to start${NC}"
        echo -e "${YELLOW}   Check logs: tail -f sidecar.log${NC}"
        exit 1
    fi
    sleep 1
done

# Display sidecar info
SIDECAR_INFO=$(curl -s http://localhost:8080/health)
echo -e "${BLUE}   Status: $(echo $SIDECAR_INFO | jq -r '.status')${NC}"
echo -e "${BLUE}   EigenX CLI: $(echo $SIDECAR_INFO | jq -r '.eigenx_cli')${NC}"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Step 4: Testing Deployment${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}🧪 Running deployment test...${NC}"

# Create test script
cat > test_deployment.py << 'EOF'
#!/usr/bin/env python3
import sys
import os

# Add paths
sys.path.insert(0, os.path.dirname(__file__))

from agents.server_agent_sdk import GenesisServerAgentSDK
from chaoschain_sdk import NetworkConfig

print("🚀 Initializing Alice with EigenCompute...")

alice = GenesisServerAgentSDK(
    agent_name="Alice",
    agent_domain="alice.genesis.studio",
    compute_provider="eigencompute",
    network=NetworkConfig.BASE_SEPOLIA
)

print(f"✅ Alice initialized")
print(f"   Wallet: {alice.sdk.wallet_address}")
print(f"   Compute: {alice.compute_provider_type}")

print("\n🛒 Testing shopping analysis...")

result = alice.generate_smart_shopping_analysis(
    item_type="winter_jacket",
    color="green",
    budget=150.0,
    premium_tolerance=0.20
)

print("\n✅ Analysis complete!")
print(f"   App ID: {result['analysis'].get('eigencompute', {}).get('app_id', 'N/A')}")
print(f"   Enclave: {result['analysis'].get('eigencompute', {}).get('enclave_wallet', 'N/A')[:20]}...")
print(f"   Digest: {result['analysis'].get('eigencompute', {}).get('docker_digest', 'N/A')[:32]}...")
print(f"   Proof: {result['process_integrity_proof'].proof_id}")

print("\n🎉 SUCCESS! EigenCompute is working!")
EOF

chmod +x test_deployment.py

# Run test
export COMPUTE_PROVIDER=eigencompute
export EIGENCOMPUTE_SIDECAR_URL=http://localhost:8080
export BASE_SEPOLIA_RPC_URL=https://sepolia.base.org
export BASE_SEPOLIA_PRIVATE_KEY=${BASE_SEPOLIA_PRIVATE_KEY:-0x0000000000000000000000000000000000000000000000000000000000000001}

python3 test_deployment.py || {
    echo -e "${RED}❌ Test failed${NC}"
    echo -e "${YELLOW}   Check logs: tail -f sidecar.log${NC}"
    kill $SIDECAR_PID 2>/dev/null || true
    exit 1
}

# Clean up test script
rm test_deployment.py

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🎉 EigenCompute Deployment Complete!                ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📋 Summary:${NC}"
echo -e "${BLUE}   • Docker Image: chaoschain/alice-shopping-agent:latest${NC}"
echo -e "${BLUE}   • Sidecar: http://localhost:8080 (PID: $SIDECAR_PID)${NC}"
echo -e "${BLUE}   • Logs: tail -f sidecar.log${NC}"
echo ""
echo -e "${YELLOW}🛠️  Next Steps:${NC}"
echo -e "${YELLOW}   1. Run genesis_studio.py with COMPUTE_PROVIDER=eigencompute${NC}"
echo -e "${YELLOW}   2. Deploy more agents with different images${NC}"
echo -e "${YELLOW}   3. Monitor sidecar logs: tail -f sidecar.log${NC}"
echo ""
echo -e "${RED}🛑 To stop sidecar: kill $SIDECAR_PID${NC}"
echo ""

