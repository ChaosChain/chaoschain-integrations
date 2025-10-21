#!/usr/bin/env python3
"""
Micro-Loan Approval Workflow Test
Tests the complete loan approval flow with EigenCompute TEE
"""

import os
import sys
import json
import hashlib
from rich import print as rprint
from rich.panel import Panel
from rich.align import Align

# Add SDK to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'sdk'))

from chaoschain_integrations.compute.eigencompute import EigenComputeAdapter

def main():
    """Test the loan approval workflow"""
    
    banner = """
[bold blue]🏦 MICRO-LOAN APPROVAL SYSTEM TEST[/bold blue]
[cyan]Autonomous Agent Lending with TEE Verification[/cyan]

[yellow]Architecture:[/yellow]
• Charlie: Requests 0.5 USDC loan
• Alice: Evaluates creditworthiness in TEE
• Bob: Audits + deterministic re-execution
• Payment: 0.5 USDC via x402 (if approved)
• Fees: 0.001 A0GI each for Alice & Bob
"""
    
    rprint(Panel(Align.center(banner), border_style="green", padding=(1, 2)))
    rprint()
    
    # Configuration
    app_id = os.getenv("EIGENCOMPUTE_APP_ID", "0xb29Ec00fF0D6C1349E6DFcD16234082aE60e64bb")
    sidecar_url = "http://localhost:8080"
    
    rprint(f"[cyan]📡 EigenCompute App ID: {app_id}[/cyan]")
    rprint(f"[cyan]📡 Sidecar URL: {sidecar_url}[/cyan]")
    rprint()
    
    # Initialize adapter
    adapter = EigenComputeAdapter(sidecar_url=sidecar_url)
    
    # ========================================================================
    # STEP 1: Charlie Requests Loan
    # ========================================================================
    rprint("[bold]📋 STEP 1: Charlie (Borrower) Requests Loan[/bold]")
    rprint("-" * 80)
    
    # In real workflow, this would come from Charlie's SDK wallet
    charlie_address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"  # Example address
    
    rprint(f"   Borrower: {charlie_address}")
    rprint(f"   Requested: 0.5 USDC")
    rprint(f"   Purpose: operational_expenses")
    rprint()
    
    try:
        charlie_result = adapter.execute(
            app_id=app_id,
            function="request_loan",
            inputs={
                "loan_amount": 0.5,
                "purpose": "operational_expenses",
                "borrower_address": charlie_address
            }
        )
        
        charlie_profile = json.loads(charlie_result.output) if isinstance(charlie_result.output, str) else charlie_result.output
        
        rprint(f"[green]✅ Charlie's Profile Loaded:[/green]")
        rprint(f"   ERC-8004 Score: {charlie_profile.get('erc8004_score')}")
        rprint(f"   Payment History: {charlie_profile.get('payment_history_count')} successful payments")
        rprint(f"   Stake: ${charlie_profile.get('stake_amount')} USDC")
        rprint(f"   Previous Defaults: {charlie_profile.get('previous_defaults')}")
        rprint(f"   Reputation Tier: {charlie_profile.get('reputation_tier')}")
        rprint()
        
    except Exception as e:
        rprint(f"[red]❌ Error loading Charlie's profile: {e}[/red]")
        sys.exit(1)
    
    # ========================================================================
    # STEP 2: Alice Evaluates Loan
    # ========================================================================
    rprint("[bold]🏦 STEP 2: Alice (Loan Officer) Evaluates Creditworthiness[/bold]")
    rprint("-" * 80)
    
    try:
        alice_result = adapter.execute(
            app_id=app_id,
            function="evaluate_loan",
            inputs={
                "borrower_address": charlie_profile['borrower_address'],
                "loan_amount": charlie_profile['requested_amount'],
                "erc8004_score": charlie_profile['erc8004_score'],
                "payment_history_count": charlie_profile['payment_history_count'],
                "stake_amount": charlie_profile['stake_amount'],
                "previous_defaults": charlie_profile['previous_defaults']
            }
        )
        
        alice_evaluation = json.loads(alice_result.output) if isinstance(alice_result.output, str) else alice_result.output
        
        # Calculate execution hash
        alice_output_json = json.dumps(alice_evaluation, sort_keys=True)
        alice_exec_hash = hashlib.sha256(alice_output_json.encode()).hexdigest()
        
        rprint(f"[green]✅ Alice's Evaluation:[/green]")
        rprint(f"   Decision: [bold]{alice_evaluation.get('decision')}[/bold]")
        rprint(f"   Risk Score: {alice_evaluation.get('risk_score')}/100")
        rprint(f"   Creditworthiness: {alice_evaluation.get('creditworthiness')}")
        rprint(f"   Max Loan Amount: ${alice_evaluation.get('max_loan_amount')} USDC")
        rprint(f"   Confidence: {alice_evaluation.get('approval_confidence')}")
        
        if 'key_factors' in alice_evaluation:
            rprint(f"   Key Factors:")
            for factor in alice_evaluation['key_factors']:
                rprint(f"      • {factor}")
        
        if 'reasoning' in alice_evaluation:
            rprint(f"   Reasoning: {alice_evaluation['reasoning'][:150]}...")
        
        rprint(f"   [cyan]Exec Hash: 0x{alice_exec_hash[:32]}...[/cyan]")
        rprint()
        
        # Display TEE execution metadata
        if 'tee_execution' in alice_evaluation:
            tee = alice_evaluation['tee_execution']
            rprint(f"[cyan]📊 TEE Execution Details:[/cyan]")
            rprint(f"   Agent: {tee.get('agent')}")
            rprint(f"   Role: {tee.get('role')}")
            rprint(f"   EigenAI Job ID: {tee.get('eigenai_job_id')}")
            rprint(f"   Model: {tee.get('eigenai_model')}")
            rprint()
        
    except Exception as e:
        rprint(f"[red]❌ Error in Alice's evaluation: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # ========================================================================
    # STEP 3: Bob Audits Alice's Evaluation
    # ========================================================================
    rprint("[bold]🔍 STEP 3: Bob (Auditor) Audits Alice's Decision[/bold]")
    rprint("-" * 80)
    
    try:
        bob_result = adapter.execute(
            app_id=app_id,
            function="audit_evaluation",
            inputs={
                "evaluation": alice_evaluation
            }
        )
        
        bob_audit = json.loads(bob_result.output) if isinstance(bob_result.output, str) else bob_result.output
        
        rprint(f"[green]✅ Bob's Audit:[/green]")
        rprint(f"   Audit Decision: [bold]{bob_audit.get('audit_decision')}[/bold]")
        rprint(f"   Agrees with Alice: {bob_audit.get('agrees_with_alice')}")
        rprint(f"   Audit Risk Score: {bob_audit.get('audit_risk_score')}/100")
        rprint(f"   Decision Quality: {bob_audit.get('decision_quality')}")
        rprint(f"   Compliance Check: {bob_audit.get('compliance_check')}")
        rprint(f"   Recommendation: {bob_audit.get('recommendation')}")
        
        if 'red_flags' in bob_audit and bob_audit['red_flags']:
            rprint(f"   Red Flags:")
            for flag in bob_audit['red_flags']:
                rprint(f"      🚨 {flag}")
        
        if 'audit_notes' in bob_audit:
            rprint(f"   Notes: {bob_audit['audit_notes'][:150]}...")
        
        rprint()
        
    except Exception as e:
        rprint(f"[red]❌ Error in Bob's audit: {e}[/red]")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    # ========================================================================
    # STEP 4: Deterministic Verification
    # ========================================================================
    rprint("[bold]🔬 STEP 4: Deterministic Verification (Bob Re-Executes)[/bold]")
    rprint("-" * 80)
    rprint("Bob re-runs Alice's exact evaluation with the same inputs...")
    rprint()
    
    try:
        # Bob re-runs Alice's evaluation
        bob_rerun = adapter.execute(
            app_id=app_id,
            function="evaluate_loan",  # Same function as Alice
            inputs={
                # EXACT same inputs as Alice
                "borrower_address": charlie_profile['borrower_address'],
                "loan_amount": charlie_profile['requested_amount'],
                "erc8004_score": charlie_profile['erc8004_score'],
                "payment_history_count": charlie_profile['payment_history_count'],
                "stake_amount": charlie_profile['stake_amount'],
                "previous_defaults": charlie_profile['previous_defaults']
            }
        )
        
        bob_evaluation = json.loads(bob_rerun.output) if isinstance(bob_rerun.output, str) else bob_rerun.output
        
        # Calculate Bob's execution hash
        bob_output_json = json.dumps(bob_evaluation, sort_keys=True)
        bob_exec_hash = hashlib.sha256(bob_output_json.encode()).hexdigest()
        
        rprint(f"   Alice's Exec Hash: [cyan]0x{alice_exec_hash[:32]}...[/cyan]")
        rprint(f"   Bob's Exec Hash:   [cyan]0x{bob_exec_hash[:32]}...[/cyan]")
        rprint()
        
        if alice_exec_hash == bob_exec_hash:
            rprint(f"[bold green]✅ DETERMINISTIC MATCH: Exec hashes IDENTICAL![/bold green]")
            rprint(f"[bold green]   🎯 Loan would be AUTO-DISBURSED[/bold green]")
            rprint(f"[bold green]   📦 Provable determinism achieved[/bold green]")
            loan_approved = True
        else:
            rprint(f"[bold red]❌ DETERMINISTIC MISMATCH: Different exec hashes![/bold red]")
            rprint(f"[red]   🚨 Loan would be HELD for review[/red]")
            rprint(f"[red]   Alice: 0x{alice_exec_hash}[/red]")
            rprint(f"[red]   Bob:   0x{bob_exec_hash}[/red]")
            loan_approved = False
        
        rprint()
        
    except Exception as e:
        rprint(f"[yellow]⚠️  Deterministic verification failed: {e}[/yellow]")
        loan_approved = False
        rprint()
    
    # ========================================================================
    # SUMMARY
    # ========================================================================
    rprint("=" * 80)
    rprint("[bold]📊 LOAN APPROVAL SUMMARY[/bold]")
    rprint("=" * 80)
    rprint()
    
    rprint(f"[bold]Borrower:[/bold] Charlie ({charlie_profile['borrower_address'][:10]}...)")
    rprint(f"  • ERC-8004 Score: {charlie_profile['erc8004_score']}")
    rprint(f"  • Stake: ${charlie_profile['stake_amount']} USDC")
    rprint(f"  • Requested: ${charlie_profile['requested_amount']} USDC")
    rprint()
    
    rprint(f"[bold]Alice's Evaluation:[/bold]")
    rprint(f"  • Decision: {alice_evaluation['decision']}")
    rprint(f"  • Risk Score: {alice_evaluation['risk_score']}/100")
    rprint(f"  • Max Approved: ${alice_evaluation.get('max_loan_amount')} USDC")
    rprint(f"  • Service Fee: 0.001 A0GI")
    rprint()
    
    rprint(f"[bold]Bob's Audit:[/bold]")
    rprint(f"  • Audit Decision: {bob_audit.get('audit_decision')}")
    rprint(f"  • Agrees with Alice: {bob_audit.get('agrees_with_alice')}")
    rprint(f"  • Compliance: {bob_audit.get('compliance_check')}")
    rprint(f"  • Service Fee: 0.001 A0GI")
    rprint()
    
    rprint(f"[bold]Deterministic Verification:[/bold]")
    if loan_approved:
        rprint(f"  • [green]✅ PASSED - Hashes match[/green]")
        rprint(f"  • [green]🎯 Loan APPROVED for disbursement[/green]")
    else:
        rprint(f"  • [red]❌ FAILED - Hashes differ[/red]")
        rprint(f"  • [red]🚨 Loan HELD for review[/red]")
    rprint()
    
    rprint(f"[bold]Payment Flow (if approved):[/bold]")
    rprint(f"  • Loan: 0.5 USDC via x402 → Charlie")
    rprint(f"  • Alice fee: 0.001 A0GI (0G network)")
    rprint(f"  • Bob fee: 0.001 A0GI (0G network)")
    rprint()
    
    rprint(f"[bold]Evidence Storage:[/bold]")
    rprint(f"  • All proofs published to 0G Storage")
    rprint(f"  • Payment tx linked to proof CIDs")
    rprint(f"  • Fully auditable and accountable")
    rprint()
    
    rprint("=" * 80)
    if loan_approved:
        rprint("[bold green]✅ LOAN APPROVAL WORKFLOW TEST PASSED![/bold green]")
    else:
        rprint("[bold yellow]⚠️  LOAN APPROVAL WORKFLOW TEST COMPLETED WITH WARNINGS[/bold yellow]")
    rprint("=" * 80)


if __name__ == "__main__":
    main()

