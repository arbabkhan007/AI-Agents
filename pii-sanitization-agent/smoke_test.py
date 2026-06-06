#!/usr/bin/env python3
"""Smoke test for PII Sanitization Agent."""
import sys
import requests

def test_api_health():
    r = requests.get("https://api.trustboost.dev/health", timeout=10)
    assert r.status_code == 200
    assert r.json().get("status") == "ok"
    print("OK - API health check passed")

def test_pii_sanitization():
    r = requests.post(
        "https://api.trustboost.dev/sanitize/preview",
        json={"text": "My email is test@example.com"},
        timeout=30
    )
    assert r.status_code == 200
    assert "[REDACTED]" in r.json().get("sanitized_content", "")
    print("OK - PII sanitization passed")

def test_empty_input():
    r = requests.post(
        "https://api.trustboost.dev/sanitize/preview",
        json={"text": ""},
        timeout=30
    )
    assert r.status_code == 200
    print("OK - Empty input handled safely")

if __name__ == "__main__":
    print("Running smoke tests...\n")
    try:
        test_api_health()
        test_pii_sanitization()
        test_empty_input()
        print("\nAll smoke tests passed.")
        sys.exit(0)
    except Exception as e:
        print(f"\nTest failed: {e}")
        sys.exit(1)
