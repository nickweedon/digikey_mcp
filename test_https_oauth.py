#!/usr/bin/env python3
"""Test HTTPS OAuth callback server."""

import os
import sys
import time
import ssl
import urllib.request
import urllib.error
from pathlib import Path

# Add current directory to path
sys.path.insert(0, '/workspace')

def test_https_server():
    """Test that the HTTPS OAuth callback server can start."""
    print("=" * 60)
    print("Testing HTTPS OAuth Callback Server")
    print("=" * 60)

    # Check SSL certificate files exist
    ssl_cert = Path("localhost-cert.pem")
    ssl_key = Path("localhost-key.pem")

    print(f"\n1. Checking SSL certificate files...")
    if ssl_cert.exists() and ssl_key.exists():
        print(f"   ✓ SSL certificate found: {ssl_cert}")
        print(f"   ✓ SSL key found: {ssl_key}")
    else:
        print(f"   ✗ SSL files not found!")
        return False

    # Import the server module
    print(f"\n2. Importing digikey_mcp_server...")
    try:
        import digikey_mcp_server
        print(f"   ✓ Module imported successfully")
    except Exception as e:
        print(f"   ✗ Failed to import: {e}")
        return False

    # Check redirect URI configuration
    print(f"\n3. Checking OAuth configuration...")
    print(f"   REDIRECT_URI: {digikey_mcp_server.REDIRECT_URI}")
    print(f"   OAUTH_PORT: {digikey_mcp_server.OAUTH_PORT}")

    if digikey_mcp_server.REDIRECT_URI.startswith("https://"):
        print(f"   ✓ Using HTTPS redirect URI")
    else:
        print(f"   ✗ Still using HTTP redirect URI!")
        return False

    # Start the OAuth server
    print(f"\n4. Starting HTTPS OAuth callback server...")
    try:
        digikey_mcp_server.start_oauth_server()
        time.sleep(2)  # Give server time to start
        print(f"   ✓ Server started successfully")
    except Exception as e:
        print(f"   ✗ Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Try to connect to the HTTPS server
    print(f"\n5. Testing HTTPS connection to localhost:{digikey_mcp_server.OAUTH_PORT}...")
    try:
        # Create SSL context that doesn't verify the self-signed cert
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        url = f"https://localhost:{digikey_mcp_server.OAUTH_PORT}/"
        req = urllib.request.Request(url)

        try:
            response = urllib.request.urlopen(req, context=ssl_context, timeout=5)
            status = response.status
            print(f"   ✓ HTTPS connection successful (status: {status})")
        except urllib.error.HTTPError as e:
            # 404 is expected for root path, callback is at /callback
            if e.code == 404:
                print(f"   ✓ HTTPS server responding (404 for root path is expected)")
            else:
                print(f"   ⚠ Unexpected HTTP error: {e.code}")

    except Exception as e:
        print(f"   ✗ Connection failed: {e}")
        import traceback
        traceback.print_exc()
        return False

    # Check authorization URL generation
    print(f"\n6. Testing authorization URL generation...")
    try:
        auth_url = digikey_mcp_server.generate_authorization_url()
        print(f"   ✓ Auth URL generated:")
        print(f"   {auth_url[:100]}...")

        if "redirect_uri=https" in auth_url:
            print(f"   ✓ Auth URL includes HTTPS redirect URI")
        else:
            print(f"   ✗ Auth URL does not include HTTPS redirect!")
            return False

    except Exception as e:
        print(f"   ✗ Failed to generate auth URL: {e}")
        return False

    print("\n" + "=" * 60)
    print("✓ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nThe HTTPS OAuth callback server is working correctly.")
    print("When you run oauth_start_login(), the browser will open and")
    print("redirect to https://localhost:8139/callback after authorization.")
    print("\nNote: The browser will show a security warning about the")
    print("self-signed certificate. Click 'Advanced' and 'Proceed to localhost'.")

    return True

if __name__ == "__main__":
    try:
        success = test_https_server()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
