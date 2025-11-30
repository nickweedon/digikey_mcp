# DigiKey MCP Server - OAuth Authentication Guide

## 🚀 New: Automatic OAuth Flow!

The DigiKey MCP Server now **automatically handles authentication** for you!

### Key Features:
- ✅ **Auto-launch browser** when MyLists API needs authentication
- ✅ **Save tokens to file** - survives server restarts
- ✅ **No manual steps** - just call MyLists methods directly!

## Quick Start

### First Time
```python
# Just call any MyLists method - browser opens automatically!
lists = get_all_lists()
# 1. Browser opens to DigiKey login
# 2. You authorize the app
# 3. Tokens saved to .digikey_tokens
# 4. Done!
```

### Every Time After
```python
# Same call - no browser needed!
lists = get_all_lists()
# Uses saved tokens from file
```

## How It Works

**File Storage**: OAuth tokens are saved to `.digikey_tokens`

**Auto-Launch**: When you call a MyLists method:
1. Checks for saved token file
2. If not found → opens browser automatically
3. After you authorize → exchanges code for tokens and saves to file
4. Future calls use the saved tokens

## Manual Control (Optional)

```python
# Check status
oauth_status()

# Manual login
oauth_start_login()
oauth_complete_login()

# Refresh token
oauth_refresh()

# Logout (deletes token file)
oauth_logout()
```

## Configuration

`.env` file:
```bash
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
USE_SANDBOX=false
REDIRECT_URI=https://localhost:8139/callback
OAUTH_PORT=8139
TOKEN_FILE=.digikey_tokens
SSL_CERT_FILE=localhost-cert.pem
SSL_KEY_FILE=localhost-key.pem
```

## SSL Certificate Setup

The server uses HTTPS for the OAuth callback endpoint. SSL certificates are required:

### Generate Self-Signed Certificate (for development):
```bash
openssl req -x509 -newkey rsa:4096 -nodes \
  -keyout localhost-key.pem \
  -out localhost-cert.pem \
  -days 365 \
  -subj "/CN=localhost" \
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
```

### Browser Security Warning
When you complete OAuth authorization, your browser will show a security warning because of the self-signed certificate. This is **normal and expected**. You need to:
1. Click "Advanced" or "Show Details"
2. Click "Proceed to localhost" or "Accept the Risk"
3. The callback will then complete successfully

### Production Deployment
For production, use a proper SSL certificate from a trusted Certificate Authority (CA) instead of a self-signed certificate.

## Security

- Add `.digikey_tokens` and `*.pem` files to `.gitignore`
- File permissions: `chmod 600 .digikey_tokens localhost-key.pem`
- Logout clears both in-memory tokens and the token file
- SSL certificate files should not be committed to version control

## Troubleshooting

**Browser doesn't open?**
- Check logs for the URL and open manually
- May not work in headless environments

**"Authentication timed out"?**
- Complete browser auth within 5 minutes
- Or increase timeout: `oauth_complete_login(timeout=600)`

**Token expires?**
- Server auto-refreshes using the refresh token
- If refresh fails, re-authenticate via browser
