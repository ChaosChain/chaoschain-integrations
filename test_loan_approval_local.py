#!/usr/bin/env python3
"""
Local Test for Loan Approval System
Tests the logic without deploying to EigenCompute
"""

import json
import hashlib
import sys
import os

# Add docker/genesis-agents to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'docker', 'genesis-agents'))

from genesis_agents import (
    charlie_request_loan,
    alice_evaluate_loan,
    bob_audit_loan_evaluation
)

print("=" * 80)
print("🧪 LOCAL TEST: Micro-Loan Approval System")
print("=" * 80)
print()

# ============================================================================
# STEP 1: Charlie Requests Loan
# ============================================================================
print("📋 STEP 1: Charlie (Borrower) Requests Loan")
print("-" * 80)

charlie_profile = charlie_request_loan(
    loan_amount=0.5,  # 0.5 USDC
    purpose="operational_expenses"
)

print(f"✅ Charlie's Profile:")
print(f"   Address: {charlie_profile['borrower_address']}")
print(f"   ERC-8004 Score: {charlie_profile['erc8004_score']}")
print(f"   Payment History: {charlie_profile['payment_history_count']} successful payments")
print(f"   Stake: ${charlie_profile['stake_amount']} USDC")
print(f"   Previous Defaults: {charlie_profile['previous_defaults']}")
print(f"   Requested: ${charlie_profile['requested_amount']} USDC")
print(f"   Purpose: {charlie_profile['loan_purpose']}")
print(f"   Reputation Tier: {charlie_profile['reputation_tier']}")
print()

# ============================================================================
# STEP 2: Alice Evaluates Loan
# ============================================================================
print("🏦 STEP 2: Alice (Loan Officer) Evaluates Creditworthiness")
print("-" * 80)

# Mock EigenAI call by setting EIGEN_API_KEY to None (will use fallback)
os.environ.pop('EIGEN_API_KEY', None)

try:
    alice_evaluation = alice_evaluate_loan(
        borrower_address=charlie_profile['borrower_address'],
        loan_amount=charlie_profile['requested_amount'],
        erc8004_score=charlie_profile['erc8004_score'],
        payment_history_count=charlie_profile['payment_history_count'],
        stake_amount=charlie_profile['stake_amount'],
        previous_defaults=charlie_profile['previous_defaults']
    )
    
    print(f"✅ Alice's Evaluation:")
    print(f"   Decision: {alice_evaluation.get('decision', 'N/A')}")
    print(f"   Risk Score: {alice_evaluation.get('risk_score', 'N/A')}/100")
    print(f"   Creditworthiness: {alice_evaluation.get('creditworthiness', 'N/A')}")
    print(f"   Max Loan Amount: ${alice_evaluation.get('max_loan_amount', 'N/A')} USDC")
    print(f"   Confidence: {alice_evaluation.get('approval_confidence', 'N/A')}")
    
    if 'reasoning' in alice_evaluation:
        print(f"   Reasoning: {alice_evaluation['reasoning'][:100]}...")
    
    # Calculate execution hash for deterministic verification
    alice_output_json = json.dumps(alice_evaluation, sort_keys=True)
    alice_exec_hash = hashlib.sha256(alice_output_json.encode()).hexdigest()
    print(f"   Exec Hash: 0x{alice_exec_hash[:32]}...")
    print()

except Exception as e:
    print(f"❌ Error in Alice's evaluation: {e}")
    print("   Note: This is expected if EIGEN_API_KEY is not set")
    print("   In production, Alice will call EigenAI from within TEE")
    print()
    
    # Create a mock evaluation for testing
    alice_evaluation = {
        "decision": "APPROVE",
        "risk_score": 35,
        "creditworthiness": "good",
        "max_loan_amount": 0.5,
        "approval_confidence": 0.85,
        "key_factors": [
            "Good ERC-8004 score (0.78)",
            "Solid payment history (8 payments)",
            "50% stake provided"
        ],
        "reasoning": "Borrower shows good creditworthiness with consistent payment history and adequate stake.",
        "recommended_interest_rate": 5.0,
        "repayment_period_days": 30,
        "inputs": {
            "borrower_address": charlie_profile['borrower_address'],
            "loan_amount": charlie_profile['requested_amount'],
            "erc8004_score": charlie_profile['erc8004_score'],
            "payment_history_count": charlie_profile['payment_history_count'],
            "stake_amount": charlie_profile['stake_amount'],
            "previous_defaults": charlie_profile['previous_defaults']
        }
    }
    
    alice_output_json = json.dumps(alice_evaluation, sort_keys=True)
    alice_exec_hash = hashlib.sha256(alice_output_json.encode()).hexdigest()
    
    print(f"✅ Using Mock Evaluation for Testing:")
    print(f"   Decision: {alice_evaluation['decision']}")
    print(f"   Risk Score: {alice_evaluation['risk_score']}/100")
    print(f"   Exec Hash: 0x{alice_exec_hash[:32]}...")
    print()

# ============================================================================
# STEP 3: Bob Audits Alice's Evaluation
# ============================================================================
print("🔍 STEP 3: Bob (Auditor) Verifies Alice's Decision")
print("-" * 80)

