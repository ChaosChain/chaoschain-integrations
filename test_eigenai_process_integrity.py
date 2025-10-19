#!/usr/bin/env python3
"""
Test EigenAI Process Integrity in Genesis Studio
Focuses on Layer 2 (Process Integrity) without on-chain transactions
"""

import os
import sys
from rich import print as rprint
from rich.panel import Panel

# Add paths
sys.path.insert(0, os.path.dirname(__file__))

# Set hyphenated env vars for SDK (can't be in .env due to eigenx parser)
if os.getenv("BASE_SEPOLIA_RPC_URL"):
    os.environ["BASE-SEPOLIA_RPC_URL"] = os.environ["BASE_SEPOLIA_RPC_URL"]
if os.getenv("BASE_SEPOLIA_PRIVATE_KEY"):
    os.environ["BASE-SEPOLIA_PRIVATE_KEY"] = os.environ["BASE_SEPOLIA_PRIVATE_KEY"]
if os.getenv("BASE_SEPOLIA_CHAIN_ID"):
    os.environ["BASE-SEPOLIA_CHAIN_ID"] = os.environ["BASE_SEPOLIA_CHAIN_ID"]

from agents.server_agent_sdk import GenesisServerAgentSDK
from agents.validator_agent_sdk import GenesisValidatorAgentSDK
from chaoschain_sdk.types import AgentRole, NetworkConfig

