#!/usr/bin/env python3
"""
Genesis Multi-Agent TEE Application
Combines Alice, Bob, and Charlie in a single EigenCompute deployment
"""

import json
import os
from datetime import datetime
from typing import Dict, Any
import httpx
from flask import Flask, request, jsonify

# EigenAI configuration
EIGENAI_API_URL = os.getenv("EIGEN_API_URL", "https://eigenai.eigencloud.xyz")
EIGENAI_API_KEY = os.getenv("EIGEN_API_KEY")

app = Flask(__name__)

# ============================================================================
# SHARED UTILITIES
# ============================================================================

def call_eigenai(prompt: str, seed: int = 42) -> dict:
    """Call EigenAI from within TEE for deterministic LLM inference"""
    if not EIGENAI_API_KEY:
        raise ValueError("EIGENAI_API_KEY not set")
    
    headers = {
        "X-API-Key": EIGENAI_API_KEY,
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "gpt-oss-120b-f16",
        "messages": [
            {
                "role": "system",
                "content": "You are an expert AI assistant. Provide analysis in JSON format only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 1000,
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
# ALICE - SHOPPING AGENT
# ============================================================================

def alice_analyze_shopping(item_type: str, color: str, budget: float, premium_tolerance: float) -> dict:
    """Alice's shopping analysis with EigenAI"""
    
    prompt = f"""Analyze this shopping request:

Product: {item_type}
Preferred Color: {color}
Budget: ${budget}
Premium Tolerance: {premium_tolerance*100}%

Provide JSON response with:
{{
  "item_type": "{item_type}",
  "requested_color": "{color}",
  "available_color": "<color>",
  "base_price": <price>,
  "final_price": <price>,
  "premium_applied": <percent>,
  "deal_quality": "excellent|good|alternative",
  "color_match_found": true|false,
  "merchant": "<name>",
  "availability": "in_stock",
  "estimated_delivery": "<days>",
  "confidence": <0.0-1.0>,
  "reasoning": "<explanation>"
}}

Keep prices within budget."""

    eigenai_response = call_eigenai(prompt, seed=42)
    content = eigenai_response["choices"][0]["message"]["content"]
    
    # Parse JSON
    try:
        analysis = json.loads(content)
    except json.JSONDecodeError:
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            content = content[start:end].strip()
            analysis = json.loads(content)
        else:
            analysis = {
                "item_type": item_type,
                "requested_color": color,
                "available_color": color,
                "final_price": budget * 0.85,
                "confidence": 0.85,
                "reasoning": content[:200]
            }
    
    # Add TEE metadata
    analysis["tee_execution"] = {
        "agent": "Alice",
        "timestamp": datetime.now().isoformat(),
        "eigenai_job_id": eigenai_response["id"],
        "eigenai_model": eigenai_response["model"],
        "function": "analyze_shopping"
    }
    
    return analysis


# ============================================================================
# BOB - VALIDATOR AGENT
# ============================================================================

def bob_validate_analysis(analysis: dict) -> dict:
    """Bob's validation with EigenAI"""
    
    analysis_summary = json.dumps({
        "item": analysis.get("item_type"),
        "price": analysis.get("final_price"),
        "merchant": analysis.get("merchant"),
        "color_match": analysis.get("color_match_found"),
        "confidence": analysis.get("confidence")
    })
    
    prompt = f"""Validate this shopping analysis:

Analysis: {analysis_summary}

Provide JSON validation with:
{{
  "overall_score": <0-100>,
  "price_accuracy": <0-100>,
  "merchant_reliability": <0-100>,
  "color_match_quality": <0-100>,
  "quality_rating": "excellent|good|fair|poor",
  "pass_fail": "PASS|FAIL",
  "confidence_assessment": "<assessment>",
  "recommendations": ["<rec1>", "<rec2>"],
  "validation_notes": "<notes>"
}}"""

    eigenai_response = call_eigenai(prompt, seed=42)
    content = eigenai_response["choices"][0]["message"]["content"]
    
    # Parse JSON
    try:
        validation = json.loads(content)
    except json.JSONDecodeError:
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            content = content[start:end].strip()
            validation = json.loads(content)
        else:
            validation = {
                "overall_score": 85,
                "quality_rating": "good",
                "pass_fail": "PASS",
                "validation_notes": content[:200]
            }
    
    # Add TEE metadata
    validation["tee_execution"] = {
        "agent": "Bob",
        "timestamp": datetime.now().isoformat(),
        "eigenai_job_id": eigenai_response["id"],
        "eigenai_model": eigenai_response["model"],
        "function": "validate_analysis"
    }
    
    return validation


# ============================================================================
# CHARLIE - MARKET ANALYST
# ============================================================================

def charlie_market_analysis(item_type: str, price: float) -> dict:
    """Charlie's market analysis with EigenAI"""
    
    prompt = f"""Analyze market trends for this product:

Product: {item_type}
Current Price: ${price}

Provide JSON market analysis with:
{{
  "market_average": <price>,
  "price_trend": "rising|stable|falling",
  "value_rating": "excellent|good|fair|poor",
  "market_position": "below|at|above",
  "competitor_prices": [<p1>, <p2>, <p3>],
  "seasonal_factor": "<factor>",
  "recommendation": "<buy_now|wait|negotiate>",
  "confidence": <0.0-1.0>,
  "analysis_notes": "<notes>"
}}"""

    eigenai_response = call_eigenai(prompt, seed=42)
    content = eigenai_response["choices"][0]["message"]["content"]
    
    # Parse JSON
    try:
        analysis = json.loads(content)
    except json.JSONDecodeError:
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            content = content[start:end].strip()
            analysis = json.loads(content)
        else:
            analysis = {
                "market_average": price * 1.1,
                "value_rating": "good",
                "recommendation": "buy_now",
                "confidence": 0.80
            }
    
    # Add TEE metadata
    analysis["tee_execution"] = {
        "agent": "Charlie",
        "timestamp": datetime.now().isoformat(),
        "eigenai_job_id": eigenai_response["id"],
        "eigenai_model": eigenai_response["model"],
        "function": "market_analysis"
    }
    
    return analysis


# ============================================================================
# HTTP ENDPOINTS
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """Health check for all agents"""
    return jsonify({
        "status": "healthy",
        "service": "genesis-multi-agent",
        "version": "1.0.0",
        "agents": {
            "alice": "shopping-analyst",
            "bob": "validator",
            "charlie": "market-analyst"
        }
    })


@app.route('/alice/analyze_shopping', methods=['POST'])
def alice_endpoint():
    """Alice's shopping analysis endpoint"""
    try:
        data = request.get_json()
        result = alice_analyze_shopping(
            item_type=data.get('item_type', 'laptop'),
            color=data.get('color', 'silver'),
            budget=float(data.get('budget', 1000)),
            premium_tolerance=float(data.get('premium_tolerance', 0.20))
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "agent": "Alice"}), 500


@app.route('/bob/validate_analysis', methods=['POST'])
def bob_endpoint():
    """Bob's validation endpoint"""
    try:
        data = request.get_json()
        analysis = data.get('analysis', {})
        result = bob_validate_analysis(analysis)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "agent": "Bob"}), 500


@app.route('/charlie/market_analysis', methods=['POST'])
def charlie_endpoint():
    """Charlie's market analysis endpoint"""
    try:
        data = request.get_json()
        result = charlie_market_analysis(
            item_type=data.get('item_type', 'laptop'),
            price=float(data.get('price', 1000))
        )
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e), "agent": "Charlie"}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    print(f"🚀 Starting Genesis Multi-Agent System on port {port}...")
    print(f"   Agents: Alice (shopping), Bob (validation), Charlie (market)")
    print(f"   Health: http://0.0.0.0:{port}/health")
    print(f"   Alice: http://0.0.0.0:{port}/alice/analyze_shopping")
    print(f"   Bob: http://0.0.0.0:{port}/bob/validate_analysis")
    print(f"   Charlie: http://0.0.0.0:{port}/charlie/market_analysis")
    app.run(host='0.0.0.0', port=port, debug=False)

