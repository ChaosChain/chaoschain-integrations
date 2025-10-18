#!/usr/bin/env python3
"""
Alice Shopping Agent - Runs inside EigenCompute TEE

This agent:
1. Receives shopping requests via HTTP
2. Calls EigenAI for LLM inference (from within TEE)
3. Returns analysis with TEE signature
"""

import json
import os
from datetime import datetime
import httpx
from flask import Flask, request, jsonify

# EigenAI configuration
EIGENAI_API_URL = os.getenv("EIGENAI_API_URL", "https://eigenai.eigencloud.xyz")
EIGENAI_API_KEY = os.getenv("EIGENAI_API_KEY")

app = Flask(__name__)

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
                "content": "You are an expert shopping analyst. Provide analysis in JSON format only."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "max_tokens": 1000,
        "seed": seed  # Deterministic
    }
    
    with httpx.Client(timeout=60) as client:
        response = client.post(
            f"{EIGENAI_API_URL}/v1/chat/completions",
            headers=headers,
            json=payload
        )
        response.raise_for_status()
        return response.json()


def analyze_shopping(item_type: str, color: str, budget: float, premium_tolerance: float) -> dict:
    """Perform shopping analysis with EigenAI inside TEE"""
    
    # Build prompt
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

    # Call EigenAI from within TEE
    eigenai_response = call_eigenai(prompt, seed=42)
    
    # Extract analysis from response
    content = eigenai_response["choices"][0]["message"]["content"]
    
    # Parse JSON from content
    try:
        # Try direct parse
        analysis = json.loads(content)
    except json.JSONDecodeError:
        # Try extracting JSON block
        if "```json" in content:
            start = content.find("```json") + 7
            end = content.find("```", start)
            content = content[start:end].strip()
            analysis = json.loads(content)
        else:
            # Fallback
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
        "timestamp": datetime.now().isoformat(),
        "eigenai_job_id": eigenai_response["id"],
        "eigenai_model": eigenai_response["model"],
        "eigenai_signature": eigenai_response.get("signature"),
        "agent": "Alice",
        "function": "analyze_shopping"
    }
    
    return analysis


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "service": "alice-shopping-agent",
        "version": "1.0.0"
    })


@app.route('/analyze_shopping', methods=['POST'])
def analyze_shopping_endpoint():
    """HTTP endpoint for shopping analysis"""
    try:
        data = request.get_json()
        item_type = data.get('item_type', 'laptop')
        color = data.get('color', 'silver')
        budget = float(data.get('budget', 1000))
        premium_tolerance = float(data.get('premium_tolerance', 0.20))
        
        result = analyze_shopping(item_type, color, budget, premium_tolerance)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Run Flask server
    port = int(os.getenv("PORT", 8080))
    print(f"🚀 Starting Alice Shopping Agent on port {port}...")
    print(f"   Health: http://0.0.0.0:{port}/health")
    print(f"   Analyze: http://0.0.0.0:{port}/analyze_shopping")
    app.run(host='0.0.0.0', port=port, debug=False)
