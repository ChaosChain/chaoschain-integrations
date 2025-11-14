#!/usr/bin/env python3
"""
Test Genesis Studio with x402 Facilitator Integration

This script tests the complete loan approval workflow with:
- Base Sepolia network (x402 supported)
- Local facilitator (http://localhost:8402)
- Real x402 payment flow with BFT consensus

Prerequisites:
1. Facilitator running: cd chaoschain-x402/http-bridge && npm run dev
2. Environment configured for Base Sepolia
"""

import os
import sys
from rich import print as rprint
from rich.console import Console
from rich.panel import Panel
from dotenv import load_dotenv

console = Console()

# Load .env file first (if it exists)
env_file = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_file):
    load_dotenv(env_file)
    rprint(f"[green]✅ Loaded configuration from .env file[/green]")
else:
    rprint(f"[yellow]⚠️  No .env file found, using environment variables[/yellow]")

# Override with Base Sepolia + Facilitator settings (only if not already set)
if not os.getenv("NETWORK"):
    os.environ["NETWORK"] = "base-sepolia"
if not os.getenv("X402_USE_FACILITATOR"):
    os.environ["X402_USE_FACILITATOR"] = "true"
if not os.getenv("X402_FACILITATOR_URL"):
    os.environ["X402_FACILITATOR_URL"] = "http://localhost:8402"
if not os.getenv("COMPUTE_PROVIDER"):
    os.environ["COMPUTE_PROVIDER"] = "eigencompute"  # Keep EigenCompute for TEE
if not os.getenv("STORAGE_PROVIDER"):
    os.environ["STORAGE_PROVIDER"] = "local"  # Use local storage for testing

# Ensure Base Sepolia RPC is set
if not os.getenv("BASE_SEPOLIA_RPC_URL"):
    os.environ["BASE_SEPOLIA_RPC_URL"] = "https://sepolia.base.org"

# Display current configuration
rprint(f"\n[cyan]Current Configuration:[/cyan]")
rprint(f"   NETWORK: {os.getenv('NETWORK')}")
rprint(f"   X402_USE_FACILITATOR: {os.getenv('X402_USE_FACILITATOR')}")
rprint(f"   X402_FACILITATOR_URL: {os.getenv('X402_FACILITATOR_URL')}")
rprint(f"   BASE_SEPOLIA_RPC_URL: {os.getenv('BASE_SEPOLIA_RPC_URL', 'not set')[:50]}...")
rprint(f"   COMPUTE_PROVIDER: {os.getenv('COMPUTE_PROVIDER')}")
rprint(f"   STORAGE_PROVIDER: {os.getenv('STORAGE_PROVIDER')}")

console.print(Panel.fit(
    "[bold cyan]Testing Genesis Studio with x402 Facilitator[/bold cyan]\n"
    "[dim]Network: Base Sepolia | Facilitator: http://localhost:8402[/dim]",
    border_style="cyan"
))

# Check facilitator health
rprint("\n[blue]🔍 Checking facilitator health...[/blue]")
import requests
try:
    response = requests.get("http://localhost:8402/health", timeout=5)
    if response.status_code == 200:
        health = response.json()
        rprint(f"[green]✅ Facilitator is running[/green]")
        rprint(f"   Healthy: {health.get('healthy')}")
        rprint(f"   RPC Base Sepolia: {health.get('checks', {}).get('rpcBaseSepolia')}")
        rprint(f"   RPC Latency: {health.get('checks', {}).get('rpcLatencyMs')}ms")
    else:
        rprint(f"[red]❌ Facilitator returned status {response.status_code}[/red]")
        sys.exit(1)
except Exception as e:
    rprint(f"[red]❌ Cannot connect to facilitator: {e}[/red]")
    rprint(f"[yellow]💡 Start facilitator:[/yellow]")
    rprint(f"[yellow]   cd /Users/sumeet/Desktop/ChaosChain_labs/chaoschain-x402/http-bridge[/yellow]")
    rprint(f"[yellow]   npm run dev[/yellow]")
    sys.exit(1)

# Check supported networks
rprint("\n[blue]📋 Checking supported networks...[/blue]")
try:
    response = requests.get("http://localhost:8402/supported", timeout=5)
    if response.status_code == 200:
        data = response.json()
        kinds = data.get("kinds", [])
        
        base_sepolia_supported = any(
            k.get("network") == "base-sepolia" for k in kinds
        )
        
        if base_sepolia_supported:
            rprint(f"[green]✅ Base Sepolia is supported[/green]")
        else:
            rprint(f"[yellow]⚠️  Base Sepolia not in supported list[/yellow]")
            rprint(f"   Supported: {[k.get('network') for k in kinds]}")
    else:
        rprint(f"[yellow]⚠️  Could not check supported networks[/yellow]")
except Exception as e:
    rprint(f"[yellow]⚠️  Error checking networks: {e}[/yellow]")

# Now run the actual genesis studio workflow
rprint("\n[bold green]🚀 Starting Genesis Studio with Facilitator Integration[/bold green]\n")

# Import and run genesis studio
sys.path.insert(0, os.path.dirname(__file__))

try:
    # Import the GenesisStudioX402Orchestrator class
    from genesis_studio import GenesisStudioX402Orchestrator
    
    # Create instance
    studio = GenesisStudioX402Orchestrator()
    
    # Run the workflow
    rprint("[cyan]═══════════════════════════════════════════════════════[/cyan]")
    rprint("[bold cyan]         GENESIS STUDIO - FACILITATOR TEST             [/bold cyan]")
    rprint("[cyan]═══════════════════════════════════════════════════════[/cyan]\n")
    
    studio.run_complete_demo()
    
    rprint("\n[green]✅ Genesis Studio completed successfully![/green]")
    
    # Check if payments used facilitator
    if hasattr(studio, 'alice_agent') and hasattr(studio.alice_agent, 'x402_payment_manager'):
        pm = studio.alice_agent.x402_payment_manager
        if pm and pm.use_facilitator:
            rprint(f"\n[bold green]🎉 Facilitator Integration Confirmed![/bold green]")
            rprint(f"   Facilitator URL: {pm.facilitator_url}")
            rprint(f"   Payment History: {len(pm.payment_history)} payments")
            
            # Show payment details
            for payment in pm.payment_history:
                rprint(f"\n[blue]Payment:[/blue]")
                rprint(f"   From: {payment.get('from_agent')}")
                rprint(f"   To: {payment.get('to_agent')}")
                rprint(f"   Amount: {payment.get('amount_usdc')} USDC")
                rprint(f"   TX: {payment.get('main_transaction_hash')}")
                if payment.get('facilitator_report'):
                    rprint(f"   [green]✅ Facilitator Verified[/green]")
                    rprint(f"   Consensus Proof: {payment['facilitator_report'].get('consensusProof', '')[:50]}...")
        else:
            rprint(f"\n[yellow]⚠️  Facilitator not used (direct mode)[/yellow]")
    else:
        rprint(f"\n[dim]ℹ️  Payment manager not accessible for verification[/dim]")
    
except KeyboardInterrupt:
    rprint("\n[yellow]⚠️  Interrupted by user[/yellow]")
    sys.exit(0)
except Exception as e:
    rprint(f"\n[red]❌ Error running Genesis Studio: {e}[/red]")
    import traceback
    traceback.print_exc()
    sys.exit(1)

console.print(Panel.fit(
    "[bold green]✅ Test Complete![/bold green]\n"
    "[dim]Check the logs above for facilitator integration details[/dim]",
    border_style="green"
))

