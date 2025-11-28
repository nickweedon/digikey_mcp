#!/usr/bin/env python3
"""Standalone test for OAuth flow (no FastMCP required)."""

import os
import json
import webbrowser
import time
import secrets
import urllib.parse
from pathlib import Path
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

# Configuration
CLIENT_ID = os.getenv("CLIENT_ID", "NLRtXHUCuG5hmSuyOHD3r76KDG3uIB2LKGb2NGIRHK9dmqwp")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "ZlWm7P8CDJT9sOtkjJlvMG2W7Tgp5tFzUYyxrP5A4fL02nNxpeb0nGLA0b7xcasn")
REDIRECT_URI = "http://localhost:8139/callback"
AUTH_CODE_FILE = Path(".digikey_auth_code")

# API endpoints
TOKEN_URL = "https://api.digikey.com/v1/oauth2/token"
AUTHORIZE_URL = "https://api.digikey.com/v1/oauth2/authorize"

# State storage
auth_state = None
auth_code = None

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """Handle OAuth callback."""

    def do_GET(self):
        global auth_code
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == '/callback':
            params = urllib.parse.parse_qs(parsed.query)

            if 'code' in params:
                code = params['code'][0]
                state = params.get('state', [None])[0]

                if state == auth_state:
                    auth_code = code

                    # Save to file
                    with open(AUTH_CODE_FILE, 'w') as f:
                        json.dump({
                            "auth_code": code,
                            "state": state,
                            "timestamp": time.time()
                        }, f, indent=2)

                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    html = """
                    <html>
                    <head><title>Success!</title></head>
                    <body style="font-family: Arial; text-align: center; padding: 50px;">
                        <h1 style="color: #28a745;">✓ Authorization Successful!</h1>
                        <p>You can close this window.</p>
                    </body>
                    </html>
                    """
                    self.wfile.write(html.encode('utf-8'))
                    print("✓ Authorization code received and saved!")
                else:
                    self.send_response(400)
                    self.end_headers()
                    print("✗ State mismatch!")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Silence server logs

def start_callback_server():
    """Start the callback server in background."""
    server = HTTPServer(('localhost', 8139), OAuthCallbackHandler)
    print(f"✓ Callback server started on http://localhost:8139")

    def run():
        server.serve_forever()

    thread = threading.Thread(target=run, daemon=True)
    thread.start()
    return server

def test_oauth_flow():
    """Test the OAuth flow."""
    global auth_state, auth_code

    print("=" * 60)
    print("DigiKey OAuth Flow Test")
    print("=" * 60)

    # Check if auth code file exists
    if AUTH_CODE_FILE.exists():
        print(f"\n✓ Found existing auth code file: {AUTH_CODE_FILE}")
        with open(AUTH_CODE_FILE, 'r') as f:
            data = json.load(f)
        print(f"  Auth code: {data['auth_code'][:20]}...")
        print(f"  Saved at: {time.ctime(data['timestamp'])}")
        print("\n✓ Auto-launch would skip browser (file exists)")
        return True

    print(f"\n✗ No auth code file found: {AUTH_CODE_FILE}")
    print("✓ Auto-launch would open browser now!\n")

    # Start callback server
    server = start_callback_server()

    # Generate state
    auth_state = secrets.token_urlsafe(32)

    # Build authorization URL
    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "state": auth_state,
    }
    auth_url = f"{AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"

    print(f"Authorization URL generated:")
    print(f"{auth_url}\n")

    # Auto-launch browser
    print("🌐 Launching browser...")
    try:
        webbrowser.open(auth_url)
        print("✓ Browser launched successfully!\n")
    except Exception as e:
        print(f"✗ Failed to launch browser: {e}")
        print(f"\nPlease open this URL manually:")
        print(auth_url)

    # Wait for callback
    print("⏳ Waiting for authorization (timeout: 60s)...")
    timeout = 60
    start = time.time()

    while not auth_code and (time.time() - start) < timeout:
        time.sleep(0.5)

    if auth_code:
        print(f"\n✓ SUCCESS! Authorization code received")
        print(f"  Code: {auth_code[:20]}...")
        print(f"  Saved to: {AUTH_CODE_FILE}")
        return True
    else:
        print(f"\n✗ TIMEOUT: No authorization code received in {timeout}s")
        return False

if __name__ == "__main__":
    try:
        success = test_oauth_flow()

        if success:
            print("\n" + "=" * 60)
            print("✓ OAuth Flow Test PASSED")
            print("=" * 60)
            print(f"\nAuth code saved to: {AUTH_CODE_FILE}")
            print("Next time this runs, it will skip the browser!")
        else:
            print("\n" + "=" * 60)
            print("✗ OAuth Flow Test FAILED")
            print("=" * 60)

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
