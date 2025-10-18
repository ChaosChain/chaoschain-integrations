#!/usr/bin/env python3
"""
Live test of EigenCompute integration
Tests the complete flow: submit job -> poll status -> get result with TEE proof
"""

import os
import sys
import time
from rich import print as rprint
from rich.panel import Panel
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Add integrations to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "chaoschain-integrations"))

from chaoschain_integrations.compute.eigen import EigenComputeAdapter

def main():
    """Test EigenCompute integration with real API"""
    
    rprint(Panel.fit(
        "[bold cyan]EigenCompute Live Integration Test[/bold cyan]\n"
        "Testing TEE-verified compute with real EigenCloud API",
        border_style="cyan"
    ))
    
    # Check environment
    api_url = os.getenv("EIGEN_API_URL", "https://api.eigencloud.xyz")
    api_key = os.getenv("EIGEN_API_KEY")
    
    if not api_key:
        rprint("[red]❌ ERROR: EIGEN_API_KEY not set![/red]")
        rprint("\n[yellow]Please set your EigenCloud API key:[/yellow]")
        rprint("   export EIGEN_API_KEY=your_key_here")
        rprint("\n[yellow]Get your key at: https://docs.eigencloud.xyz/products/eigencompute/quickstart[/yellow]")
        return 1
    
    rprint(f"\n[green]✅ API URL: {api_url}[/green]")
    rprint(f"[green]✅ API Key: {api_key[:8]}...{api_key[-4:]}[/green]")
    
    # Initialize adapter
    rprint("\n[yellow]🔧 Initializing EigenCompute adapter...[/yellow]")
    try:
        adapter = EigenComputeAdapter(
            api_url=api_url,
            api_key=api_key,
        )
        rprint("[green]✅ EigenAI adapter initialized[/green]")
        rprint(f"   Client API URL: {adapter.client.api_url}")
        rprint(f"   Default timeout: {adapter.default_timeout}s")
    except Exception as e:
        rprint(f"[red]❌ Failed to initialize adapter: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 1
    
    # Test 1: Submit a simple inference task
    rprint("\n[bold]📝 Test 1: Submit TEE-verified inference task[/bold]")
    
    task = {
        "model": "gpt-oss-120b-f16",  # Correct EigenAI model
        "prompt": "What is the capital of France? Answer in one word.",
        "max_tokens": 50,
        "seed": 42,  # For deterministic results
    }
    
    rprint(f"   Model: {task['model']}")
    rprint(f"   Prompt: {task['prompt']}")
    rprint(f"   Seed: {task.get('seed', 'None')} (for deterministic results)")
    
    try:
        rprint("\n[cyan]📤 Submitting job to EigenCloud...[/cyan]")
        job_id = adapter.submit(task)
        rprint(f"[green]✅ Job submitted successfully![/green]")
        rprint(f"   Job ID: {job_id}")
    except Exception as e:
        rprint(f"[red]❌ Failed to submit job: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 1
    
    # Test 2: Poll for job status
    rprint("\n[bold]📊 Test 2: Monitor job status[/bold]")
    
    max_polls = 40
    poll_interval = 3
    
    for i in range(max_polls):
        try:
            status = adapter.status(job_id)
            state = status.get("status", "unknown")
            
            rprint(f"   [{i+1}/{max_polls}] Status: [cyan]{state}[/cyan]", end="")
            
            if state == "completed":
                rprint(" [green]✅[/green]")
                break
            elif state == "failed":
                rprint(" [red]❌[/red]")
                rprint(f"[red]Job failed: {status}[/red]")
                return 1
            else:
                rprint(f" (waiting {poll_interval}s...)")
                time.sleep(poll_interval)
        except Exception as e:
            rprint(f"\n[yellow]⚠️  Status check error: {e}[/yellow]")
            time.sleep(poll_interval)
    else:
        rprint(f"\n[yellow]⚠️  Job did not complete within {max_polls * poll_interval}s[/yellow]")
        return 1
    
    # Test 3: Retrieve result with TEE proof
    rprint("\n[bold]🎯 Test 3: Retrieve result with TEE attestation[/bold]")
    
    try:
        rprint("[cyan]📥 Fetching result...[/cyan]")
        result = adapter.result(job_id, wait=False)
        
        rprint("[green]✅ Result retrieved successfully![/green]\n")
        
        # Display output
        rprint(Panel(
            f"[bold]Model Output:[/bold]\n{result.output}",
            title="💬 Inference Result",
            border_style="green"
        ))
        
        # Display TEE proof
        rprint("\n[bold cyan]🔐 TEE Attestation Proof:[/bold cyan]")
        proof = result.proof
        
        rprint(f"   Verification Method: [yellow]{proof.method}[/yellow]")
        if proof.docker_digest:
            rprint(f"   Docker Image: [yellow]{proof.docker_digest}[/yellow]")
        if proof.enclave_pubkey:
            rprint(f"   Enclave Public Key: [yellow]{proof.enclave_pubkey}[/yellow]")
        if proof.execution_hash:
            rprint(f"   Execution Hash: [yellow]{proof.execution_hash}[/yellow]")
        if proof.signature:
            rprint(f"   Result Signature: [yellow]{proof.signature[:32]}...[/yellow]")
        
        if proof.attestation:
            rprint(f"\n   [dim]Full Attestation Data:[/dim]")
            import json
            attestation_str = json.dumps(proof.attestation, indent=2)[:500]
            rprint(f"   [dim]{attestation_str}...[/dim]")
        
        # Success summary
        rprint("\n" + "="*70)
        rprint(Panel.fit(
            "[bold green]✅ All Tests Passed![/bold green]\n\n"
            f"✓ Job submitted: {job_id}\n"
            f"✓ Job completed with status: completed\n"
            f"✓ Result retrieved with TEE proof\n"
            f"✓ Verification method: {proof.method}\n"
            f"✓ Execution hash: {proof.execution_hash or 'N/A'}",
            title="🎉 Integration Test Success",
            border_style="green"
        ))
        
        return 0
        
    except Exception as e:
        rprint(f"[red]❌ Failed to retrieve result: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)

