#!/usr/bin/env python3
"""Test script for MyLists API functionality."""

import asyncio
import json
import os
import sys
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USE_SANDBOX = os.getenv("USE_SANDBOX", "false").lower() == "true"

# Set up API base URL
if USE_SANDBOX:
    TOKEN_URL = "https://sandbox-api.digikey.com/v1/oauth2/token"
    API_BASE = "https://sandbox-api.digikey.com"
else:
    TOKEN_URL = "https://api.digikey.com/v1/oauth2/token"
    API_BASE = "https://api.digikey.com"

def get_access_token():
    """Get OAuth2 access token from DigiKey."""
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError("CLIENT_ID and CLIENT_SECRET must be set in .env file")

    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    print(f"Requesting token from {'SANDBOX' if USE_SANDBOX else 'PRODUCTION'}...")
    print(f"CLIENT_ID: {CLIENT_ID[:20]}...")

    resp = requests.post(TOKEN_URL, data=data, headers=headers)

    if resp.status_code != 200:
        print(f"❌ OAuth error: {resp.status_code}")
        print(f"Response: {resp.text}")
        resp.raise_for_status()

    print("✓ Successfully obtained access token")
    return resp.json()["access_token"]

def get_all_lists(access_token, customer_id="0"):
    """Get all MyLists for the user."""
    url = f"{API_BASE}/mylists/v2/Lists"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-DIGIKEY-Client-Id": CLIENT_ID,
        "Content-Type": "application/json",
        "X-DIGIKEY-Locale-Site": "US",
        "X-DIGIKEY-Locale-Language": "en",
        "X-DIGIKEY-Locale-Currency": "USD",
        "X-DIGIKEY-Customer-Id": customer_id,
    }

    print(f"\nCalling MyLists API: {url}")
    resp = requests.get(url, headers=headers)

    print(f"Response status: {resp.status_code}")

    if resp.status_code != 200:
        print(f"❌ API error: {resp.status_code}")
        print(f"Response: {resp.text}")
        resp.raise_for_status()

    return resp.json()

def main():
    """Main test function."""
    try:
        print("=" * 60)
        print("Testing DigiKey MyLists API - get_all_lists()")
        print("=" * 60)

        # Get access token
        access_token = get_access_token()

        # Get all lists
        result = get_all_lists(access_token)

        print("\n" + "=" * 60)
        print("✓ SUCCESS - Retrieved MyLists")
        print("=" * 60)
        print(f"\nResult:")
        print(json.dumps(result, indent=2))

        # Count lists
        if isinstance(result, list):
            print(f"\n📋 Total lists found: {len(result)}")
            for i, lst in enumerate(result, 1):
                list_name = lst.get('ListName', 'Unknown')
                list_id = lst.get('ListId', 'Unknown')
                print(f"  {i}. {list_name} (ID: {list_id})")
        elif isinstance(result, dict) and 'Lists' in result:
            lists = result['Lists']
            print(f"\n📋 Total lists found: {len(lists)}")
            for i, lst in enumerate(lists, 1):
                list_name = lst.get('ListName', 'Unknown')
                list_id = lst.get('ListId', 'Unknown')
                print(f"  {i}. {list_name} (ID: {list_id})")

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
