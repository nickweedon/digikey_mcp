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
import requests

# Configuration
CLIENT_ID = os.getenv("CLIENT_ID", "NLRtXHUCuG5hmSuyOHD3r76KDG3uIB2LKGb2NGIRHK9dmqwp")
CLIENT_SECRET = os.getenv("CLIENT_SECRET", "ZlWm7P8CDJT9sOtkjJlvMG2W7Tgp5tFzUYyxrP5A4fL02nNxpeb0nGLA0b7xcasn")
REDIRECT_URI = "http://localhost:8139/callback"
TOKEN_FILE = Path(".digikey_tokens")

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
                    print("✓ Authorization code received!")
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

def exchange_code_for_tokens(code):
    """Exchange authorization code for tokens."""
    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    print("Exchanging authorization code for tokens...")
    resp = requests.post(TOKEN_URL, data=data, headers=headers)

    if resp.status_code != 200:
        print(f"✗ Token exchange error: {resp.status_code} - {resp.text}")
        return None

    token_data = resp.json()
    return token_data

def save_tokens(user_token, refresh_token):
    """Save tokens to file."""
    with open(TOKEN_FILE, 'w') as f:
        json.dump({
            "user_token": user_token,
            "refresh_token": refresh_token,
            "timestamp": time.time()
        }, f, indent=2)
    print(f"✓ Tokens saved to {TOKEN_FILE}")

def test_oauth_flow():
    """Test the OAuth flow."""
    global auth_state, auth_code

    print("=" * 60)
    print("DigiKey OAuth Flow Test")
    print("=" * 60)

    # Check if token file exists
    if TOKEN_FILE.exists():
        print(f"\n✓ Found existing token file: {TOKEN_FILE}")
        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)
        if "user_token" in data:
            print(f"  User token: {data['user_token'][:20]}...")
            print(f"  Saved at: {time.ctime(data['timestamp'])}")
            print("\n✓ Tokens already saved - would skip browser!")
            return True

    print(f"\n✗ No token file found: {TOKEN_FILE}")
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
        print(f"\n✓ Authorization code received")
        print(f"  Code: {auth_code[:20]}...")

        # Exchange code for tokens
        token_data = exchange_code_for_tokens(auth_code)
        if token_data:
            user_token = token_data.get("access_token")
            refresh_token = token_data.get("refresh_token")
            save_tokens(user_token, refresh_token)
            return True
        else:
            print("✗ Failed to exchange code for tokens")
            return False
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
            print(f"\nTokens saved to: {TOKEN_FILE}")
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
