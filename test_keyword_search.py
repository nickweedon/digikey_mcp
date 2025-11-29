#!/usr/bin/env python3
"""Test script for keyword search functionality."""

import json
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import the necessary modules
from src.config import logger, CLIENT_ID, CLIENT_SECRET
from src.oauth.flow import get_client_token
from src.oauth.state import oauth_state
from src.tools.product_tools import register_product_tools
from fastmcp import FastMCP

def main():
    """Test keyword_search with 'arduino'."""
    try:
        print("=" * 60)
        print("Testing DigiKey MCP Server - keyword_search('arduino')")
        print("=" * 60)

        # Check credentials
        if not CLIENT_ID or not CLIENT_SECRET:
            print("❌ ERROR: CLIENT_ID and CLIENT_SECRET must be set in .env file")
            return 1

        print(f"\n✓ CLIENT_ID configured: {CLIENT_ID[:20]}...")

        # Initialize MCP server
        mcp = FastMCP("DigiKey Test")
        register_product_tools(mcp)

        # Get client token
        print("\n📡 Requesting OAuth2 client token...")
        oauth_state.client_token = get_client_token()
        print("✓ Successfully obtained client token")

        # Call keyword_search with "arduino"
        print(f"\n🔍 Searching for 'arduino' (limit=5)...")

        # Import API client functions
        from src.api.client import _get_headers, _make_request
        from src.config import API_BASE

        url = f"{API_BASE}/products/v4/search/keyword"
        headers = _get_headers()

        body = {
            "Keywords": "arduino",
            "Limit": 5
        }

        result = _make_request("POST", url, headers, body, use_user_token=False)

        print("\n" + "=" * 60)
        print("✓ SUCCESS - Keyword search completed")
        print("=" * 60)

        # Display results
        if isinstance(result, dict):
            products = result.get("Products", [])
            exact_count = result.get("ExactManufacturerProductsCount", 0)
            total_count = result.get("ProductsCount", 0)

            print(f"\n📊 Results Summary:")
            print(f"   Total products: {total_count}")
            print(f"   Exact matches: {exact_count}")
            print(f"   Returned: {len(products)}")

            print(f"\n📦 Products found:")
            for i, product in enumerate(products, 1):
                pn = product.get("DigiKeyPartNumber", "N/A")
                mfr_pn = product.get("ManufacturerPartNumber", "N/A")

                # Handle Manufacturer - could be dict or string
                mfr = product.get("Manufacturer")
                if isinstance(mfr, dict):
                    mfr = mfr.get("Name", "N/A")
                elif mfr is None:
                    mfr = "N/A"

                desc = product.get("ProductDescription") or product.get("Description", "N/A")

                # Get stock and pricing info
                stock = product.get("QuantityAvailable", "N/A")
                min_qty = product.get("MinimumOrderQuantity", "N/A")

                print(f"\n{i}. {pn}")
                print(f"   Manufacturer: {mfr}")
                print(f"   Mfr Part #: {mfr_pn}")
                print(f"   Stock: {stock} | Min Order: {min_qty}")
                if desc and desc != "N/A":
                    print(f"   Description: {desc[:100]}...")
        else:
            print(f"\nRaw result:\n{json.dumps(result, indent=2)}")

        return 0

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
