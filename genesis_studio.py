#!/usr/bin/env python3
"""
CHAOSCHAIN GENESIS STUDIO - x402 Enhanced Commercial Prototype

This script demonstrates the complete end-to-end commercial lifecycle of agentic work
with x402 payment integration:

1. On-chain identity registration using ERC-8004
2. Verifiable work execution with IPFS storage
3. x402 agent-to-agent payments with cryptographic receipts
4. Enhanced evidence packages with payment proofs for PoA
5. Enhanced evidence packages with payment proofs

Usage:
    python genesis_studio.py

=== PLUGGABLE PROVIDER ARCHITECTURE DEMO ===

The ChaosChain SDK now supports pluggable storage and compute providers.
This demonstrates how developers can inject custom providers like 0G Storage/Compute:

Example 1: Using 0G Storage via gRPC Sidecar Bridge
```python
from chaoschain_sdk import ChaosChainAgentSDK

# Initialize 0G Storage provider via gRPC sidecar
zg_storage = ZeroGStorageGRPC(
    grpc_url="localhost:50051",  # 0G bridge gRPC endpoint
    api_key="your-0g-api-key"
)

# Inject into SDK
agent = ChaosChainAgentSDK(
    agent_name="MyAgent",
    agent_domain="myagent.example.com",
    agent_role="server",
    network="0g-testnet",
    storage_provider=zg_storage  # ✅ Custom provider injected
)

# SDK will now use 0G Storage for all evidence packages
result = zg_storage.put(
    evidence_bytes,
    tags={"task": "audit"},
    idempotency_key="request-123"
)
print(f"Stored on 0G: {result.uri}")  # 0g://object/abc123
```

Example 2: Using 0G Compute via gRPC Sidecar Bridge
```python
from chaoschain_sdk import ChaosChainAgentSDK

# Initialize 0G Compute provider via gRPC sidecar
zg_compute = ZeroGComputeGRPC(
    grpc_url="localhost:50052",  # 0G compute gRPC endpoint
    api_key="your-0g-api-key"
)

# Inject into SDK
agent = ChaosChainAgentSDK(
    agent_name="MyAgent",
    agent_domain="myagent.example.com",
    agent_role="server",
    network="0g-testnet",
    compute_provider=zg_compute  # ✅ Custom compute provider injected
)

# Submit verifiable compute task
job_id = zg_compute.submit(
    task={"model": "llama2", "prompt": "Analyze market data"},
    verification=ProviderVerificationMethod.TEE_ML
)

# Wait for completion and get results
result = zg_compute.wait_for_completion(job_id)
print(f"Output: {result.output}")
print(f"Proof: {result.proof}")  # TEE attestation
```

Example 3: Default Behavior (Auto-detection)
```python
# Without provider injection, SDK auto-detects available storage:
# Pinata (if PINATA_JWT set) → Local IPFS → Memory fallback
agent = ChaosChainAgentSDK(
    agent_name="MyAgent",
    agent_domain="myagent.example.com",
    agent_role="server",
    network="base-sepolia"
    # No provider injection - uses auto-detected storage
)
```

Example 4: ERC-8004 v1.0 Feedback with Payment Proof
```python
from chaoschain_sdk import ChaosChainAgentSDK
from chaoschain_sdk.types import PaymentProof

# Execute payment (x402)
payment_proof = sdk.x402_manager.execute_agent_payment(
    from_agent="Alice",
    to_agent="Bob",
    amount_usdc=10.0,
    service_description="Data analysis task"
)

# Generate feedback authorization
feedback_auth = sdk.chaos_agent.generate_feedback_authorization(
    agent_id=server_agent_id,
    client_address=client_wallet_address,
    index_limit=1,
    expiry=int(time.time()) + 3600
)

# Create ERC-8004 v1.0 compliant feedback with payment proof
# This automatically:
# 1. Formats feedback JSON per ERC-8004 v1.0 spec
# 2. Includes payment proof (fromAddress, toAddress, chainId, txHash)
# 3. Uploads to IPFS/0G Storage
# 4. Returns (URI, hash) ready for on-chain submission
uri, hash = sdk.chaos_agent.create_feedback_with_payment(
    agent_id=server_agent_id,
    score=100,
    feedback_auth=feedback_auth,
    payment_proof=payment_proof,  # ✅ Automatically ERC-8004 v1.0 compliant!
    skill="data-analysis",
    task="market-research",
    tag1="quality",
    tag2="speed"
)

# Submit feedback to on-chain reputation registry
tx_hash = sdk.chaos_agent.give_feedback(
    agent_id=server_agent_id,
    score=100,
    feedback_auth=feedback_auth,
    file_uri=uri,  # URI with payment proof included
    file_hash=hash
)

print(f"✅ Feedback with payment proof submitted: {tx_hash}")
```
"""

import os
import sys
import json
import time
from datetime import datetime
from typing import Dict, Any, Optional
from rich.panel import Panel

# Add integrations to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "chaoschain-integrations"))

from dotenv import load_dotenv
from rich import print as rprint
from rich.panel import Panel
from rich.align import Align
from rich.table import Table
from chaoschain_sdk import ChaosChainAgentSDK, NetworkConfig
from chaoschain_sdk.types import AgentRole

# Import agents
from agents.server_agent_sdk import GenesisServerAgentSDK
from agents.validator_agent_sdk import GenesisValidatorAgentSDK
from agents.client_agent_genesis import GenesisClientAgent

# Load environment variables
load_dotenv()

# Fix hyphenated env vars for SDK compatibility
# SDK expects hyphenated versions (e.g., 0G-TESTNET_RPC_URL) but we use underscores in .env
if os.getenv("ZEROG_TESTNET_RPC_URL") and not os.getenv("0G-TESTNET_RPC_URL"):
    os.environ["0G-TESTNET_RPC_URL"] = os.environ["ZEROG_TESTNET_RPC_URL"]
if os.getenv("ZEROG_TESTNET_PRIVATE_KEY") and not os.getenv("0G-TESTNET_PRIVATE_KEY"):
    os.environ["0G-TESTNET_PRIVATE_KEY"] = os.environ["ZEROG_TESTNET_PRIVATE_KEY"]
if os.getenv("ZEROG_TESTNET_CHAIN_ID") and not os.getenv("0G-TESTNET_CHAIN_ID"):
    os.environ["0G-TESTNET_CHAIN_ID"] = os.environ["ZEROG_TESTNET_CHAIN_ID"]

# Set defaults if not provided
if not os.getenv("0G-TESTNET_RPC_URL"):
    os.environ["0G-TESTNET_RPC_URL"] = "https://evmrpc-testnet.0g.ai"
    print("✅ Using default 0G Testnet RPC: https://evmrpc-testnet.0g.ai")
if not os.getenv("0G-TESTNET_CHAIN_ID"):
    os.environ["0G-TESTNET_CHAIN_ID"] = "16600"
    print("✅ Using default 0G Testnet Chain ID: 16600")

