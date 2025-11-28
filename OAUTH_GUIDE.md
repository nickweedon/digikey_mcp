# DigiKey MCP Server - OAuth Authentication Guide

## 🚀 New: Automatic OAuth Flow!

The DigiKey MCP Server now **automatically handles authentication** for you!

### Key Features:
- ✅ **Auto-launch browser** when MyLists API needs authentication
- ✅ **Save auth code to file** - survives server restarts  
- ✅ **No manual steps** - just call MyLists methods directly!

## Quick Start

### First Time
```python
# Just call any MyLists method - browser opens automatically!
lists = get_all_lists()
# 1. Browser opens to DigiKey login
# 2. You authorize the app
# 3. Auth code saved to .digikey_auth_code
# 4. Done!
```

### Every Time After
```python
# Same call - no browser needed!
lists = get_all_lists()
# Uses saved auth code from file
```

## How It Works

**File Storage**: Auth code is saved to `.digikey_auth_code`

**Auto-Launch**: When you call a MyLists method:
1. Checks for saved auth code file
2. If not found → opens browser automatically
3. After you authorize → saves to file
4. Future calls use the saved auth code

## Manual Control (Optional)

```python
# Check status
oauth_status()

# Manual login
oauth_start_login()
oauth_complete_login()

# Refresh token
oauth_refresh()

# Logout (deletes auth code file)
oauth_logout()
```

## Configuration

`.env` file:
```bash
CLIENT_ID=your_client_id
CLIENT_SECRET=your_client_secret
USE_SANDBOX=false
REDIRECT_URI=http://localhost:8139/callback
OAUTH_PORT=8139
AUTH_CODE_FILE=.digikey_auth_code
```

## Security

- Add `.digikey_auth_code` to `.gitignore`
- File permissions: `chmod 600 .digikey_auth_code`
- Logout clears both tokens and file

## Troubleshooting

**Browser doesn't open?**
- Check logs for the URL and open manually
- May not work in headless environments

**"Authentication timed out"?**
- Complete browser auth within 5 minutes
- Or increase timeout: `oauth_complete_login(timeout=600)`

**Auth code expires?**
- Server auto-detects and re-launches browser
- Old file is automatically deleted
