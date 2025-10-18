#!/bin/bash
#
# EigenAI Deployment Script (Without eigenx CLI)
# This deploys using EigenAI for now (LLM with TEE proofs)
# Until eigenx CLI is available, we'll use the working EigenAI integration
#

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${BLUE}║  ChaosChain EigenAI Deployment                       ║${NC}"
echo -e "${BLUE}║  Layer 2: Process Integrity (LLM with TEE proofs)    ║${NC}"
echo -e "${BLUE}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Check prerequisites
echo -e "${YELLOW}🔍 Checking prerequisites...${NC}"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python3 not found${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Python3 found ($(python3 --version))${NC}"

# Check environment variables
if [ -z "$EIGEN_API_KEY" ]; then
    echo -e "${RED}❌ EIGEN_API_KEY not set${NC}"
    echo -e "${YELLOW}💡 Set with: export EIGEN_API_KEY=sk-...${NC}"
    exit 1
fi
echo -e "${GREEN}✅ EIGEN_API_KEY set${NC}"

if [ -z "$BASE_SEPOLIA_RPC_URL" ]; then
    echo -e "${YELLOW}⚠️  BASE_SEPOLIA_RPC_URL not set, using default${NC}"
    export BASE_SEPOLIA_RPC_URL=https://sepolia.base.org
fi
echo -e "${GREEN}✅ BASE_SEPOLIA_RPC_URL set${NC}"

if [ -z "$BASE_SEPOLIA_PRIVATE_KEY" ]; then
    echo -e "${RED}❌ BASE_SEPOLIA_PRIVATE_KEY not set${NC}"
    echo -e "${YELLOW}💡 Set with: export BASE_SEPOLIA_PRIVATE_KEY=0x...${NC}"
    exit 1
fi
echo -e "${GREEN}✅ BASE_SEPOLIA_PRIVATE_KEY set${NC}"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Installing ChaosChain SDK${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo ""

# Install SDK
echo -e "${YELLOW}📦 Installing chaoschain-sdk...${NC}"
python3 -m pip install -q ./sdk || {
    echo -e "${RED}❌ SDK installation failed${NC}"
    exit 1
}
echo -e "${GREEN}✅ ChaosChain SDK installed${NC}"

# Install integrations
echo -e "${YELLOW}📦 Installing chaoschain-integrations...${NC}"
python3 -m pip install -q -e .[eigen] || {
    echo -e "${RED}❌ Integrations installation failed${NC}"
    exit 1
}
echo -e "${GREEN}✅ ChaosChain Integrations installed${NC}"

echo ""
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Testing EigenAI Integration${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}🧪 Running EigenAI test...${NC}"

# Create test script
cat > test_eigenai_deployment.py << 'EOF'
#!/usr/bin/env python3
import sys
import os

# Add paths
sys.path.insert(0, os.path.dirname(__file__))

from agents.server_agent_sdk import GenesisServerAgentSDK
from chaoschain_sdk import NetworkConfig
from rich import print as rprint

try:
    rprint("[bold blue]🚀 Initializing Alice with EigenAI...[/bold blue]")
    
    alice = GenesisServerAgentSDK(
        agent_name="Alice",
        agent_domain="alice.genesis.studio",
        compute_provider="eigenai",  # Use EigenAI (not eigencompute)
        network=NetworkConfig.BASE_SEPOLIA
    )
    
    rprint(f"[green]✅ Alice initialized[/green]")
    rprint(f"[blue]   Wallet: {alice.sdk.wallet_address}[/blue]")
    rprint(f"[blue]   Compute: {alice.compute_provider_type}[/blue]")
    
    rprint("\n[bold blue]🛒 Testing shopping analysis...[/bold blue]")
    
    result = alice.generate_smart_shopping_analysis(
        item_type="winter_jacket",
        color="green",
        budget=150.0,
        premium_tolerance=0.20
    )
    
    analysis = result["analysis"]
    proof = result["process_integrity_proof"]
    
    rprint("\n[bold green]✅ Analysis complete![/bold green]")
    rprint(f"[blue]   Item: {analysis.get('item_type', 'N/A')}[/blue]")
    rprint(f"[blue]   Price: ${analysis.get('final_price', 0):.2f}[/blue]")
    rprint(f"[blue]   Merchant: {analysis.get('merchant', 'N/A')}[/blue]")
    rprint(f"[blue]   TEE Provider: {proof.tee_provider}[/blue]")
    rprint(f"[blue]   TEE Job ID: {proof.tee_job_id}[/blue]")
    rprint(f"[blue]   Verification: {proof.verification_status}[/blue]")
    
    rprint("\n[bold green]🎉 SUCCESS! EigenAI is working![/bold green]")
    
    sys.exit(0)
    
except Exception as e:
    rprint(f"\n[bold red]❌ Test failed: {e}[/bold red]")
    import traceback
    traceback.print_exc()
    sys.exit(1)
EOF

chmod +x test_eigenai_deployment.py

# Run test
export COMPUTE_PROVIDER=eigenai

python3 test_eigenai_deployment.py || {
    echo -e "${RED}❌ Test failed${NC}"
    rm test_eigenai_deployment.py
    exit 1
}

# Clean up test script
rm test_eigenai_deployment.py

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🎉 EigenAI Deployment Complete!                     ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "${BLUE}📋 Summary:${NC}"
echo -e "${BLUE}   • EigenAI: ✅ Working (TEE-verified LLM)${NC}"
echo -e "${BLUE}   • Model: gpt-oss-120b-f16${NC}"
echo -e "${BLUE}   • Process Integrity: Layer 2 (partial - LLM only)${NC}"
echo ""
echo -e "${YELLOW}ℹ️  Note:${NC}"
echo -e "${YELLOW}   EigenCompute (full TEE deployment) requires eigenx CLI${NC}"
echo -e "${YELLOW}   which is currently in alpha/allowlisted access.${NC}"
echo -e "${YELLOW}   Using EigenAI for now (LLM with TEE signatures).${NC}"
echo ""
echo -e "${YELLOW}🛠️  Next Steps:${NC}"
echo -e "${YELLOW}   1. Run genesis_studio.py with COMPUTE_PROVIDER=eigenai${NC}"
echo -e "${YELLOW}   2. For full TEE deployment, contact EigenCloud for eigenx access${NC}"
echo ""

