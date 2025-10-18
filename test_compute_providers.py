#!/usr/bin/env python3
"""
Test script to demonstrate flexible compute provider support in ChaosChain agents
"""

import os
import sys
from rich import print as rprint
from rich.panel import Panel
from rich.table import Table

# Add chaoschain-integrations to path
sys.path.insert(0, os.path.dirname(__file__))

def test_eigenai():
    """Test EigenAI integration"""
    rprint(Panel.fit("[bold cyan]Testing EigenAI Provider[/bold cyan]"))
    
    try:
        from agents.server_agent_sdk import GenesisServerAgentSDK
        from chaoschain_sdk.types import AgentRole, NetworkConfig
        
        # Initialize agent with EigenAI
        alice = GenesisServerAgentSDK(
            agent_name="Alice_Test",
            agent_domain="alice-test.chaoschain.com",
            agent_role=AgentRole.SERVER,
            network=NetworkConfig.BASE_SEPOLIA,
            enable_ap2=False,  # Disable for simple test
            enable_process_integrity=False,  # Disable for simple test
            compute_provider="eigenai",
            eigenai_api_key=os.getenv("EIGEN_API_KEY")
        )
        
        rprint("[green]✅ EigenAI agent initialized successfully![/green]")
        rprint(f"   Provider: {alice.compute_provider_type}")
        rprint(f"   EigenAI client available: {alice.eigenai is not None}")
        
        if alice.eigenai:
            # Test simple analysis
            rprint("\n[yellow]🔍 Testing shopping analysis with EigenAI...[/yellow]")
            result = alice.generate_smart_shopping_analysis(
                item_type="winter_jacket",
                color="red",
                budget=150.0,
                premium_tolerance=0.20
            )
            
            rprint("[green]✅ Analysis completed![/green]")
            rprint(f"   Item: {result['analysis'].get('item_type')}")
            rprint(f"   Price: ${result['analysis'].get('final_price', 0):.2f}")
            rprint(f"   TEE Provider: {result['process_integrity_proof'].tee_provider}")
            rprint(f"   Job ID: {result['process_integrity_proof'].tee_job_id}")
            
            return True
        else:
            rprint("[red]❌ EigenAI client not initialized[/red]")
            return False
            
    except Exception as e:
        rprint(f"[red]❌ EigenAI test failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False


def test_crewai():
    """Test CrewAI fallback"""
    rprint(Panel.fit("[bold cyan]Testing CrewAI Provider[/bold cyan]"))
    
    try:
        from agents.server_agent_sdk import GenesisServerAgentSDK
        from chaoschain_sdk.types import AgentRole, NetworkConfig
        
        # Initialize agent with CrewAI
        alice = GenesisServerAgentSDK(
            agent_name="Alice_Test",
            agent_domain="alice-test.chaoschain.com",
            agent_role=AgentRole.SERVER,
            network=NetworkConfig.BASE_SEPOLIA,
            enable_ap2=False,
            enable_process_integrity=True,  # Enable to test integrity
            compute_provider="crewai"
        )
        
        rprint("[green]✅ CrewAI agent initialized successfully![/green]")
        rprint(f"   Provider: {alice.compute_provider_type}")
        
        return True
            
    except Exception as e:
        rprint(f"[red]❌ CrewAI test failed: {e}[/red]")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    rprint(Panel.fit("""
[bold cyan]ChaosChain Compute Provider Tests[/bold cyan]

Testing flexible compute provider support:
• EigenAI (TEE-verified LLM)
• CrewAI (local fallback)
""", title="🧪 Test Suite"))
    
    # Check environment
    if not os.getenv("EIGEN_API_KEY"):
        rprint("[yellow]⚠️  EIGEN_API_KEY not set - EigenAI test will be skipped[/yellow]")
    
    results = {}
    
    # Test EigenAI if API key available
    if os.getenv("EIGEN_API_KEY"):
        rprint("\n" + "="*80 + "\n")
        results["eigenai"] = test_eigenai()
    else:
        results["eigenai"] = None
    
    # Test CrewAI
    rprint("\n" + "="*80 + "\n")
    results["crewai"] = test_crewai()
    
    # Summary
    rprint("\n" + "="*80 + "\n")
    table = Table(title="Test Results")
    table.add_column("Provider", style="cyan")
    table.add_column("Status", style="bold")
    
    for provider, success in results.items():
        if success is None:
            table.add_row(provider.upper(), "[yellow]SKIPPED[/yellow]")
        elif success:
            table.add_row(provider.upper(), "[green]✅ PASSED[/green]")
        else:
            table.add_row(provider.upper(), "[red]❌ FAILED[/red]")
    
    rprint(table)
    
    # Exit code
    passed = sum(1 for v in results.values() if v is True)
    total = sum(1 for v in results.values() if v is not None)
    
    if passed == total:
        rprint("\n[bold green]🎉 All tests passed![/bold green]")
        return 0
    else:
        rprint(f"\n[bold yellow]⚠️  {passed}/{total} tests passed[/bold yellow]")
        return 1


if __name__ == "__main__":
    sys.exit(main())