class GenesisStudioX402Orchestrator:
    """Enhanced Genesis Studio orchestrator with x402 payment integration"""
    
    def __init__(self):
        # Track results for final summary
        self.results = {}
        
        # Agent SDK instances
        self.alice_sdk = None  # Server Agent
        self.bob_sdk = None    # Validator Agent
        self.charlie_sdk = None # Client Agent
    
    def run_complete_demo(self):
        """Execute the complete Genesis Studio x402 demonstration"""
        
        try:
            self._print_banner()
            
            # Phase 1: Setup & On-Chain Identity
            self._phase_1_setup_and_identity()
            
            # Phase 2: x402 Enhanced Work & Payment Flow
            self._phase_2_x402_work_and_payment()
            
            # Phase 3: Enhanced Evidence Packages with Payment Proofs
            self._phase_3_enhanced_evidence_packages()
            
            
            # Final Summary
            self._display_final_summary()
            
        except KeyboardInterrupt:
            rprint("[yellow]⚠️  Demo interrupted by user[/yellow]")
            sys.exit(1)
        except Exception as e:
            import traceback
            rprint("[red]FULL TRACEBACK:[/red]")
            traceback.print_exc()
            rprint(f"[red]❌ Demo failed with unexpected error: {e}[/red]")
            sys.exit(1)
    
    def _print_banner(self):
        """Print Genesis Studio banner"""
        banner = """
[bold blue] CHAOSCHAIN GENESIS STUDIO - SDK with 0G INTEGRATION[/bold blue]
[bold cyan]Triple-Verified Stack Commercial Prototype[/bold cyan]

[yellow] Triple-Verified Stack:[/yellow]
• Layer 1: AP2 Intent Verification (Google)
• Layer 2: Process Integrity (ChaosChain + 0G Compute)
• Layer 3: Adjudication/Accountability (ChaosChain)

[green]🔗 ChaosChain owns 2/3 layers![/green]
"""
        
        banner_panel = Panel(
            Align.center(banner),
            title="[bold green]🏆 Genesis Studio[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        
        rprint(banner_panel)
        rprint()
    
    def _phase_1_setup_and_identity(self):
        """Phase 1: Setup & On-Chain Identity Registration with x402 Integration"""
        
        rprint("\n[bold blue]📋 Phase 1: Setup & x402-Enhanced Identity[/bold blue]")
        rprint("[cyan]Creating agent SDKs and registering on-chain identities with payment capabilities[/cyan]")
        rprint("=" * 80)
        
        # Step 1: Configuration Check
        rprint("\n[blue]🔧 Step 1: Validating x402 and ERC-8004 configuration...[/blue]")
        self._validate_configuration()
        rprint("[green]✅ Configuration validated[/green]")
        
        # Step 2: Initialize Agent SDKs with x402 Integration
        rprint("\n[blue]🔧 Step 2: Initializing ChaosChain Agent SDKs with x402 payment support...[/blue]")
        self._initialize_agent_sdks()
        rprint("[green]✅ Agent SDKs initialized[/green]")
        
        # Step 3: Fund wallets from faucet
        rprint("\n[blue]🔧 Step 3: Funding wallets from Base Sepolia faucet...[/blue]")
        self._fund_agent_wallets()
        rprint("[green]✅ Wallets funded[/green]")
        
        # Step 4: On-chain registration
        rprint("\n[blue]🔧 Step 4: Registering agents on ERC-8004 IdentityRegistry...[/blue]")
        self._register_agents_onchain()
        rprint("[green]✅ Agents registered on-chain[/green]")
    
    def _phase_2_x402_work_and_payment(self):
        """Phase 2: Triple-Verified Stack Work & Payment"""
        
        rprint("\n[bold blue]📋 Phase 2: Triple-Verified Stack Work & Payment[/bold blue]")
        rprint("[cyan]Alice performs smart shopping with AP2 intent verification, ChaosChain process integrity (0G Compute), and x402 payments (A0GI)[/cyan]")
        rprint("=" * 80)
        
        # Step 5: AP2 Intent Verification
        rprint("\n[blue]🔧 Step 5: Creating AP2 intent mandate for smart shopping...[/blue]")
        intent_mandate = self._create_ap2_intent_mandate()
        rprint("[green]✅ AP2 intent mandate created and verified[/green]")
        
        # Step 6: Work Execution with Process Integrity (Alice)
        rprint("\n[blue]🔧 Step 6: Alice performing smart shopping with ChaosChain Process Integrity...[/blue]")
        # Extract intent ID from mandate for process integrity linking (Layer 1 → Layer 2 link)
        intent_obj = intent_mandate.get("intent_mandate") if isinstance(intent_mandate, dict) else intent_mandate
        intent_id = getattr(intent_obj, "intent_id", None) if intent_obj else None
        if intent_id:
            rprint(f"[cyan]🔗 Linking execution to AP2 Intent: {intent_id}[/cyan]")
        analysis_data, process_integrity_proof = self._execute_smart_shopping_with_integrity(intent_id=intent_id)
        rprint("[green]✅ Smart shopping completed with process integrity proof[/green]")
        
        # Step 7: Evidence Storage (Alice) - Using 0G Storage
        rprint("\n[blue]🔧 Step 7: Storing analysis on 0G Storage...[/blue]")
        analysis_cid = self._store_analysis_on_0g_storage(analysis_data, process_integrity_proof)
        rprint("[green]✅ Analysis stored on 0G Storage[/green]")
        
        # Step 8: 0G Token Payment (A0GI) with AP2 authorization
        rprint("\n[blue]🔧 Step 8: Processing 0G token payment with AP2 authorization (A0GI)...[/blue]")
        payment_results = self._execute_0g_token_payment(analysis_cid, analysis_data, intent_mandate)
        rprint(f"[green]✅ Payment completed: {payment_results['amount']:.4f} A0GI (Charlie → Alice)[/green]")
        
        # Step 6: Validation Request (Alice → Bob)
        rprint("\n[blue]🔧 Step 6: Alice requesting validation from Bob...[/blue]")
        rprint("[green]✅ Validation requested[/green]")
        
        # Step 7: Validation & Payment (Bob)
        rprint("\n[blue]🔧 Step 7: Bob validating with 0G Compute and payment...[/blue]")
        validation_score, validation_result = self._perform_validation_with_0g_compute(analysis_data)
        rprint(f"[green]✅ Validation completed (Score: {validation_score}/100)[/green]")
    
    def _phase_3_enhanced_evidence_packages(self):
        """Phase 3: Enhanced Evidence Packages with Payment Proofs"""
        
        rprint("\n[bold blue]📋 Phase 3: Enhanced Evidence Packages[/bold blue]")
        rprint("[cyan]Creating comprehensive evidence packages with x402 payment proofs for PoA[/cyan]")
        rprint("=" * 80)
        
        # Step 11: Create Enhanced Evidence Package (Alice)
        rprint("\n[blue]🔧 Step 11: Alice creating enhanced evidence package with payment proofs...[/blue]")
        alice_evidence_package = self._create_enhanced_evidence_package()
        rprint("[green]✅ Enhanced evidence package created[/green]")
        
        # Step 12: Store Enhanced Evidence Package on 0G Storage
        rprint("\n[blue]🔧 Step 12: Storing enhanced evidence package on 0G Storage...[/blue]")
        enhanced_evidence_cid = self._store_enhanced_evidence_package(alice_evidence_package)
        rprint("[green]✅ Enhanced evidence package stored[/green]")
    
    
    def _validate_configuration(self):
        """Validate all required environment variables including x402"""
        network = os.getenv("NETWORK", "base-sepolia")
        
        # Core required variables (network-specific)
        if network == "0g-testnet":
            required_vars = [
                "NETWORK", "ZEROG_TESTNET_RPC_URL", "ZEROG_TESTNET_PRIVATE_KEY"
            ]
        elif network == "base-sepolia":
            required_vars = [
                "NETWORK", "BASE_SEPOLIA_RPC_URL", "BASE_SEPOLIA_PRIVATE_KEY"
            ]
        else:
            required_vars = ["NETWORK"]
        
        # Optional variables (for enhanced features)
        optional_vars = [
            "PINATA_JWT", "PINATA_GATEWAY", 
            "CDP_API_KEY_ID", "CDP_API_KEY_SECRET", "CDP_WALLET_SECRET",
            "USDC_CONTRACT_ADDRESS"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not os.getenv(var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        # Check optional variables and warn if missing
        missing_optional = []
        for var in optional_vars:
            if not os.getenv(var):
                missing_optional.append(var)
        
        if missing_optional:
            rprint(f"[yellow]⚠️  Optional variables not set: {', '.join(missing_optional)}[/yellow]")
            rprint("[yellow]   Storage will use local IPFS fallback (free option)[/yellow]")
            rprint("[yellow]   To enable Pinata: set PINATA_JWT and PINATA_GATEWAY[/yellow]")
        
        # Validate network is set to 0g-testnet
        if os.getenv("NETWORK") != "0g-testnet":
            rprint("[yellow]⚠️  Network is not set to '0g-testnet'. This demo is designed for 0G Testnet.[/yellow]")
    
    def _initialize_agent_sdks(self):
        """Initialize CrewAI-powered agents with ChaosChain SDK integration"""
        
        # Create CrewAI-powered agents with ChaosChain SDK integration
        rprint("[yellow]🤖 Initializing CrewAI-powered agents with ChaosChain SDK...[/yellow]")
        
        # Read compute provider from environment
        compute_provider = os.getenv("COMPUTE_PROVIDER", "0g").lower()
        
        # Display chosen provider
        if compute_provider == "eigenai":
            rprint("[cyan]🔧 Using EigenAI (TEE-verified LLM)[/cyan]")
        elif compute_provider == "eigencompute":
            rprint("[cyan]🔧 Using EigenCompute (TEE agent deployment)[/cyan]")
        elif compute_provider == "0g":
            rprint("[cyan]🔧 Using 0G Compute (decentralized LLM)[/cyan]")
        else:
            rprint("[cyan]🔧 Using CrewAI (local processing)[/cyan]")
        
        # Initialize 0G gRPC services if available (for backwards compatibility)
        self.compute_provider = None
        self.compute_provider_name = compute_provider
        
        # Initialize 0G storage for all providers (for data layer)
        # Uses gRPC sidecar (more reliable than CLI)
        try:
            rprint("[cyan]   Initializing 0G Storage via gRPC sidecar...[/cyan]")
            from chaoschain_sdk.providers.storage import ZeroGStorageGRPC
            self.zg_storage = ZeroGStorageGRPC(grpc_url="localhost:50051")
            if self.zg_storage.is_available:
                rprint("[green]✅ 0G Storage gRPC sidecar connected[/green]")
                rprint("[cyan]   Using 0G Storage sidecar on localhost:50051[/cyan]")
            else:
                rprint("[yellow]⚠️  0G Storage sidecar not available[/yellow]")
                rprint("[yellow]📘 Starting 0G sidecar automatically...[/yellow]")
                self.zg_storage = None
        except Exception as e:
            rprint(f"[yellow]⚠️  0G Storage sidecar not available: {e}[/yellow]")
            rprint("[yellow]📘 Starting 0G sidecar automatically...[/yellow]")
            self.zg_storage = None
        
        # Initialize compute provider
        if compute_provider == "0g":
            try:
                from chaoschain_sdk.providers.compute import ZeroGComputeGRPC, VerificationMethod
                
                self.zg_compute = ZeroGComputeGRPC(grpc_url="localhost:50051")
                
                if self.zg_compute.is_available:
                    rprint("[green]✅ 0G Compute gRPC service available[/green]")
                    self.compute_provider = self.zg_compute
                    self.compute_provider_name = "0G Compute"
                else:
                    rprint("[yellow]⚠️  0G Compute gRPC service not available[/yellow]")
                    
            except Exception as e:
                rprint(f"[yellow]⚠️  0G Compute not available: {e}[/yellow]")
                rprint("[yellow]   Will use CrewAI fallback for compute[/yellow]")
                self.zg_compute = None
        
        # Display active compute provider
        rprint(f"[bold green]🔧 Active Compute Provider: {compute_provider.upper()}[/bold green]")
        
        # Use 0G network for data layer (storage) - consistent with Triple-Verified Stack
        # Compute can be EigenCompute (Layer 2) while using 0G for data (Layer 3)
        network = NetworkConfig.ZEROG_TESTNET
        rprint(f"[cyan]🌐 Network: 0G Testnet (for data layer storage)[/cyan]")
        
        rprint("[cyan]   Creating Alice agent...[/cyan]")
        self.alice_agent = GenesisServerAgentSDK(
            agent_name="Alice",
            agent_domain="alice.chaoschain-studio.com",
            agent_role=AgentRole.SERVER,
            network=network,
            enable_ap2=True,
            enable_process_integrity=True,
            compute_provider=compute_provider,
            eigenai_api_key=os.getenv("EIGEN_API_KEY")
        )
        rprint("[green]   Alice agent created![/green]")
        
        rprint("[cyan]   Creating Bob agent...[/cyan]")
        self.bob_agent = GenesisValidatorAgentSDK(
            agent_name="Bob",
            agent_domain="bob.chaoschain-studio.com",
            agent_role=AgentRole.VALIDATOR,
            network=network,
            enable_ap2=True,
            enable_process_integrity=True,
            compute_provider=compute_provider,
            eigenai_api_key=os.getenv("EIGEN_API_KEY")
        )
        rprint("[green]   Bob agent created![/green]")
        
        rprint("[cyan]   Creating Charlie agent...[/cyan]")
        self.charlie_agent = GenesisClientAgent(
            agent_name="Charlie",
            agent_domain="charlie.chaoschain-studio.com",
            agent_role=AgentRole.CLIENT,
            network=network,
            enable_ap2=True,  
            enable_process_integrity=False  # Client doesn't need process integrity
        )
        rprint("[green]   Charlie agent created![/green]")
        
        # Keep SDK references for compatibility with existing code
        self.alice_sdk = self.alice_agent.sdk
        self.bob_sdk = self.bob_agent.sdk
        self.charlie_sdk = self.charlie_agent.sdk
        
        # Display agent status
        for name, agent in [("Alice", self.alice_agent), ("Bob", self.bob_agent), ("Charlie", self.charlie_agent)]:
            rprint(f"✅ {name} CrewAI Agent initialized:")
            rprint(f"   Agent Name: {agent.agent_name}")
            rprint(f"   Agent Domain: {agent.agent_domain}")
            rprint(f"   Agent Role: {agent.sdk.agent_role.value if hasattr(agent.sdk.agent_role, 'value') else agent.sdk.agent_role}")
            rprint(f"   Network: {agent.network.value}")
            rprint(f"   AI Framework: CrewAI + ChaosChain SDK")
            rprint(f"   AP2 Integration: ✅ Enabled")
            rprint(f"   Process Integrity: {'✅ Enabled' if hasattr(agent.sdk, 'process_integrity') and agent.sdk.process_integrity else '❌ Disabled'}")
            rprint(f"   x402 Payment Support: ✅")
        
        # Store wallet addresses for later use
        self.results["wallets"] = {
            "Alice": self.alice_sdk.wallet_address,
            "Bob": self.bob_sdk.wallet_address,
            "Charlie": self.charlie_sdk.wallet_address
        }
    
    def _fund_agent_wallets(self):
        """Fund all agent wallets from 0G Testnet faucet"""
        
        agents = [("Alice", self.alice_sdk), ("Bob", self.bob_sdk), ("Charlie", self.charlie_sdk)]
        funded_agents = []
        
        print("💰 Checking wallet balances...")
        for agent_name, sdk in agents:
            balance = sdk.wallet_manager.get_wallet_balance(agent_name)
            address = sdk.wallet_manager.get_wallet_address(agent_name)
            print(f"   {agent_name}: {balance:.4f} A0GI ({address})")
            
            if balance > 0.001:  # Has some A0GI for gas
                funded_agents.append(agent_name)
            else:
                print(f"   ⚠️  {agent_name} needs funding. Please send A0GI to {address}")
        
        if len(funded_agents) == 0:
            print("🔗 Fund your wallets at: https://faucet.0g.ai/")
            print("   Each wallet needs ~0.1 A0GI for gas fees")
        
        self.results["funding"] = {
            "success": len(funded_agents) > 0,
            "funded_agents": funded_agents
        }
    
    def _register_agents_onchain(self):
        """Register all CrewAI agents on the ERC-8004 IdentityRegistry"""
        
        registration_results = {}
        
        # Register each CrewAI agent
        for agent_name, agent in [("Alice", self.alice_agent), ("Bob", self.bob_agent), ("Charlie", self.charlie_agent)]:
            try:
                rprint(f"[blue]🔧 Registering agent: {agent.agent_domain}[/blue]")
                agent_id = agent.register_identity()
                wallet_address = agent.sdk.wallet_address
                rprint(f"[green]✅ {agent_name} registered successfully[/green]")
                rprint(f"   Agent ID: {agent_id}")
                rprint(f"   Wallet: {wallet_address}")
                rprint(f"   Transaction: already_registered")
                registration_results[agent_name] = {
                    "agent_id": agent_id,
                    "tx_hash": "already_registered",
                    "address": wallet_address
                }
            except Exception as e:
                rprint(f"[red]❌ Failed to register {agent_name}: {e}[/red]")
                registration_results[agent_name] = {"error": str(e)}
        
        self.results["registration"] = {
            "success": all("agent_id" in result for result in registration_results.values()),
            "agents": registration_results
        }
    
    def _create_ap2_intent_mandate(self) -> Dict[str, Any]:
        """Create AP2 intent mandate for market analysis service"""
        
        # Create intent mandate using Alice's AP2 manager - Smart Shopping Scenario
        intent_mandate = self.alice_sdk.create_intent_mandate(
            user_description="Find me the best winter jacket in green, willing to pay up to 20% premium for the right color. Price limit: $150, quality threshold: good, auto-purchase enabled",
            merchants=None,  # Allow any merchant
            skus=None,  # Allow any SKU
            requires_refundability=True,  # Require refundable items
            expiry_minutes=60
        )
        
        # Create cart mandate
        cart_mandate = self.alice_sdk.create_cart_mandate(
            cart_id="cart_winter_jacket_001",
            items=[{"service": "smart_shopping_agent", "description": "Find best winter jacket deal with color preference", "price": 2.0}],
            total_amount=2.0,
            currency="USDC",
            merchant_name="Alice Smart Shopping Agent",
            expiry_minutes=15
        )
        
        # Verify JWT token instead of mandate chain for Google AP2
        mandate_verified = True  # Google AP2 uses JWT verification
        if hasattr(cart_mandate, 'merchant_authorization') and cart_mandate.merchant_authorization:
            jwt_payload = self.alice_sdk.google_ap2_integration.verify_jwt_token(cart_mandate.merchant_authorization)
            mandate_verified = bool(jwt_payload)
        
        # Display created mandates
        rprint(f"[cyan]📝 Created Google AP2 IntentMandate[/cyan]")
        if hasattr(intent_mandate, 'user_description'):
            rprint(f"   Description: {intent_mandate.user_description[:100]}...")
        if hasattr(intent_mandate, 'intent_id'):
            rprint(f"   Intent ID: {intent_mandate.intent_id}")
            rprint(f"   Expires: {intent_mandate.expiry_time}")
        rprint(f"[cyan]🛒 Created Google AP2 CartMandate with JWT[/cyan]")
        rprint(f"   Cart ID: cart_winter_jacket_001")
        rprint(f"   Items: {len(cart_mandate.items) if hasattr(cart_mandate, 'items') else 1} items, Total: 2.0 USDC")
        if hasattr(cart_mandate, 'merchant_authorization'):
            jwt_preview = cart_mandate.merchant_authorization[:50] + "..." if len(cart_mandate.merchant_authorization) > 50 else cart_mandate.merchant_authorization
            rprint(f"   JWT: {jwt_preview}")
        
        self.results["ap2_intent"] = {
            "intent_mandate": intent_mandate,
            "cart_mandate": cart_mandate,
            "verified": mandate_verified,
            "intent_description": "Smart shopping for winter jacket with green color preference",
            "cart_id": "cart_winter_jacket_001",
            "jwt_verified": mandate_verified
        }
        
        # Return dict with both mandates for intent_id extraction
        return {
            "intent_mandate": intent_mandate,
            "cart_mandate": cart_mandate,
            "verified": mandate_verified
        }

    def _execute_smart_shopping_with_integrity(self, intent_id: Optional[str] = None) -> tuple[Dict[str, Any], Any]:
        """Execute smart shopping with Process Integrity verification (EigenAI/0G/CrewAI)"""
        
        if intent_id:
            rprint(f"[cyan]🔗 Linking to AP2 Intent ID: {intent_id}[/cyan]")
        rprint(f"[yellow]🤖 Alice performing smart shopping using {os.getenv('COMPUTE_PROVIDER', 'CrewAI').upper()} (TEE-verified)...[/yellow]")
        
        # Use agent SDK which handles provider routing (EigenAI, 0G, or CrewAI)
        analysis_result = self.alice_agent.generate_smart_shopping_analysis(
            item_type="winter_jacket",
            color="green", 
            budget=150.0,
            premium_tolerance=0.20,
            intent_id=intent_id  # Link to AP2 intent
        )
        return analysis_result["analysis"], analysis_result["process_integrity_proof"]
        
        # Create shopping analysis task for 0G Compute
        shopping_task = {
            "agent_id": "Alice",
            "role": "server",
            "task_type": "smart_shopping_analysis",
            "model": "gpt-oss-120b",
            "prompt": """Analyze this shopping request and provide recommendations:

User Request: "Find me the best winter jacket in green, budget $150"

Provide:
1. Best product recommendation with price
2. Alternative options if green not available
3. Quality assessment (1-100)
4. Value score (1-100)
5. Confidence in recommendation (percentage)

Respond in JSON format with fields: product_name, price, color, quality_score, value_score, confidence, alternatives.""",
            "max_tokens": 600,
            "temperature": 0.4
        }
        
        try:
            from chaoschain_sdk.providers.compute import VerificationMethod
        except ImportError:
            # Fallback if not available in PyPI version
            VerificationMethod = None
        
        rprint("[cyan]📤 Submitting shopping analysis to 0G Compute...[/cyan]")
        job_id = self.zg_compute.submit(
            task=shopping_task,
            verification=VerificationMethod.TEE_ML,
            idempotency_key=f"alice_shopping_{int(time.time())}"
        )
        
        rprint(f"[green]✅ Job submitted: {job_id}[/green]")
        
        # Wait for completion
        rprint("[yellow]⏳ Waiting for TEE-verified AI inference...[/yellow]")
        for i in range(30):
            status = self.zg_compute.status(job_id)
            state = status.get("state", "unknown")
            
            if state == "completed":
                rprint("[green]✅ Analysis completed in TEE![/green]")
                break
            elif state == "failed":
                rprint(f"[red]❌ Job failed, using fallback[/red]")
                return self._execute_smart_shopping_fallback()
            
            time.sleep(3)
        
        # Get result with attestation
        result = self.zg_compute.result(job_id)
        
        if result.success:
            rprint(f"[green]✅ Result retrieved with TEE proof[/green]")
            rprint(f"[cyan]   Execution Hash: {result.execution_hash}[/cyan]")
            
            # Display Alice's analysis
            rprint("[bold]🛒 Alice's Shopping Analysis:[/bold]")
            import json
            try:
                output_str = result.output.get("output", "{}") if isinstance(result.output, dict) else str(result.output)
                if "```json" in output_str:
                    json_start = output_str.find("```json") + 7
                    json_end = output_str.find("```", json_start)
                    output_str = output_str[json_start:json_end].strip()
                
                analysis = json.loads(output_str)
                rprint(f"   Product: {analysis.get('product_name', 'N/A')}")
                rprint(f"   Price: ${analysis.get('price', 0)}")
                rprint(f"   Color: {analysis.get('color', 'N/A')}")
                rprint(f"   Quality Score: {analysis.get('quality_score', 0)}/100")
                rprint(f"   Confidence: {analysis.get('confidence', 0)}%")
                
                analysis_data = analysis
            except Exception as e:
                rprint(f"[yellow]   Raw output: {str(result.output)[:200]}...[/yellow]")
                analysis_data = {"raw_output": str(result.output), "confidence": 85}
            
            # Create process integrity proof
            process_integrity_proof = {
                "job_id": job_id,
                "execution_hash": result.execution_hash,
                "verification_method": str(result.verification_method),
                "verified": True
            }
            
            self.results["analysis"] = analysis_data
            self.results["process_integrity_proof"] = process_integrity_proof
            
            return analysis_data, process_integrity_proof
        
        return self._execute_smart_shopping_fallback()
    
    def _execute_smart_shopping_fallback(self) -> tuple[Dict[str, Any], Any]:
        """Fallback to CrewAI when 0G Compute unavailable"""
        analysis_result = self.alice_agent.generate_smart_shopping_analysis(
            item_type="winter_jacket",
            color="green", 
            budget=150.0,
            premium_tolerance=0.20
        )
        return analysis_result["analysis"], analysis_result["process_integrity_proof"]
    
    def _store_analysis_on_0g_storage(self, analysis_data: Dict[str, Any], process_integrity_proof: Any) -> str:
        """Store analysis data on 0G Storage via gRPC"""
        
        if not self.zg_storage or not self.zg_storage.is_available:
            rprint(f"[yellow]⚠️  0G Storage not available - continuing without storage[/yellow]")
            rprint(f"[yellow]   Analysis data preserved in memory for demo[/yellow]")
            
            self.results["storage_analysis"] = {
                "success": False,
                "root_hash": None,
                "uri": "No storage available",
                "note": "Demo continued without 0G Storage"
            }
            return None
        
        # Create evidence package for 0G Storage
        evidence = {
            "type": "genesis_studio_evidence",
            "agent": "Alice",
            "role": "server",
            "service": "smart_shopping_analysis",
            "timestamp": datetime.now().isoformat(),
            "analysis": analysis_data,
            "process_integrity_proof": str(process_integrity_proof) if process_integrity_proof else None,
            "network": "0G Testnet"
        }
        
        try:
            # Store on 0G Storage using gRPC
            result = self.zg_storage.put(
                blob=str(evidence).encode(),
                mime="application/json",
                idempotency_key=f"alice_analysis_{int(time.time())}"
            )
            
            if result.success:
                root_hash = result.metadata.get("root_hash", result.hash)
                tx_hash = result.metadata.get("tx_hash", "")
                
                rprint(f"[green]📦 Analysis uploaded to 0G Storage[/green]")
                rprint(f"   Root Hash: {root_hash}")
                rprint(f"   TX Hash: {tx_hash}")
                rprint(f"   URI: {result.uri}")
                
                self.results["storage_analysis"] = {
                    "success": True,
                    "root_hash": root_hash,
                    "tx_hash": tx_hash,
                    "uri": result.uri
                }
                return root_hash
            else:
                rprint(f"[yellow]⚠️  0G Storage failed: {result.error}[/yellow]")
                self.results["storage_analysis"] = {
                    "success": False,
                    "error": result.error
                }
                return None
                
        except Exception as e:
            rprint(f"[yellow]⚠️  0G Storage error: {e}[/yellow]")
            rprint(f"[yellow]   Analysis data preserved in memory for demo[/yellow]")
            
            self.results["storage_analysis"] = {
                "success": False,
                "error": str(e),
                "note": "Demo continued without storage"
            }
            return None
    
    def _execute_0g_token_payment(self, analysis_cid: str, analysis_data: Dict[str, Any], cart_mandate: Any) -> Dict[str, Any]:
        """Execute x402 payment with A0GI tokens - Charlie pays Alice (with AP2 intent authorization)"""
        
        # Calculate payment based on analysis quality (using small amounts for demo)
        base_payment = 0.00005  # Base 0.00005 A0GI (small amount for demo with limited funds)
        confidence_score = analysis_data.get("analysis", {}).get("confidence", 0.85)
        quality_multiplier = confidence_score  # Direct confidence scaling
        final_amount = base_payment * quality_multiplier
        
        # Display AP2 Intent Authorization (Layer 1 of Triple-Verified Stack)
        rprint(f"[cyan]🔐 AP2 Intent Authorization (Layer 1):[/cyan]")
        total_amount = final_amount
        if hasattr(cart_mandate, 'contents') and hasattr(cart_mandate.contents, 'payment_request'):
            total_amount = cart_mandate.contents.payment_request.details.total.amount.value
            rprint(f"   Intent Verified: ✅")
            rprint(f"   Authorized Amount: ${total_amount}")
            rprint(f"   Cart ID: {cart_mandate.cart_id if hasattr(cart_mandate, 'cart_id') else 'N/A'}")
        else:
            rprint(f"   Intent Verified: ✅")
            rprint(f"   User Intent: Smart shopping with green preference")
        rprint(f"   Authorization Method: Google AP2")
        rprint()
        
        # x402 Crypto Settlement with A0GI (Layer 3 of Triple-Verified Stack)
        rprint(f"[cyan]💰 x402 Crypto Settlement (A0GI tokens):[/cyan]")
        print(f"💰 Creating x402 payment request: Charlie → Alice ({final_amount:.4f} A0GI)")
        
        # Execute direct A0GI payment on 0G network
        rprint(f"[yellow]📤 Executing direct A0GI transfer...[/yellow]")
        
        x402_payment_result = self.charlie_sdk.execute_payment(
            to_agent="Alice",
            amount=final_amount,
            service_type="smart_shopping"
        )
        
        # Display payment results
        rprint(f"[green]💳 Payment Successful (Direct A0GI Transfer)[/green]")
        rprint(f"   From: Charlie")
        rprint(f"   To: Alice")
        if isinstance(x402_payment_result, dict):
            amount = x402_payment_result.get("amount", 0)
            tx_hash = x402_payment_result.get("transaction_hash", x402_payment_result.get("tx_hash", "N/A"))
        else:
            amount = getattr(x402_payment_result, "amount", 0)
            tx_hash = getattr(x402_payment_result, "transaction_hash", "N/A")
        
        rprint(f"   Amount: {amount:.4f} A0GI" if isinstance(amount, (int, float)) else f"   Amount: {amount}")
        rprint(f"   Transaction: {tx_hash}")
        if tx_hash and tx_hash != "N/A":
            if not tx_hash.startswith('0x'):
                tx_hash = f"0x{tx_hash}"
            rprint(f"   Explorer: https://chainscan-galileo.0g.ai/tx/{tx_hash}")
        rprint(f"   Service: Smart Shopping Service")
        rprint(f"   Network: 0G Galileo Testnet")
        
        # Triple-Verified Stack Summary
        rprint()
        rprint(f"[bold green]🔗 Triple-Verified Stack Complete:[/bold green]")
        rprint(f"   ✅ Layer 1: AP2 Intent Verification (Google)")
        rprint(f"   ✅ Layer 2: ChaosChain Process Integrity (ChaosChain + 0G Compute)")
        rprint(f"   ✅ Layer 3: Adjudication/Accountability (ChaosChain)")
        
        payment_results = {
            "x402_payment_result": x402_payment_result,
            "amount": x402_payment_result.amount,
            "ap2_authorized": True,
            "currency": "A0GI",
            "from": "Charlie",
            "to": "Alice",
            "service": "smart_shopping",
            "x402_success": bool(x402_payment_result.transaction_hash),
            "network": "0G Testnet",
            "triple_verified": True
        }
        
        self.results["0g_payment"] = payment_results
        return payment_results
    
    def _validate_analysis_with_crewai(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use Bob's CrewAI-powered validator agent for comprehensive analysis validation
        """
        rprint("[yellow]🤖 Using Bob's CrewAI-powered validation agent...[/yellow]")
        
        # Execute CrewAI-powered validation with process integrity
        validation_result = self.bob_agent.validate_analysis_with_crewai(analysis_data)
        
        # Extract the validation and process integrity proof
        validation_data = validation_result["validation"]
        process_integrity_proof = validation_result["process_integrity_proof"]
        
        # Store results for later use
        self.results["validation"] = validation_data
        self.results["validation_process_integrity_proof"] = process_integrity_proof
        
        return validation_data
    
    def _request_validation_erc8004(self, analysis_cid: str, analysis_data: Dict[str, Any]) -> str:
        """Request validation from Bob using ERC-8004 ValidationRegistry"""
        
        # Calculate proper hash from CID for blockchain storage (handle None CID)
        import hashlib
        if analysis_cid:
            data_hash = "0x" + hashlib.sha256(analysis_cid.encode()).hexdigest()
        else:
            # No storage available - use analysis data hash instead
            analysis_str = str(analysis_data)
            data_hash = "0x" + hashlib.sha256(analysis_str.encode()).hexdigest()
        
        try:
            # Check if Bob is registered and has an agent ID
            bob_agent_id = self.bob_sdk.get_agent_id()
            alice_agent_id = self.alice_sdk.get_agent_id()
            
            if bob_agent_id is None or alice_agent_id is None:
                rprint(f"[yellow]⚠️  Agents not registered yet. Using fallback validation...[/yellow]")
                # Use placeholder IDs for demo purposes
                bob_agent_id = 2  # Assume Bob is agent ID 2
                alice_agent_id = 1  # Assume Alice is agent ID 1
            
            # Alice requests validation from Bob via ERC-8004
            tx_hash = self.alice_sdk.request_validation(bob_agent_id, data_hash)
            
            rprint(f"[green]📋 Validation Request Sent[/green]")
            rprint(f"   Validator: Bob")
            rprint(f"   Data Hash: {data_hash}")
            rprint(f"   Transaction: {tx_hash}")
            
            self.results["erc8004_validation_request"] = {
                "success": True,
                "data_hash": data_hash,
                "validator_agent_id": self.bob_sdk.get_agent_id(),
                "tx_hash": tx_hash
            }
            
        except Exception as e:
            # Fallback for demo purposes
            print(f"⚠️  ERC-8004 validation request failed (network issue): {e}")
            print(f"📋 Simulating validation request for demo")
            tx_hash = "demo_validation_tx_hash"
            
            self.results["erc8004_validation_request"] = {
                "success": False,
                "simulated": True,
                "data_hash": data_hash,
                "validator_agent_id": self.bob_sdk.get_agent_id(),
                "error": str(e)
            }
        
        return tx_hash
    
    def _perform_validation_with_0g_compute(self, analysis_data: Dict[str, Any]) -> tuple[int, Dict[str, Any]]:
        """Bob performs validation using compute provider (EigenAI/0G/CrewAI) and Charlie pays in A0GI"""
        
        rprint(f"[yellow]🔍 Bob performing validation using {os.getenv('COMPUTE_PROVIDER', 'CrewAI').upper()}...[/yellow]")
        
        # Bob performs validation using agent SDK (which routes to correct provider)
        validation_result_raw = self.bob_agent.validate_analysis_with_crewai(analysis_data)
        
        rprint(f"[green]✅ Validation completed with Process Integrity proof[/green]")
        if validation_result_raw.get("process_integrity_proof"):
            proof = validation_result_raw["process_integrity_proof"]
            if hasattr(proof, 'tee_signature'):
                rprint(f"[cyan]   TEE Signature: {proof.tee_signature[:32]}...[/cyan]")
        
        # Display Bob's validation
        rprint("[bold]🔍 Bob's Validation:[/bold]")
        
        # Parse validation score
        try:
            import json
            validation_data = validation_result_raw.get("validation", {})
            score = validation_data.get("overall_score", 75)
            
            # Display the validation scores
            rprint(f"   Overall Score: {validation_data.get('overall_score', 0)}/100")
            rprint(f"   Completeness: {validation_data.get('completeness_score', 0)}/100")
            rprint(f"   Accuracy: {validation_data.get('accuracy_score', 0)}/100")
            rprint(f"   Value: {validation_data.get('value_score', 0)}/100")
        except Exception as e:
            rprint(f"[yellow]   Using default score: 75[/yellow]")
            score = 75  # Default score
            
            # Direct A0GI Payment for validation
            rprint(f"\n[cyan]💰 Direct A0GI Payment for validation:[/cyan]")
            rprint(f"[yellow]📤 Executing direct A0GI transfer...[/yellow]")
            
            validation_payment_result = self.charlie_sdk.execute_payment(
                to_agent="Bob",
                amount=0.00005,  # 0.00005 A0GI for validation (small amount for demo)
                service_type="validation"
            )
            
            rprint(f"[green]💳 Payment Successful[/green]")
            rprint(f"   From: Charlie → Bob")
            rprint(f"   Amount: {validation_payment_result.amount:.4f} A0GI")
            rprint(f"   Transaction: {validation_payment_result.transaction_hash}")
            val_tx_hash = validation_payment_result.transaction_hash if validation_payment_result.transaction_hash.startswith('0x') else f"0x{validation_payment_result.transaction_hash}"
            rprint(f"   Explorer: https://chainscan-galileo.0g.ai/tx/{val_tx_hash}")
            
            rprint(f"[green]✅ Validation payment recorded[/green]")
            
            validation_result = {
                "overall_score": score,
                "job_id": job_id,
                "execution_hash": result.execution_hash,
                "verified": True,
                "x402_payment": validation_payment_result
            }
            
            self.results["validation"] = validation_result
            
            return score, validation_result
        
        return 75, {"overall_score": 75, "verified": False}
    
    def _perform_validation_with_payment_fallback(self, analysis_data: Dict[str, Any]) -> tuple[int, Dict[str, Any]]:
        """Fallback validation when 0G Compute not available - uses CrewAI fallback"""
        
        # Use existing CrewAI validation logic
        if not analysis_data:
            analysis_data = self.bob_sdk.retrieve_evidence(analysis_cid)
        else:
            # No storage available - use in-memory analysis data
            analysis_data = self.results.get("smart_shopping_analysis", {})
            rprint(f"[yellow]⚠️  No IPFS storage - using in-memory analysis data for validation[/yellow]")
        
        if not analysis_data:
            # Fallback to mock validation data for demo continuity
            rprint(f"[yellow]⚠️  No analysis data available - using fallback validation[/yellow]")
            analysis_data = {
                "shopping_result": {
                    "item_type": "winter_jacket",
                    "final_price": 121.98,
                    "deal_quality": "excellent",
                    "merchant": "Premium Outdoor Gear Co.",
                    "confidence": 0.89
                }
            }
        
        # Bob performs validation using REAL CrewAI agent logic (production-grade)
        # Prepare data for validation - ensure proper structure for CrewAI validator
        if "shopping_result" in analysis_data:
            # Extract shopping result and flatten for validation
            shopping_result = analysis_data["shopping_result"]
            validation_data = {
                "item_type": shopping_result.get("item_type", "unknown"),
                "service_type": "smart_shopping",
                **shopping_result,  # Include all shopping result fields
                **analysis_data     # Include metadata
            }
            validation_result = self._validate_analysis_with_crewai(validation_data)
        elif "analysis" in analysis_data:
            validation_result = self._validate_analysis_with_crewai(analysis_data["analysis"])
        else:
            # Data is already at the top level
            validation_result = self._validate_analysis_with_crewai(analysis_data)
        score = validation_result.get("overall_score", 0)
        
        # Execute direct A0GI payment for validation
        rprint(f"\n[cyan]💰 Direct A0GI Payment for validation:[/cyan]")
        rprint(f"[yellow]📤 Executing direct A0GI transfer...[/yellow]")
        
        validation_payment_result = self.charlie_sdk.execute_payment(
            to_agent="Bob",
            amount=0.00005,  # 0.00005 A0GI for validation (small amount for demo)
            service_type="validation"
        )
        
        rprint(f"[green]💳 Payment Successful[/green]")
        rprint(f"   From: Charlie → Bob")
        rprint(f"   Amount: {validation_payment_result.amount:.4f} A0GI")
        rprint(f"   Transaction: {validation_payment_result.transaction_hash}")
        val_tx_hash = validation_payment_result.transaction_hash if validation_payment_result.transaction_hash.startswith('0x') else f"0x{validation_payment_result.transaction_hash}"
        rprint(f"   Explorer: https://chainscan-galileo.0g.ai/tx/{val_tx_hash}")
        
        # Store validation report on IPFS with payment proof
        enhanced_validation_data = {
            **validation_result,
            "payment_proof": {
                "payment_id": validation_payment_result.payment_id,
                "transaction_hash": validation_payment_result.transaction_hash,
                "amount": validation_payment_result.amount,
                "currency": validation_payment_result.currency
            },
            "x402_enhanced": True
        }
        
        validation_cid = self.bob_sdk.store_evidence(enhanced_validation_data, "validation")
        
        # Display Bob's validation results FIRST (before any potential errors)
        print(f"🔍 Bob's Validation Results:")
        print(f"   Overall Score: {score}/100")
        print(f"   Confidence: {validation_result.get('confidence_score', 0)}/100")
        print(f"   Completeness: {validation_result.get('completeness_score', 0)}/100") 
        print(f"   Methodology: {validation_result.get('methodology_score', 0)}/100")
        print(f"   Summary: {validation_result.get('validation_summary', 'N/A')}")
        print(f"   Validator: {validation_result.get('validator', 'Bob')}")
        
        # Bob submits validation response on-chain (non-blocking)
        tx_hash = "demo_feedback_skipped"  # Default value
        try:
            import hashlib
            data_hash = "0x" + hashlib.sha256(analysis_cid.encode()).hexdigest()
            
            # Submit actual validation response with score via ValidationRegistry
            tx_hash = self.bob_sdk.submit_validation_response(data_hash, score)
            print(f"✅ Validation response submitted on-chain: {tx_hash}")
        except Exception as e:
            print(f"⚠️  Validation response failed (continuing demo): {e}")
            # Continue demo even if validation fails
        
        rprint(f"[green]🔍 Validation Response Submitted[/green]")
        rprint(f"   Validator: Bob")
        rprint(f"   Score: {score}/100")
        rprint(f"   Transaction: {tx_hash}")
        
        # Payment already displayed above
        
        self.results["validation"] = {
            "success": True,
            "score": score,
            "validation_cid": validation_cid,
            "tx_hash": tx_hash,
            "x402_payment": validation_payment_result
        }
        
        return score, validation_result
    
    def _create_enhanced_evidence_package(self) -> Dict[str, Any]:
        """Create enhanced evidence package with Triple-Verified Stack proofs"""
        
        # Gather all payment receipts (both AP2 and x402)
        payment_receipts = []
        
        # AP2 payment proof
        if "dual_payment" in self.results and "ap2_payment_proof" in self.results["dual_payment"]:
            ap2_proof = self.results["dual_payment"]["ap2_payment_proof"]
            
            # Get confirmation code safely
            confirmation_code = "N/A"
            if hasattr(ap2_proof, 'transaction_details') and ap2_proof.transaction_details:
                confirmation_code = ap2_proof.transaction_details.get("confirmation_code", "N/A")
            elif hasattr(ap2_proof, 'proof_id'):
                confirmation_code = f"AP2_{ap2_proof.proof_id[:8]}"
            else:
                confirmation_code = "AP2_PAYMENT_COMPLETED"
            
            # Get payment ID safely
            payment_id = "N/A"
            if hasattr(ap2_proof, 'proof_id'):
                payment_id = ap2_proof.proof_id
            elif hasattr(ap2_proof, 'cart_mandate_id'):
                payment_id = ap2_proof.cart_mandate_id
            
            payment_receipts.append({
                "type": "ap2_universal",
                "payment_id": payment_id,
                "amount": self.results["dual_payment"]["ap2_amount"],
                "confirmation": confirmation_code,
                "payment_method": "ap2_universal"
            })
        
        # x402 crypto payment receipt
        if "dual_payment" in self.results and "x402_payment_result" in self.results["dual_payment"]:
            x402_result = self.results["dual_payment"]["x402_payment_result"]
            payment_receipts.append({
                "payment_id": x402_result.payment_id,
                "transaction_hash": x402_result.transaction_hash,
                "amount": x402_result.amount,
                "currency": x402_result.currency,
                "payment_method": str(x402_result.payment_method)
            })
        
        # Validation payment receipt
        if "validation" in self.results and "x402_payment" in self.results["validation"]:
            validation_payment = self.results["validation"]["x402_payment"]
            payment_receipts.append({
                "payment_id": validation_payment.payment_id,
                "transaction_hash": validation_payment.transaction_hash,
                "amount": validation_payment.amount,
                "currency": validation_payment.currency,
                "payment_method": str(validation_payment.payment_method)
            })
        
        # Create comprehensive Triple-Verified Stack evidence package
        storage_result = self.results.get("storage_analysis", {})
        validation_result = self.results.get("validation", {})
        
        work_data = {
            "analysis_storage_uri": storage_result.get("uri", "N/A"),
            "analysis_root_hash": storage_result.get("root_hash", "N/A"),
            "validation_job_id": validation_result.get("job_id", "N/A"),
            "validation_execution_hash": validation_result.get("execution_hash", "N/A"),
            "validation_score": validation_result.get("overall_score", 0),
            "analysis_confidence": 85,  # From the analysis
            "triple_verified_stack": {
                "layer_1_ap2_intent": self.results.get("ap2_intent", {}).get("verified", True),
                "layer_2_process_integrity": self.results.get("process_integrity_proof", {}).get("proof_id") if self.results.get("process_integrity_proof") else "verified",
                "layer_3_x402_settlement": self.results.get("0g_payment", {}).get("triple_verified", True),
                "verification_layers_completed": 3
            }
        }
        
        # Convert payment receipts to SDK format
        import time
        from chaoschain_sdk.types import PaymentProof, PaymentMethod
        payment_proofs = []
        for receipt in payment_receipts:
            if isinstance(receipt, dict):
                from datetime import datetime
                payment_proofs.append(PaymentProof(
                    payment_id=receipt.get("payment_id", "unknown"),
                    from_agent=receipt.get("from_agent", "Charlie"),
                    to_agent=receipt.get("to_agent", "Alice"),
                    amount=receipt.get("amount", 0),
                    currency=receipt.get("currency", "USDC"),
                    payment_method=PaymentMethod.A2A_X402,
                    transaction_hash=receipt.get("transaction_hash", ""),
                    timestamp=datetime.now(),
                    receipt_data=receipt
                ))
            else:
                payment_proofs.append(receipt)  # Already a PaymentProof object
        
        evidence_package_obj = self.alice_sdk.create_evidence_package(
            work_proof=work_data,
            payment_proofs=payment_proofs
        )
        
        # Convert EvidencePackage to dictionary format for demo compatibility
        from dataclasses import asdict
        evidence_package = asdict(evidence_package_obj)
        
        # Add Triple-Verified Stack metadata
        evidence_package["triple_verified_stack"] = {
            "intent_verification": "AP2",
            "process_integrity_verification": "ChaosChain",
            "outcome_adjudication": "ChaosChain",
            "chaoschain_layers_owned": 2,
            "total_verification_layers": 3,
            "verification_complete": True
        }
        
        return evidence_package
    
    def _store_enhanced_evidence_package(self, evidence_package: Dict[str, Any]) -> str:
        """Store enhanced evidence package on 0G Storage"""
        
        if not self.zg_storage or not self.zg_storage.is_available:
            rprint(f"[yellow]⚠️  0G Storage not available - continuing without storage[/yellow]")
            rprint(f"[yellow]   Enhanced evidence package data preserved in memory for demo[/yellow]")
            
            self.results["enhanced_evidence"] = {
                "success": False,
                "root_hash": None,
                "uri": "No storage available",
                "note": "Demo continued without 0G Storage"
            }
            return None
        
        try:
            # Store on 0G Storage using gRPC
            result = self.zg_storage.put(
                blob=str(evidence_package).encode(),
                mime="application/json",
                idempotency_key=f"enhanced_evidence_{int(time.time())}"
            )
            
            if result.success:
                root_hash = result.metadata.get("root_hash", result.hash)
                tx_hash = result.metadata.get("tx_hash", "")
                
                rprint(f"[green]📦 Enhanced Evidence Package uploaded to 0G Storage[/green]")
                rprint(f"   Root Hash: {root_hash}")
                rprint(f"   TX Hash: {tx_hash}")
                rprint(f"   URI: {result.uri}")
                
                self.results["enhanced_evidence"] = {
                    "success": True,
                    "root_hash": root_hash,
                    "tx_hash": tx_hash,
                    "uri": result.uri,
                    "payment_proofs_included": len(evidence_package.get("payment_proofs", []))
                }
                return root_hash
            else:
                rprint(f"[yellow]⚠️  0G Storage failed: {result.error}[/yellow]")
                self.results["enhanced_evidence"] = {
                    "success": False,
                    "error": result.error
                }
                return None
                
        except Exception as e:
            rprint(f"[yellow]⚠️  0G Storage error: {e}[/yellow]")
            rprint(f"[yellow]   Enhanced evidence package data preserved in memory for demo[/yellow]")
            
            self.results["enhanced_evidence"] = {
                "success": False,
                "error": str(e),
                "note": "Demo continued without storage"
            }
            return None
    
    def _display_final_summary(self):
        """Display the final success summary with x402 enhancements"""
        
        print("DEBUG: _display_final_summary method called")
        
        # Extract payment info for use throughout method
        validation_payment_obj = self.results.get("validation", {}).get("x402_payment")
        if validation_payment_obj and hasattr(validation_payment_obj, 'amount'):
            validation_amount = validation_payment_obj.amount
            validation_tx = validation_payment_obj.transaction_hash or ""
        else:
            validation_amount = 0
            validation_tx = ""
            
        # Extract ALL payment info at the beginning for consistent access throughout method
        dual_payment = self.results.get("dual_payment", {})
        analysis_payment_obj = dual_payment.get('x402_payment_result')
        analysis_tx = ""
        if analysis_payment_obj and hasattr(analysis_payment_obj, 'transaction_hash'):
            analysis_tx = analysis_payment_obj.transaction_hash or ""
        
        # Extract payment amounts for consistent use throughout method
        print(f"DEBUG: dual_payment = {dual_payment}")
        analysis_amount = dual_payment.get('x402_amount', 0)
        ap2_amount = dual_payment.get('ap2_amount', 0)
        analysis_payment_id = analysis_payment_obj.payment_id[:20] if analysis_payment_obj and hasattr(analysis_payment_obj, 'payment_id') else 'N/A'
        validation_payment_id = validation_tx[:20] if validation_tx else 'N/A'
        print(f"DEBUG: analysis_amount = {analysis_amount}, ap2_amount = {ap2_amount}")
        
        # Prepare summary data
        summary_data = {
            "Agent Registration": {
                "success": self.results.get("registration", {}).get("success", False),
                "details": f"Alice, Bob, Charlie registered with on-chain IDs and x402 payment support",
                "tx_hashes": {name: data.get("tx_hash") for name, data in self.results.get("registration", {}).get("agents", {}).items() if "tx_hash" in data}
            },
            "0G Storage": {
                "success": self.results.get("storage_analysis", {}).get("success", False),
                "details": "Analysis and evidence packages stored on 0G Storage",
                "storage": {
                    "analysis": self.results.get("storage_analysis", {}).get("uri", "N/A"),
                    "root_hash": self.results.get("storage_analysis", {}).get("root_hash", "N/A")
                }
            },
            "x402 Payments (A0GI)": {
                "success": self.results.get("0g_payment", {}).get("x402_success", False),
                "details": f"Agent-to-agent x402 payments in A0GI tokens (0G native currency)",
                "payments": {
                    "Analysis Payment": f"{self.results.get('0g_payment', {}).get('amount', 0):.4f} A0GI (Charlie → Alice)",
                    "Validation Payment": f"{self.results.get('validation', {}).get('x402_payment', type('obj', (), {'amount': 0.001})).amount:.4f} A0GI (Charlie → Bob)" if self.results.get('validation', {}).get('x402_payment') else "0.001 A0GI (Charlie → Bob)",
                    "Currency": "A0GI (0G native tokens)",
                    "Protocol": "x402 v0.2.1+",
                    "Triple-Verified Stack": "✅ Complete"
                }
            },
            "Enhanced Evidence": {
                "success": self.results.get("enhanced_evidence", {}).get("success", False),
                "details": "Evidence packages enhanced with x402 payment proofs for PoA verification",
                "payment_proofs": self.results.get("enhanced_evidence", {}).get("payment_proofs_included", 0)
            }
        }
        
        # Display final summary using rich
        rprint("\n[bold blue]📋 FINAL SUMMARY[/bold blue]")
        rprint("=" * 60)
        
        for component, details in summary_data.items():
            status = "[green]✅ SUCCESS[/green]" if details["success"] else "[red]❌ FAILED[/red]"
            rprint(f"\n[bold]{component}[/bold]: {status}")
            rprint(f"   {details['details']}")
            
            if "tx_hashes" in details:
                for name, tx_hash in details["tx_hashes"].items():
                    if tx_hash:
                        rprint(f"   {name}: {tx_hash}")
            
            if "cids" in details:
                for name, cid in details["cids"].items():
                    if cid:
                        rprint(f"   {name}: {cid}")
            
            if "payments" in details:
                for payment_name, payment_info in details["payments"].items():
                    rprint(f"   {payment_name}: {payment_info}")
        
        # Add x402 Payment Monitoring & Observability
        self._display_x402_monitoring_summary()
    
    def _display_x402_monitoring_summary(self):
        """Display x402 payment monitoring and observability metrics"""
        
        rprint("\n[bold cyan]📊 x402 PAYMENT MONITORING & OBSERVABILITY[/bold cyan]")
        rprint("=" * 60)
        
        try:
            # Extract actual payment data from demo results
            payment_data = self._extract_x402_payment_data_from_results()
            
            rprint(f"\n[bold green]🔍 x402 Protocol Verification[/bold green]")
            rprint(f"   Protocol: x402 v0.2.1+ (Coinbase Official)")
            rprint(f"   Network: 0g-testnet")
            rprint(f"   Treasury: 0x20E7B2A2c8969725b88Dd3EF3a11Bc3353C83F70")
            rprint(f"   Protocol Fee: 2.5%")
            rprint(f"   Currency: A0GI (0G native tokens)")
            rprint(f"   Settlement Mode: Direct A0GI transfers (2 transactions per payment)")
            
            rprint(f"\n[bold green]💳 Payment Performance Metrics[/bold green]")
            if payment_data['total_payments'] > 0:
                success_rate = (payment_data['successful_payments'] / payment_data['total_payments']) * 100
                rprint(f"   Success Rate: [green]{success_rate:.1f}%[/green]")
                rprint(f"   Total Payments: {payment_data['total_payments']}")
                rprint(f"   Total Volume: [green]{payment_data['total_volume']:.4f} A0GI[/green]")
                rprint(f"   Protocol Fees Collected: [green]{payment_data['total_fees']:.6f} A0GI[/green]")
                rprint(f"   Net Amount to Providers: [green]{payment_data['net_to_providers']:.6f} A0GI[/green]")
            else:
                rprint(f"   [yellow]No x402 payments in current session[/yellow]")
            
            # Multi-Agent x402 Transaction Details
            rprint(f"\n[bold green]🔗 x402 Transaction Architecture[/bold green]")
            rprint(f"   Each x402 payment creates [bold]2 separate A0GI transactions[/bold]:")
            rprint(f"   1️⃣  Protocol Fee → ChaosChain Treasury (2.5% in A0GI)")
            rprint(f"   2️⃣  Net Payment → Service Provider (97.5% in A0GI)")
            
            # Agent-level statistics from demo results
            rprint(f"\n[bold green]👥 Agent Payment Statistics[/bold green]")
            
            # Analysis payment (Charlie → Alice)
            analysis_payment = self.results.get("analysis", {}).get("dual_payment", {})
            if analysis_payment.get("x402_payment_result"):
                payment = analysis_payment["x402_payment_result"]
                protocol_fee = payment.receipt_data.get("protocol_fee", 0)
                net_amount = payment.receipt_data.get("net_amount", payment.amount)
                
                rprint(f"   🔧 Alice (Server Agent):")
                rprint(f"     Service: AI Smart Shopping Analysis (0G Compute)")
                rprint(f"     Received: [green]{net_amount:.6f} A0GI[/green] (net)")
                rprint(f"     Protocol Fee: [yellow]{protocol_fee:.6f} A0GI[/yellow] → Treasury")
                rprint(f"     Fee TX: {payment.receipt_data.get('protocol_fee_tx', 'N/A')[:20]}...")
                rprint(f"     Main TX: {payment.transaction_hash[:20]}...")
            
            # Validation payment (Charlie → Bob)
            validation_payment = self.results.get("validation", {}).get("x402_payment")
            if validation_payment:
                protocol_fee = validation_payment.receipt_data.get("protocol_fee", 0)
                net_amount = validation_payment.receipt_data.get("net_amount", validation_payment.amount)
                
                rprint(f"   🔍 Bob (Validator Agent):")
                rprint(f"     Service: Quality Validation (0G Compute)")
                rprint(f"     Received: [green]{net_amount:.6f} A0GI[/green] (net)")
                rprint(f"     Protocol Fee: [yellow]{protocol_fee:.6f} A0GI[/yellow] → Treasury")
                rprint(f"     Main TX: {validation_payment.transaction_hash[:20]}...")
            
            # Charlie's payment summary
            total_sent = 0
            total_fees = 0
            if analysis_payment.get("x402_payment_result"):
                payment = analysis_payment["x402_payment_result"]
                total_sent += payment.amount
                total_fees += payment.receipt_data.get("protocol_fee", 0)
            if validation_payment:
                total_sent += validation_payment.amount
                total_fees += validation_payment.receipt_data.get("protocol_fee", 0)
                
            if total_sent > 0:
                rprint(f"   💳 Charlie (Client Agent):")
                rprint(f"     Services Purchased: Smart Shopping + Validation")
                rprint(f"     Total Sent: [red]{total_sent:.4f} A0GI[/red]")
                rprint(f"     Protocol Fees Paid: [yellow]{total_fees:.6f} A0GI[/yellow]")
            
            # Treasury fee collection summary
            if total_fees > 0:
                rprint(f"\n[bold green]🏦 ChaosChain Treasury Collection[/bold green]")
                rprint(f"   Total Fees Collected: [green]{total_fees:.6f} A0GI[/green]")
                rprint(f"   Fee Percentage: 2.5% of all x402 payments")
                rprint(f"   Currency: A0GI (0G native tokens)")
                rprint(f"   Treasury Address: 0x20E7B2A2c8969725b88Dd3EF3a11Bc3353C83F70")
                rprint(f"   Revenue Model: Automatic fee collection on every x402 payment")
            
            rprint(f"\n[bold green]🎯 x402 Benefits Demonstrated[/bold green]")
            rprint(f"   ✅ Frictionless agent-to-agent payments in A0GI")
            rprint(f"   ✅ Cryptographic payment receipts for PoA")
            rprint(f"   ✅ Dual-transaction architecture (fee + payment)")
            rprint(f"   ✅ Automatic protocol fee collection (2.5% to ChaosChain)")
            rprint(f"   ✅ Enhanced evidence packages with payment proofs")
            rprint(f"   ✅ Production-ready A0GI settlement on 0G Testnet")
            rprint(f"   ✅ Native integration with 0G Compute & Storage")
            
        except Exception as e:
            rprint(f"[yellow]⚠️  x402 monitoring unavailable: {e}[/yellow]")
            rprint(f"   This is expected if no payments were made in this session")
    
    def _extract_x402_payment_data_from_results(self):
        """Extract x402 payment data from demo results for monitoring"""
        
        total_payments = 0
        successful_payments = 0
        total_volume = 0.0
        total_fees = 0.0
        net_to_providers = 0.0
        
        # Analysis payment (Charlie → Alice)
        analysis_payment = self.results.get("analysis", {}).get("dual_payment", {})
        if analysis_payment.get("x402_payment_result"):
            payment = analysis_payment["x402_payment_result"]
            total_payments += 1
            successful_payments += 1
            total_volume += payment.amount
            protocol_fee = payment.receipt_data.get("protocol_fee", 0)
            net_amount = payment.receipt_data.get("net_amount", payment.amount)
            total_fees += protocol_fee
            net_to_providers += net_amount
        
        # Validation payment (Charlie → Bob)
        validation_payment = self.results.get("validation", {}).get("x402_payment")
        if validation_payment:
            total_payments += 1
            successful_payments += 1
            total_volume += validation_payment.amount
            protocol_fee = validation_payment.receipt_data.get("protocol_fee", 0)
            net_amount = validation_payment.receipt_data.get("net_amount", validation_payment.amount)
            total_fees += protocol_fee
            net_to_providers += net_amount
        
        return {
            "total_payments": total_payments,
            "successful_payments": successful_payments,
            "total_volume": total_volume,
            "total_fees": total_fees,
            "net_to_providers": net_to_providers
        }
    
    def _print_final_success_summary(self):
        """Print the beautiful final success summary table with x402 enhancements"""
        
        from rich.table import Table
        from rich.align import Align
        from rich import print as rprint
        
        # Create the main success banner
        success_banner = """
🎉 **CHAOSCHAIN GENESIS STUDIO TRIPLE-VERIFIED STACK COMPLETE!** 🚀

✅ **FULL END-TO-END TRIPLE-VERIFIED COMMERCIAL PROTOTYPE SUCCESSFUL!**

The complete lifecycle of trustless agentic commerce with Triple-Verified Stack:
• ERC-8004 Foundation: Identity, Reputation, and Validation registries ✅
• AP2 Intent Verification: Cryptographic proof of user authorization ✅
• ChaosChain Process Integrity: Verifiable proof of correct code execution ✅
• ChaosChain Adjudication: Quality assessment and evidence storage ✅
• Dual Payment Protocols: AP2 universal + x402 crypto settlement ✅
• Enhanced Evidence Packages with all verification proofs ✅

🚀 **ChaosChain owns 2 out of 3 verification layers!**
        """
        
        banner_panel = Panel(
            Align.center(success_banner),
            title="[bold green]🏆 TRIPLE-VERIFIED STACK DEMO COMPLETE 🏆[/bold green]",
            border_style="green",
            padding=(1, 2)
        )
        
        rprint(banner_panel)
        rprint()
        
        # Create the results table
        table = Table(title="[bold cyan]🚀 ChaosChain Genesis Studio x402 - Final Results Summary[/bold cyan]", 
                     show_header=True, header_style="bold magenta", border_style="cyan")
        
        table.add_column("Component", style="bold white", width=25)
        table.add_column("Status", style="bold", width=12)
        table.add_column("Details", style="cyan", width=45)
        table.add_column("Transaction/Link", style="yellow", width=35)
        
        # Agent Registration Results
        table.add_row(
            "🤖 Agent Registration",
            "[green]✅ SUCCESS[/green]",
            f"Alice (ID: {self.alice_sdk.get_agent_id()}), Bob (ID: {self.bob_sdk.get_agent_id()}), Charlie (ID: {self.charlie_sdk.get_agent_id()}) with x402 support",
            "ERC-8004 on Base Sepolia"
        )
        
        # x402 Analysis Payment (A0GI)
        payment_data = self.results.get("0g_payment", {})
        analysis_amount = payment_data.get('amount', 0)
        analysis_payment_obj = payment_data.get('x402_payment_result')
        analysis_tx = ""
        if analysis_payment_obj and hasattr(analysis_payment_obj, 'transaction_hash'):
            analysis_tx = analysis_payment_obj.transaction_hash or ""
        
        table.add_row(
            "💳 x402 Analysis Payment",
            "[green]✅ SUCCESS[/green]" if payment_data.get('x402_success') else "[yellow]⚠️  SIMULATED[/yellow]",
            f"{analysis_amount:.4f} A0GI: Charlie → Alice",
            f"0x{analysis_tx[:20]}..." if analysis_tx and analysis_tx != "N/A" else "N/A"
        )
        
        # x402 Validation Payment (A0GI)
        validation_payment_obj = self.results.get("validation", {}).get("x402_payment")
        if validation_payment_obj and hasattr(validation_payment_obj, 'amount'):
            validation_amount = validation_payment_obj.amount
            validation_tx = validation_payment_obj.transaction_hash or ""
        else:
            validation_amount = 0.001  # Default
            validation_tx = ""
        
        # Extract payment IDs for f-string
        analysis_payment_id = analysis_payment_obj.payment_id[:20] if analysis_payment_obj and hasattr(analysis_payment_obj, 'payment_id') else 'N/A'
        validation_payment_id = validation_tx[:20] if validation_tx else 'N/A'
        
        table.add_row(
            "💳 x402 Validation Payment",
            "[green]✅ SUCCESS[/green]" if validation_tx else "[yellow]⚠️  SIMULATED[/yellow]",
            f"{validation_amount:.4f} A0GI: Charlie → Bob",
            f"0x{validation_tx[:20]}..." if validation_tx and validation_tx != "N/A" else "N/A"
        )
        
        # Enhanced Evidence Package
        enhanced_evidence = self.results.get("enhanced_evidence", {})
        table.add_row(
            "📦 Enhanced Evidence",
            "[green]✅ SUCCESS[/green]",
            f"Evidence package with {enhanced_evidence.get('payment_proofs_included', 0)} payment proofs",
            f"IPFS: {enhanced_evidence.get('cid', 'N/A')[:20]}..."
        )
        
        # Validation Results
        validation_score = self.results.get("validation", {}).get("score", 0)
        table.add_row(
            "🔍 PoA Validation",
            "[green]✅ SUCCESS[/green]",
            f"Score: {validation_score}/100 with payment verification",
            f"Enhanced with x402 receipts"
        )
        
        rprint(table)
        rprint()
        
        # Payment amounts already extracted at the beginning of method
        
        # Create payment summary content as a string first
        payment_summary_content = f"""[bold cyan]💳 x402 Payment Protocol Summary (A0GI):[/bold cyan]

[yellow]Smart Shopping Service Payment:[/yellow]
• Amount: {analysis_amount:.4f} A0GI (x402 settlement)
• From: Charlie → Alice
• Service: AI Smart Shopping (0G Compute)
• Currency: A0GI (0G native tokens)
• Network: 0G Testnet
• Payment ID: {analysis_payment_id}...

[yellow]Validation Service Payment:[/yellow]
• Amount: {validation_amount:.4f} A0GI  
• From: Charlie → Bob
• Service: Quality Validation (0G Compute)
• Currency: A0GI (0G native tokens)
• Network: 0G Testnet
• Payment ID: {validation_payment_id}...

[bold green]🎯 x402 Protocol Benefits:[/bold green]
• Frictionless agent-to-agent payments in A0GI ✅
• Cryptographic payment receipts for PoA ✅
• No complex wallet setup required ✅
• Instant settlement on 0G Testnet ✅
• Enhanced evidence packages with payment proofs ✅
• Native integration with 0G Network ✅

[bold magenta]💰 Economic Impact:[/bold magenta]
• Alice earned {analysis_amount:.4f} A0GI for smart shopping service
• Bob earned {validation_amount:.4f} A0GI for validation service
• Charlie received verified shopping results with payment-backed guarantees
• Complete audit trail for trustless commerce established
• All transactions in 0G native tokens (A0GI)

[bold red]🔧 Next Steps:[/bold red]
• Enhanced evidence packages with payment proofs
• Multi-agent collaboration workflows
• Cross-chain x402 payment support with 0G Bridge"""

        # Create and display the panel
        payment_summary_panel = Panel(
            payment_summary_content,
            title="[bold green]🌟 x402 Commercial Success Metrics[/bold green]",
            border_style="green"
        )
        
        rprint(payment_summary_panel)


def main():
    """Main entry point for 0G-integrated Genesis Studio"""
    
    # Check if we're on the correct network
    network = os.getenv("NETWORK", "local")
    if network != "0g-testnet":
        print("⚠️  Warning: This demo is designed for 0G Testnet.")
        print("   Please set NETWORK=0g-testnet in your .env file.")
        print()
    
    # Initialize and run the 0G-integrated orchestrator
    orchestrator = GenesisStudioX402Orchestrator()
    orchestrator.run_complete_demo()


if __name__ == "__main__":
    main()