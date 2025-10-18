#!/bin/bash
#
# 🔐 SECURE Environment Setup for EigenCompute
# This script will create .env file with your private key
# .env is in .gitignore and will NOT be committed to git
#

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}╔═══════════════════════════════════════════════════════╗${NC}"
echo -e "${YELLOW}║  🔐 ChaosChain EigenCompute - Secure Setup          ║${NC}"
echo -e "${YELLOW}╚═══════════════════════════════════════════════════════╝${NC}"
echo ""

# Check if .env already exists
if [ -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env file already exists!${NC}"
    read -p "Do you want to overwrite it? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Aborted.${NC}"
        exit 1
    fi
fi

# Prompt for private key securely (input hidden)
echo -e "${GREEN}Enter your PRIVATE KEY for 0x20E7B2A2c8969725b88Dd3EF3a11Bc3353C83F70:${NC}"
echo -e "${YELLOW}(Your input will be hidden for security)${NC}"
read -s PRIVATE_KEY
echo ""

# Validate private key format
if [[ ! $PRIVATE_KEY =~ ^0x[0-9a-fA-F]{64}$ ]]; then
    echo -e "${RED}❌ Invalid private key format!${NC}"
    echo -e "${YELLOW}Expected format: 0x followed by 64 hex characters${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Private key format valid${NC}"

# Create .env file
cat > .env << EOF
# ⚠️ NEVER COMMIT THIS FILE! (.env is in .gitignore)
# Generated: $(date)

# ═══════════════════════════════════════════════════════════
# EigenCompute / EigenAI
# ═══════════════════════════════════════════════════════════

EIGEN_API_KEY=sk-b95b841711571e641a4d11d942e3bf79d5e06ba643d2b074017c1bb3c205a7fb
STUDIO_ADDRESS=0x20E7B2A2c8969725b88Dd3EF3a11Bc3353C83F70
PRIVATE_KEY=${PRIVATE_KEY}

# ═══════════════════════════════════════════════════════════
# Base Sepolia Network
# ═══════════════════════════════════════════════════════════

BASE_SEPOLIA_RPC_URL=https://sepolia.base.org
BASE_SEPOLIA_PRIVATE_KEY=${PRIVATE_KEY}

# ═══════════════════════════════════════════════════════════
# Compute Provider
# ═══════════════════════════════════════════════════════════

COMPUTE_PROVIDER=eigencompute
EIGENCOMPUTE_SIDECAR_URL=http://localhost:8080
EOF

# Set secure permissions
chmod 600 .env

echo ""
echo -e "${GREEN}✅ .env file created successfully!${NC}"
echo -e "${GREEN}   Permissions: 600 (only you can read/write)${NC}"
echo -e "${GREEN}   Location: $(pwd)/.env${NC}"
echo ""
echo -e "${YELLOW}⚠️  SECURITY REMINDERS:${NC}"
echo -e "${YELLOW}   1. .env is in .gitignore (won't be committed)${NC}"
echo -e "${YELLOW}   2. Never share .env file${NC}"
echo -e "${YELLOW}   3. Never commit it to git${NC}"
echo ""
echo -e "${GREEN}🚀 You can now run: ./deploy_eigencompute.sh${NC}"
echo ""

