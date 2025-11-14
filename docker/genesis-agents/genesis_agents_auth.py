#!/usr/bin/env python3
"""
Genesis Multi-Agent TEE Application - WITH AUTHENTICATION
Alice: Loan Officer (evaluates creditworthiness)
Bob: Auditor (re-verifies Alice's evaluation)
Charlie: Borrower (requests loan)

🔐 SECURITY: Requires users to provide their own EigenAI API key
"""

import json
import os
from datetime import datetime
from typing import Dict, Any
import httpx
from flask import Flask, request, jsonify

# EigenAI configuration
EIGENAI_API_URL = os.getenv("EIGEN_API_URL", "https://eigenai.eigencloud.xyz")

app = Flask(__name__)

# ============================================================================
# AUTHENTICATION MIDDLEWARE
# ============================================================================

def get_api_key_from_request() -> str:
    """Extract EigenAI API key from request headers"""
    api_key = request.headers.get('X-EigenAI-Key')
    if not api_key:
        raise ValueError("X-EigenAI-Key header is required. Get your key from https://eigenai.eigencloud.xyz")
    return api_key


# ============================================================================
# SHARED UTILITIES
# ============================================================================

def call_eigenai(prompt: str, api_key: str, seed: int = 42) -> dict:
    """
    Call EigenAI from within TEE for deterministic LLM inference
    
    🔐 SECURITY: Uses the API key provided by the caller
    """
    if not api_key:
        raise ValueError("API key is required")
    
    headers = {
        "X-API-Key": api_key,  # ✅ Use caller's API key
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-oss-120b-f16",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert financial analyst. Provide analysis in JSON format only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 1000,
        "temperature": 0,  # ✅ Deterministic: same input → same output
        "seed": seed
    }
    
    with httpx.Client(timeout=60) as client:
        response = client.post(
            f"{EIGENAI_API_URL}/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()


# ============================================================================
# ALICE - LOAN OFFICER AGENT
# ============================================================================

def alice_evaluate_loan(
    borrower_address: str,
    loan_amount: float,
    erc8004_score: float,
    payment_history_count: int,
    stake_amount: float,
    previous_defaults: int,
    api_key: str  # ✅ Caller provides API key
) -> dict:
    """Alice evaluates loan request using on-chain metrics"""
    
    prompt = f"""Evaluate this micro-loan request:

Borrower: {borrower_address}
Requested Amount: ${loan_amount} USDC
ERC-8004 Reputation Score: {erc8004_score} (0.0-1.0 scale)
Payment History: {payment_history_count} successful payments
Stake Amount: ${stake_amount} USDC
Previous Defaults: {previous_defaults}

Evaluation Criteria:
1. Reputation Score: Must be > 0.65 for approval
2. Payment History: More history = lower risk
3. Stake: Higher stake = more skin in the game (ideally 50%+ of loan)
4. Defaults: Any defaults increase risk significantly

Provide JSON evaluation with:
{{
  "risk_score": <0-100, lower is better>,
  "decision": "APPROVE|REJECT",
  "max_loan_amount": <approved amount in USDC>,
  "creditworthiness": "excellent|good|fair|poor",
  "approval_confidence": <0.0-1.0>,
  "key_factors": ["<factor1>", "<factor2>", "<factor3>"],
  "reasoning": "<detailed explanation>",
  "recommended_interest_rate": <percentage>,
  "repayment_period_days": <days>
}}

Be conservative but fair. Consider all factors holistically."""

    eigenai_response = call_eigenai(prompt, api_key=api_key, seed=42)
    content = eigenai_response["choices"][0]["message"]["content"]
    
    # Parse JSON
    try:
        evaluation = json.loads(content)
    except json.JSONDecodeError:
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            content = content[start:end].strip()
            evaluation = json.loads(content)
        else:
            # Fallback: Conservative rejection
            evaluation = {
                "risk_score": 85,
                "decision": "REJECT",
                "max_loan_amount": 0,
                "creditworthiness": "poor",
                "approval_confidence": 0.3,
                "reasoning": "Unable to parse evaluation, defaulting to rejection for safety"
            }
    
    # Add input data for deterministic verification
    evaluation["inputs"] = {
        "borrower_address": borrower_address,
        "loan_amount": loan_amount,
        "erc8004_score": erc8004_score,
        "payment_history_count": payment_history_count,
        "stake_amount": stake_amount,
        "previous_defaults": previous_defaults
    }
    
    # Add TEE metadata
    evaluation["tee_execution"] = {
        "agent": "Alice",
        "role": "Loan Officer",
        "timestamp": datetime.now().isoformat(),
        "eigenai_job_id": eigenai_response["id"],
        "eigenai_model": eigenai_response["model"],
        "function": "evaluate_loan"
    }
    
    return evaluation


# ============================================================================
# HTTP ENDPOINTS WITH AUTHENTICATION
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check - no authentication required"""
    return jsonify({
        "status": "healthy",
        "service": "genesis-loan-approval-system",
        "version": "2.0.0-auth",
        "agents": {
            "alice": "loan-officer",
            "bob": "auditor",
            "charlie": "borrower"
        },
        "use_case": "Micro-Loan Approval with Deterministic Verification",
        "authentication": "Required: X-EigenAI-Key header"
    })


@app.route('/alice/evaluate_loan', methods=['POST'])
def alice_endpoint():
    """
    Alice's loan evaluation endpoint
    
    🔐 REQUIRES: X-EigenAI-Key header
    """
    try:
        # Get API key from request
        api_key = get_api_key_from_request()
        
        data = request.get_json()
        result = alice_evaluate_loan(
            borrower_address=data.get('borrower_address', '0xUnknown'),
            loan_amount=float(data.get('loan_amount', 50)),
            erc8004_score=float(data.get('erc8004_score', 0.5)),
            payment_history_count=int(data.get('payment_history_count', 0)),
            stake_amount=float(data.get('stake_amount', 0)),
            previous_defaults=int(data.get('previous_defaults', 0)),
            api_key=api_key  # ✅ Pass caller's API key
        )
        return jsonify(result)
    except ValueError as e:
        return jsonify({"error": str(e), "agent": "Alice"}), 401
    except Exception as e:
        return jsonify({"error": str(e), "agent": "Alice"}), 500


# Similar updates for Bob and Charlie endpoints...
# (Add authentication to all endpoints that call EigenAI)


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    print(f"🚀 Starting Genesis Micro-Loan Approval System on port {port}...")
    print(f"   🔐 Authentication: ENABLED (X-EigenAI-Key header required)")
    print(f"   Alice: Loan Officer (evaluates creditworthiness)")
    print(f"   Bob: Auditor (verifies Alice's decisions)")
    print(f"   Charlie: Borrower (requests loans)")
    print(f"")
    print(f"   Health: http://0.0.0.0:{port}/health")
    print(f"   Alice: http://0.0.0.0:{port}/alice/evaluate_loan")
    app.run(host='0.0.0.0', port=port, debug=False)

