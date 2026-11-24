#!/usr/bin/env python3
"""Quick test to verify API keys are working."""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from dotenv import load_dotenv
from apify_client import ApifyClient
from openai import OpenAI

load_dotenv()

def test_apify():
    """Test Apify API key."""
    print("Testing Apify API key...")
    api_key = os.getenv("APIFY_API_KEY")

    if not api_key:
        print("❌ APIFY_API_KEY not found in .env")
        return False

    try:
        client = ApifyClient(api_key)
        # Simple test - get user info
        user = client.user().get()
        print(f"✅ Apify connected! Username: {user.get('username')}")
        return True
    except Exception as e:
        print(f"❌ Apify error: {e}")
        return False

def test_openai():
    """Test OpenAI API key."""
    print("\nTesting OpenAI API key...")
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        print("❌ OPENAI_API_KEY not found in .env")
        return False

    try:
        client = OpenAI(api_key=api_key)
        # Simple test - list models
        models = client.models.list()
        print(f"✅ OpenAI connected! Models available: {len(list(models.data))}")
        return True
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return False

if __name__ == "__main__":
    print("=== API Key Test ===\n")

    apify_ok = test_apify()
    openai_ok = test_openai()

    print("\n=== Results ===")
    if apify_ok and openai_ok:
        print("✅ All API keys working!")
        print("\nReady to run: python scripts/analyze_creators.py")
    else:
        print("❌ Some API keys failed. Check your .env file.")
        sys.exit(1)