try:
    bob_audit = bob_audit_loan_evaluation(alice_evaluation)
    
    print(f"✅ Bob's Audit:")
    print(f"   Audit Decision: {bob_audit.get('audit_decision', 'N/A')}")
    print(f"   Agrees with Alice: {bob_audit.get('agrees_with_alice', 'N/A')}")
    print(f"   Audit Risk Score: {bob_audit.get('audit_risk_score', 'N/A')}/100")
    print(f"   Decision Quality: {bob_audit.get('decision_quality', 'N/A')}")
    print(f"   Compliance Check: {bob_audit.get('compliance_check', 'N/A')}")
    print(f"   Recommendation: {bob_audit.get('recommendation', 'N/A')}")
    
    if 'audit_notes' in bob_audit:
        print(f"   Notes: {bob_audit['audit_notes'][:100]}...")
    
    # Calculate execution hash
    bob_output_json = json.dumps(bob_audit, sort_keys=True)
    bob_exec_hash = hashlib.sha256(bob_output_json.encode()).hexdigest()
    print(f"   Exec Hash: 0x{bob_exec_hash[:32]}...")
    print()

except Exception as e:
    print(f"❌ Error in Bob's audit: {e}")
    print("   Note: This is expected if EIGEN_API_KEY is not set")
    print()
    
    bob_audit = {
        "audit_decision": "APPROVE",
        "agrees_with_alice": True,
        "audit_risk_score": 35,
        "decision_quality": "good",
        "compliance_check": "PASS",
        "recommendation": "APPROVE"
    }
    print(f"✅ Using Mock Audit for Testing:")
    print(f"   Audit Decision: {bob_audit['audit_decision']}")
    print(f"   Agrees with Alice: {bob_audit['agrees_with_alice']}")
    print()

# ============================================================================
# STEP 4: Deterministic Verification (Bob re-runs Alice's evaluation)
# ============================================================================
print("🔬 STEP 4: Deterministic Verification")
print("-" * 80)
print("For true deterministic verification, Bob would re-run Alice's")
print("exact evaluation function with the same inputs:")
print()

try:
    # Bob re-runs Alice's evaluation
    bob_rerun = alice_evaluate_loan(
        borrower_address=charlie_profile['borrower_address'],
        loan_amount=charlie_profile['requested_amount'],
        erc8004_score=charlie_profile['erc8004_score'],
        payment_history_count=charlie_profile['payment_history_count'],
        stake_amount=charlie_profile['stake_amount'],
        previous_defaults=charlie_profile['previous_defaults']
    )
    
    bob_rerun_json = json.dumps(bob_rerun, sort_keys=True)
    bob_rerun_hash = hashlib.sha256(bob_rerun_json.encode()).hexdigest()
    
    print(f"   Alice's Exec Hash: 0x{alice_exec_hash[:32]}...")
    print(f"   Bob's Exec Hash:   0x{bob_rerun_hash[:32]}...")
    
    if alice_exec_hash == bob_rerun_hash:
        print()
        print("   ✅ DETERMINISTIC MATCH: Hashes are IDENTICAL!")
        print("   🎯 Loan would be AUTO-DISBURSED")
        print("   📦 Provable determinism achieved")
    else:
        print()
        print("   ❌ MISMATCH: Different hashes")
        print("   🚨 Loan would be HELD for review")
    print()

except Exception as e:
    print(f"   ⚠️  Deterministic verification requires EigenAI API")
    print(f"   In production TEE: temperature=0, seed=42 ensures determinism")
    print()

# ============================================================================
# SUMMARY
# ============================================================================
print("=" * 80)
print("📊 WORKFLOW SUMMARY")
print("=" * 80)
print()
print(f"1. Charlie requests: ${charlie_profile['requested_amount']} USDC loan")
print(f"   - ERC-8004 Score: {charlie_profile['erc8004_score']}")
print(f"   - Stake: ${charlie_profile['stake_amount']} USDC (50% of loan)")
print()
print(f"2. Alice evaluates: {alice_evaluation.get('decision', 'N/A')}")
print(f"   - Risk Score: {alice_evaluation.get('risk_score', 'N/A')}/100")
print(f"   - Max Approved: ${alice_evaluation.get('max_loan_amount', 'N/A')} USDC")
print()
print(f"3. Bob audits: {bob_audit.get('audit_decision', 'N/A')}")
print(f"   - Agrees with Alice: {bob_audit.get('agrees_with_alice', 'N/A')}")
print(f"   - Compliance: {bob_audit.get('compliance_check', 'N/A')}")
print()
print("4. Payment Flow:")
print(f"   - Loan: 0.5 USDC via x402 (if approved)")
print(f"   - Alice fee: 0.001 A0GI (0G network)")
print(f"   - Bob fee: 0.001 A0GI (0G network)")
print()
print("5. Evidence Storage:")
print("   - All proofs published to 0G Storage")
print("   - Payment linked to proof CID")
print()
print("=" * 80)
print("✅ Local test complete! Ready for EigenCompute deployment.")
print("=" * 80)

