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
