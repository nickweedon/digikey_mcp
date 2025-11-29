#!/usr/bin/env python3
"""Test script for keyword search with 'arduino'."""

import json
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the necessary modules
from src.config import logger, CLIENT_ID, CLIENT_SECRET
from src.oauth.flow import get_client_token
from src.oauth.state import oauth_state
from src.api.client import _get_headers, _make_request
from src.config import API_BASE

def main():
    """Test keyword_search with 'arduino'."""
    try:
        print("=" * 70)
        print("DigiKey MCP Server Test: Keyword Search for 'arduino'")
        print("=" * 70)

        # Check credentials
        if not CLIENT_ID or not CLIENT_SECRET:
            print("❌ ERROR: CLIENT_ID and CLIENT_SECRET must be set in .env file")
            return 1

        # Get client token
        print("\n📡 Authenticating with DigiKey API...")
        oauth_state.client_token = get_client_token()
        print("✓ Successfully authenticated")

        # Call keyword_search API
        print(f"\n🔍 Searching for 'arduino' (limit=5)...")

        url = f"{API_BASE}/products/v4/search/keyword"
        headers = _get_headers()

        body = {
            "Keywords": "arduino",
            "Limit": 5
        }

        result = _make_request("POST", url, headers, body, use_user_token=False)

        print("\n" + "=" * 70)
        print("✓ SEARCH SUCCESSFUL")
        print("=" * 70)

        # Display results
        if isinstance(result, dict):
            products = result.get("Products", [])
            exact_count = result.get("ExactManufacturerProductsCount", 0)
            total_count = result.get("ProductsCount", 0)

            print(f"\n📊 SEARCH SUMMARY:")
            print(f"   • Total products matching 'arduino': {total_count:,}")
            print(f"   • Exact manufacturer matches: {exact_count}")
            print(f"   • Results returned: {len(products)}")

            print(f"\n📦 TOP {len(products)} RESULTS:")
            print("-" * 70)

            for i, product in enumerate(products, 1):
                pn = product.get("DigiKeyPartNumber", "N/A")
                mfr_pn = product.get("ManufacturerPartNumber", "N/A")

                # Handle Manufacturer - could be dict or string
                mfr = product.get("Manufacturer")
                if isinstance(mfr, dict):
                    mfr = mfr.get("Name", "N/A")
                elif mfr is None:
                    mfr = "N/A"

                desc = product.get("ProductDescription") or product.get("Description", "")

                # Get stock and pricing info
                stock = product.get("QuantityAvailable")
                min_qty = product.get("MinimumOrderQuantity")
                price = product.get("UnitPrice")

                print(f"\n{i}. DigiKey Part #: {pn}")
                print(f"   Manufacturer: {mfr}")
                print(f"   Mfr Part #: {mfr_pn}")

                if stock is not None:
                    print(f"   Stock: {stock:,} units")
                if min_qty is not None:
                    print(f"   Min Order Qty: {min_qty}")
                if price is not None:
                    print(f"   Price: ${price}")
                if desc:
                    desc_short = desc[:80] + "..." if len(desc) > 80 else desc
                    print(f"   Description: {desc_short}")

            print("\n" + "=" * 70)
            print("💾 Full JSON response saved to: arduino_search_result.json")
            print("=" * 70)

            # Save full JSON response
            with open("arduino_search_result.json", "w") as f:
                json.dump(result, f, indent=2)

        else:
            print(f"\nUnexpected result format:\n{json.dumps(result, indent=2)}")

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
