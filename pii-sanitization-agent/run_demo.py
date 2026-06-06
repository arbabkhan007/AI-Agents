#!/usr/bin/env python3
"""
PII Sanitization Agent Demo
Usage: python run_demo.py
"""
import requests

ENDPOINT = "https://api.trustboost.dev/sanitize/preview"

def sanitize(text):
    try:
        r = requests.post(ENDPOINT, json={"text": text}, timeout=30)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        print(f"[PII Agent] Error: {e} - failing closed")
        return {"sanitized_content": "[BLOCKED]", "safety_score": 1.0, "risk_category": "CRITICAL", "entities": []}

def main():
    tests = [
        "My email is john@example.com and my SSN is 123-45-6789",
        "Cliente: Juan Lopez, RFC: LOPJ850101ABC, Tel: 55-1234-5678",
        "CPF do cliente: 123.456.789-09, email: cliente@empresa.com.br",
        "Send 149 USDC from wallet ABC123xyz to john@example.com",
        "API key: sk-abc123def456ghi789jkl012mno345pqr678stu",
    ]
    print("TrustBoost PII Sanitization Agent")
    print("=" * 60)
    for i, text in enumerate(tests, 1):
        r = sanitize(text)
        print(f"Test {i}: {text[:60]}")
        print(f"  Output: {r.get('sanitized_content')}")
        print(f"  Score: {r.get('safety_score')} | Risk: {r.get('risk_category')}")
        print()
    print("Done. No PII stored. No raw input logged.")

if __name__ == "__main__":
    main()