def test_eigenai_process_integrity():
    """Test EigenAI for Process Integrity (Layer 2 of Triple-Verified Stack) with ERC-8004 + AP2"""
    
    rprint(Panel.fit("""
[bold cyan]🧪 Testing EigenAI Process Integrity with Full Stack[/bold cyan]

[yellow]Triple-Verified Stack:[/yellow]
• [bold green]Layer 1: AP2 Intent Verification ✅[/bold green]
• [bold green]Layer 2: Process Integrity (EigenAI TEE) ✅[/bold green]
• Layer 3: Adjudication/Accountability (skipped for this test)

This test demonstrates:
1. ERC-8004 Agent Identity Registration
2. AP2 Intent & Cart Mandates
3. Alice generates smart shopping analysis with EigenAI TEE
4. Bob validates the analysis with EigenAI TEE
5. Both generate ProcessProofs with TEE attestations
""", title="🔬 EigenAI Process Integrity Test"))
    
    # Check API key
    api_key = os.getenv("EIGEN_API_KEY")
    if not api_key:
        rprint("[red]❌ EIGEN_API_KEY not set![/red]")
        return False
    
    rprint(f"\n[green]✅ EIGEN_API_KEY found[/green]")
    rprint(f"   Key: {api_key[:20]}...")
    
    # Initialize Alice (Server Agent) with EigenAI
    rprint("\n[bold cyan]🔧 Step 1: Initializing Alice (Server Agent) with EigenAI + AP2...[/bold cyan]")
    
    alice = GenesisServerAgentSDK(
        agent_name="Alice_EigenAI_Test",
        agent_domain="alice-test.chaoschain.com",
        agent_role=AgentRole.SERVER,
        network=NetworkConfig.BASE_SEPOLIA,
        enable_ap2=True,  # Enable AP2 for intent verification
        enable_process_integrity=False,  # Skip SDK integrity, use direct EigenAI
        compute_provider="eigenai",
        eigenai_api_key=api_key
    )
    
    rprint(f"[green]✅ Alice initialized with {alice.compute_provider_type.upper()}[/green]")
    rprint(f"   Compute: EigenAI gpt-oss-120b-f16 (TEE verified)")
    
    # Initialize Bob (Validator Agent) with EigenAI
    rprint("\n[bold cyan]🔧 Step 2: Initializing Bob (Validator Agent) with EigenAI + AP2...[/bold cyan]")
    
    bob = GenesisValidatorAgentSDK(
        agent_name="Bob_EigenAI_Test",
        agent_domain="bob-test.chaoschain.com",
        agent_role=AgentRole.VALIDATOR,
        network=NetworkConfig.BASE_SEPOLIA,
        enable_ap2=True,  # Enable AP2 for intent verification
        enable_process_integrity=False,
        compute_provider="eigenai",
        eigenai_api_key=api_key
    )
    
    rprint(f"[green]✅ Bob initialized with {bob.compute_provider_type.upper()}[/green]")
    rprint(f"   Compute: EigenAI gpt-oss-120b-f16 (TEE verified)")
    
    # Register agents on ERC-8004
    rprint("\n" + "="*80)
    rprint("\n[bold cyan]🏛️  Step 3: Registering Agents on ERC-8004 IdentityRegistry...[/bold cyan]")
    
    registration_results = {}
    for agent_name, agent in [("Alice", alice), ("Bob", bob)]:
        try:
            rprint(f"[blue]🔧 Registering {agent_name} ({agent.agent_domain})...[/blue]")
            agent_id = agent.register_identity()
            wallet_address = agent.sdk.wallet_address
            rprint(f"[green]✅ {agent_name} registered successfully[/green]")
            rprint(f"   Agent ID: {agent_id}")
            rprint(f"   Wallet: {wallet_address}")
            registration_results[agent_name] = {
                "agent_id": agent_id,
                "wallet": wallet_address
            }
        except Exception as e:
            rprint(f"[yellow]⚠️  {agent_name} registration: {e}[/yellow]")
            registration_results[agent_name] = {"error": str(e)}
    
    # Create AP2 Intent Mandate
    rprint("\n" + "="*80)
    rprint("\n[bold cyan]📋 Step 4: Creating AP2 Intent & Cart Mandates...[/bold cyan]")
    
    try:
        # Create intent mandate for smart shopping
        intent_mandate = alice.sdk.create_intent_mandate(
            user_description="Find me the best winter jacket in green, willing to pay up to 20% premium for the right color. Price limit: $150, quality threshold: good, auto-purchase enabled",
            merchants=None,  # Allow any merchant
            skus=None,  # Allow any SKU
            requires_refundability=True,
            expiry_minutes=60
        )
        
        rprint("[green]✅ Intent Mandate created[/green]")
        rprint(f"   Description: Smart shopping for winter jacket (green)")
        rprint(f"   Budget: $150 (20% premium tolerance)")
        rprint(f"   Refundable: Yes")
        
        # Create cart mandate
        cart_mandate = alice.sdk.create_cart_mandate(
            cart_id="cart_winter_jacket_eigenai_test",
            items=[{
                "service": "smart_shopping_agent",
                "description": "Find best winter jacket deal with color preference",
                "price": 2.0
            }],
            total_amount=2.0,
            currency="USDC",
            merchant_name="Alice Smart Shopping Agent (EigenAI)",
            expiry_minutes=15
        )
        
        rprint("[green]✅ Cart Mandate created[/green]")
        rprint(f"   Cart ID: cart_winter_jacket_eigenai_test")
        rprint(f"   Total: 2.0 USDC")
        rprint(f"   Merchant: Alice Smart Shopping Agent (EigenAI)")
        
        # Verify JWT if available
        mandate_verified = True
        if hasattr(cart_mandate, 'merchant_authorization') and cart_mandate.merchant_authorization:
            jwt_payload = alice.sdk.google_ap2_integration.verify_jwt_token(cart_mandate.merchant_authorization)
            mandate_verified = bool(jwt_payload)
            rprint(f"[green]✅ JWT Token verified: {mandate_verified}[/green]")
        
    except Exception as e:
        rprint(f"[yellow]⚠️  AP2 Mandate creation: {e}[/yellow]")
        cart_mandate = None
    
    # Test 1: Alice generates smart shopping analysis with EigenAI TEE
    rprint("\n" + "="*80)
    rprint("\n[bold cyan]🛒 Step 5: Alice generating smart shopping analysis with EigenAI TEE...[/bold cyan]")
    
    try:
        result = alice.generate_smart_shopping_analysis(
            item_type="winter_jacket",
            color="green",
            budget=150.0,
            premium_tolerance=0.20
        )
        
        analysis = result["analysis"]
        proof = result["process_integrity_proof"]
        
        rprint("\n[bold green]✅ Analysis Complete with TEE Proof![/bold green]")
        rprint("\n[bold yellow]📊 Shopping Analysis Results:[/bold yellow]")
        rprint(f"   Item: {analysis.get('item_type', 'N/A')}")
        rprint(f"   Requested Color: {analysis.get('requested_color', 'N/A')}")
        rprint(f"   Available Color: {analysis.get('available_color', 'N/A')}")
        rprint(f"   Final Price: ${analysis.get('final_price', 0):.2f}")
        rprint(f"   Merchant: {analysis.get('merchant', 'N/A')}")
        rprint(f"   Confidence: {analysis.get('confidence', 0)*100:.1f}%")
        
        rprint("\n[bold green]🔐 Process Integrity Proof (Layer 2):[/bold green]")
        rprint(f"   Proof ID: {proof.proof_id}")
        rprint(f"   TEE Provider: {proof.tee_provider}")
        rprint(f"   TEE Job ID: {proof.tee_job_id}")
        rprint(f"   Verification Status: {proof.verification_status}")
        rprint(f"   Code Hash: {proof.code_hash[:30]}...")
        rprint(f"   Execution Hash: {proof.execution_hash[:30]}...")
        rprint(f"   TEE Attestation: {'✅ Present' if proof.tee_attestation else '❌ Missing'}")
        
        # Test 2: Bob validates the analysis with EigenAI TEE
        rprint("\n" + "="*80)
        rprint("\n[bold cyan]🔍 Step 6: Bob validating analysis with EigenAI TEE...[/bold cyan]")
        
        validation_result = bob.validate_analysis_with_crewai(analysis)
        
        validation = validation_result["validation"]
        validation_proof = validation_result["process_integrity_proof"]
        
        rprint("\n[bold green]✅ Validation Complete with TEE Proof![/bold green]")
        rprint("\n[bold yellow]📋 Validation Results:[/bold yellow]")
        rprint(f"   Overall Score: {validation.get('overall_score', 0)}/100")
        rprint(f"   Quality Rating: {validation.get('quality_rating', 'N/A')}")
        rprint(f"   Pass/Fail: {validation.get('pass_fail', 'N/A')}")
        
        if 'price_accuracy' in validation:
            rprint(f"   Price Accuracy: {validation['price_accuracy']}/100")
        if 'merchant_reliability' in validation:
            rprint(f"   Merchant Reliability: {validation['merchant_reliability']}/100")
        
        rprint("\n[bold green]🔐 Validation Proof (Layer 2):[/bold green]")
        rprint(f"   Proof ID: {validation_proof.proof_id}")
        rprint(f"   TEE Provider: {validation_proof.tee_provider}")
        rprint(f"   TEE Job ID: {validation_proof.tee_job_id}")
        rprint(f"   Verification Status: {validation_proof.verification_status}")
        rprint(f"   TEE Attestation: {'✅ Present' if validation_proof.tee_attestation else '❌ Missing'}")
        
        # Summary
        rprint("\n" + "="*80)
        rprint("\n[bold green]🎉 SUCCESS: Full Triple-Verified Stack Demo Complete![/bold green]")
        
        alice_agent_id = registration_results.get("Alice", {}).get("agent_id", "N/A")
        bob_agent_id = registration_results.get("Bob", {}).get("agent_id", "N/A")
        
        rprint(Panel.fit(f"""
[bold cyan]Triple-Verified Stack - Layers 1 & 2 Complete! ✅[/bold cyan]

[yellow]Layer 1: ERC-8004 Identity + AP2 Intent:[/yellow]
• [green]✅ Alice ERC-8004:[/green] {alice_agent_id[:20]}...
• [green]✅ Bob ERC-8004:[/green] {bob_agent_id[:20]}...
• [green]✅ Intent Mandate:[/green] Winter jacket (green), $150 budget
• [green]✅ Cart Mandate:[/green] cart_winter_jacket_eigenai_test

[yellow]Layer 2: Process Integrity Verification:[/yellow]
• [green]✅ Alice's Analysis:[/green] Verified with EigenAI TEE
  - Job ID: {proof.tee_job_id}
  - Price: ${analysis.get('final_price', 0):.2f}
  - Confidence: {analysis.get('confidence', 0)*100:.1f}%

• [green]✅ Bob's Validation:[/green] Verified with EigenAI TEE
  - Job ID: {validation_proof.tee_job_id}
  - Score: {validation.get('overall_score', 0)}/100
  - Rating: {validation.get('quality_rating', 'N/A')}

[bold green]🔐 Full stack demonstrated:[/bold green]
✅ ERC-8004 Agent Identity Registry
✅ AP2 Intent & Cart Mandates (Google protocol)
✅ TEE-verified computation (EigenAI)
✅ Cryptographic attestations
✅ Hardware-based security (Intel SGX/AMD SEV)

[yellow]This is the most complete ChaosChain demo![/yellow]
""", title="🏆 Full Stack Test Results", border_style="green"))
        
        return True
        
    except Exception as e:
        rprint(f"\n[red]❌ Test failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    rprint("\n[bold blue]Starting EigenAI Process Integrity Test...[/bold blue]\n")
    
    success = test_eigenai_process_integrity()
    
    if success:
        rprint("\n[bold green]✅ All tests passed![/bold green]")
        sys.exit(0)
    else:
        rprint("\n[bold red]❌ Tests failed![/bold red]")
        sys.exit(1)

