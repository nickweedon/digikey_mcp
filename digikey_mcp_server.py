import os
import json
import logging
import secrets
import threading
import urllib.parse
import webbrowser
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from fastmcp import FastMCP
from dotenv import load_dotenv
from pathlib import Path
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USE_SANDBOX = os.getenv("USE_SANDBOX", "true").lower() == "false"
REDIRECT_URI = os.getenv("REDIRECT_URI", "http://localhost:8139/callback")
OAUTH_PORT = int(os.getenv("OAUTH_PORT", "8139"))

# Auth code file storage
AUTH_CODE_FILE = Path(os.getenv("AUTH_CODE_FILE", ".digikey_auth_code"))

# DigiKey OAuth2 endpoints
if USE_SANDBOX:
    TOKEN_URL = "https://sandbox-api.digikey.com/v1/oauth2/token"
    AUTHORIZE_URL = "https://sandbox-api.digikey.com/v1/oauth2/authorize"
    API_BASE = "https://sandbox-api.digikey.com"
else:
    TOKEN_URL = "https://api.digikey.com/v1/oauth2/token"
    AUTHORIZE_URL = "https://api.digikey.com/v1/oauth2/authorize"
    API_BASE = "https://api.digikey.com"

# Initialize FastMCP server
mcp = FastMCP("DigiKey MCP Server")

# ============================================================================
# OAuth State Management
# ============================================================================

class OAuthState:
    """Manages OAuth state and tokens."""
    def __init__(self):
        self.client_token = None  # Client credentials token for Product Search API
        self.user_token = None    # User token for MyLists API
        self.refresh_token = None # Refresh token for token renewal
        self.auth_state = None    # State parameter for CSRF protection
        self.auth_code = None     # Authorization code from callback
        self.server_thread = None # HTTP server thread
        self.http_server = None   # HTTP server instance

    def has_user_token(self):
        """Check if user token is available."""
        return self.user_token is not None

oauth_state = OAuthState()

# ============================================================================
# Auth Code File Storage
# ============================================================================

def save_auth_code(code: str, state: str):
    """Save authorization code to file."""
    try:
        data = {
            "auth_code": code,
            "state": state,
            "timestamp": time.time()
        }
        with open(AUTH_CODE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"✓ Authorization code saved to {AUTH_CODE_FILE}")
    except Exception as e:
        logger.error(f"Failed to save auth code: {e}")

def load_auth_code():
    """Load authorization code from file."""
    try:
        if not AUTH_CODE_FILE.exists():
            logger.debug(f"Auth code file not found: {AUTH_CODE_FILE}")
            return None

        with open(AUTH_CODE_FILE, 'r') as f:
            data = json.load(f)

        logger.info(f"✓ Authorization code loaded from {AUTH_CODE_FILE}")
        return data
    except Exception as e:
        logger.error(f"Failed to load auth code: {e}")
        return None

def delete_auth_code_file():
    """Delete the authorization code file."""
    try:
        if AUTH_CODE_FILE.exists():
            AUTH_CODE_FILE.unlink()
            logger.info(f"✓ Deleted auth code file: {AUTH_CODE_FILE}")
    except Exception as e:
        logger.error(f"Failed to delete auth code file: {e}")


def auto_launch_oauth_if_needed():
    """Automatically launch OAuth flow if no auth code file exists."""
    # Check if auth code file exists
    if AUTH_CODE_FILE.exists():
        logger.info("Auth code file exists, loading existing authorization...")
        return False

    logger.info("No auth code file found. Launching OAuth flow...")

    # Start the OAuth server
    start_oauth_server()

    # Generate authorization URL
    auth_url = generate_authorization_url()

    logger.info(f"Opening browser to: {auth_url}")

    # Open the authorization URL in the default browser
    try:
        webbrowser.open(auth_url)
        logger.info("✓ Browser launched successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to open browser: {e}")
        logger.info(f"Please manually open this URL: {auth_url}")
        return True

# ============================================================================
# OAuth Callback HTTP Server
# ============================================================================

class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback."""

    def do_GET(self):
        """Handle GET requests to the callback endpoint."""
        # Parse the URL and query parameters
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == '/callback':
            params = urllib.parse.parse_qs(parsed.query)

            # Check for authorization code
            if 'code' in params:
                code = params['code'][0]
                state = params.get('state', [None])[0]

                # Verify state matches
                if state == oauth_state.auth_state:
                    oauth_state.auth_code = code

                    # Save auth code to file
                    save_auth_code(code, state)

                    # Send success page
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    html_response = """
                    <html>
                    <head><title>Authorization Successful</title></head>
                    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; text-align: center;">
                        <h1 style="color: #28a745;">&#10003; Authorization Successful!</h1>
                        <p>You have successfully authorized the DigiKey MCP Server.</p>
                        <p>You can now close this window and return to your application.</p>
                        <p style="margin-top: 30px; color: #666;">The server will now exchange the authorization code for an access token.</p>
                    </body>
                    </html>
                    """
                    self.wfile.write(html_response.encode('utf-8'))

                    logger.info("✓ Authorization code received successfully")
                else:
                    # State mismatch - possible CSRF attack
                    self.send_response(400)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    html_response = """
                    <html>
                    <head><title>Authorization Failed</title></head>
                    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; text-align: center;">
                        <h1 style="color: #dc3545;">&#10007; Authorization Failed</h1>
                        <p>State parameter mismatch. Possible CSRF attack detected.</p>
                        <p>Please try again.</p>
                    </body>
                    </html>
                    """
                    self.wfile.write(html_response.encode('utf-8'))
                    logger.error("State parameter mismatch in OAuth callback")

            elif 'error' in params:
                # User denied authorization
                error = params['error'][0]
                error_desc = params.get('error_description', ['Unknown error'])[0]

                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html_response = f"""
                <html>
                <head><title>Authorization Denied</title></head>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; text-align: center;">
                    <h1 style="color: #dc3545;">&#10007; Authorization Denied</h1>
                    <p><strong>Error:</strong> {error}</p>
                    <p><strong>Description:</strong> {error_desc}</p>
                </body>
                </html>
                """
                self.wfile.write(html_response.encode('utf-8'))
                logger.warning(f"User denied authorization: {error} - {error_desc}")
        else:
            # Unknown path
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Override to use our logger instead of printing to stderr."""
        logger.debug(f"OAuth callback server: {format % args}")

def start_oauth_server():
    """Start the OAuth callback HTTP server in a background thread."""
    if oauth_state.server_thread and oauth_state.server_thread.is_alive():
        logger.info("OAuth callback server already running")
        return

    def run_server():
        try:
            oauth_state.http_server = HTTPServer(('localhost', OAUTH_PORT), OAuthCallbackHandler)
            logger.info(f"✓ OAuth callback server started on http://localhost:{OAUTH_PORT}")
            oauth_state.http_server.serve_forever()
        except Exception as e:
            logger.error(f"OAuth callback server error: {e}")

    oauth_state.server_thread = threading.Thread(target=run_server, daemon=True)
    oauth_state.server_thread.start()

def stop_oauth_server():
    """Stop the OAuth callback HTTP server."""
    if oauth_state.http_server:
        oauth_state.http_server.shutdown()
        logger.info("OAuth callback server stopped")

# ============================================================================
# OAuth Functions
# ============================================================================

def get_client_token():
    """Get OAuth2 client credentials token for Product Search API."""
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError("CLIENT_ID and CLIENT_SECRET must be set in .env file")

    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    endpoint = "SANDBOX" if USE_SANDBOX else "PRODUCTION"
    logger.info(f"Requesting client token from {endpoint}...")
    resp = requests.post(TOKEN_URL, data=data, headers=headers)

    if resp.status_code != 200:
        logger.error(f"OAuth error: {resp.status_code} - {resp.text}")
        resp.raise_for_status()

    logger.info("✓ Successfully obtained client credentials token")
    return resp.json()["access_token"]

def generate_authorization_url():
    """Generate the OAuth authorization URL for user login."""
    # Generate random state for CSRF protection
    oauth_state.auth_state = secrets.token_urlsafe(32)

    params = {
        "response_type": "code",
        "client_id": CLIENT_ID,
        "redirect_uri": REDIRECT_URI,
        "state": oauth_state.auth_state,
    }

    url = f"{AUTHORIZE_URL}?{urllib.parse.urlencode(params)}"
    return url

def exchange_code_for_token(code: str):
    """Exchange authorization code for access and refresh tokens."""
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError("CLIENT_ID and CLIENT_SECRET must be set in .env file")

    data = {
        "grant_type": "authorization_code",
        "code": code,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "redirect_uri": REDIRECT_URI,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    logger.info("Exchanging authorization code for tokens...")
    resp = requests.post(TOKEN_URL, data=data, headers=headers)

    if resp.status_code != 200:
        logger.error(f"Token exchange error: {resp.status_code} - {resp.text}")
        resp.raise_for_status()

    token_data = resp.json()
    oauth_state.user_token = token_data["access_token"]
    oauth_state.refresh_token = token_data.get("refresh_token")

    logger.info("✓ Successfully obtained user access token")
    return token_data

def refresh_user_token():
    """Refresh the user access token using the refresh token."""
    if not oauth_state.refresh_token:
        raise ValueError("No refresh token available. User must re-authenticate.")

    data = {
        "grant_type": "refresh_token",
        "refresh_token": oauth_state.refresh_token,
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}

    logger.info("Refreshing user access token...")
    resp = requests.post(TOKEN_URL, data=data, headers=headers)

    if resp.status_code != 200:
        logger.error(f"Token refresh error: {resp.status_code} - {resp.text}")
        oauth_state.user_token = None
        oauth_state.refresh_token = None
        resp.raise_for_status()

    token_data = resp.json()
    oauth_state.user_token = token_data["access_token"]
    oauth_state.refresh_token = token_data.get("refresh_token", oauth_state.refresh_token)

    logger.info("✓ Successfully refreshed user access token")
    return token_data

# ============================================================================
# MCP Tools for OAuth Management
# ============================================================================

@mcp.tool()
def oauth_start_login():
    """Start the OAuth login process for MyLists API access.

    This will:
    1. Start a local HTTP server to receive the OAuth callback
    2. Generate an authorization URL
    3. Return the URL for the user to visit in their browser

    After visiting the URL and logging in, the server will automatically
    receive the authorization code and exchange it for an access token.

    Returns:
        dict: Contains the authorization URL and instructions
    """
    # Start the callback server
    start_oauth_server()

    # Generate authorization URL
    auth_url = generate_authorization_url()

    return {
        "status": "ready",
        "authorization_url": auth_url,
        "instructions": [
            "1. Open the authorization_url in your web browser",
            "2. Log in to your DigiKey account",
            "3. Authorize the application to access your MyLists",
            "4. You will be redirected to a success page",
            "5. Call oauth_complete_login() to finalize the authentication"
        ],
        "redirect_uri": REDIRECT_URI
    }

@mcp.tool()
def oauth_complete_login(timeout: int = 300):
    """Complete the OAuth login process by exchanging the authorization code for tokens.

    This should be called after the user has visited the authorization URL
    and been redirected back to the callback server.

    Args:
        timeout: Maximum seconds to wait for the authorization code (default: 300)

    Returns:
        dict: Status of the login completion
    """
    import time

    # Wait for authorization code
    logger.info(f"Waiting for authorization code (timeout: {timeout}s)...")
    start_time = time.time()

    while not oauth_state.auth_code and (time.time() - start_time) < timeout:
        time.sleep(1)

    if not oauth_state.auth_code:
        return {
            "status": "timeout",
            "error": f"No authorization code received within {timeout} seconds",
            "suggestion": "Please call oauth_start_login() again and complete the browser authorization"
        }

    # Exchange code for token
    try:
        token_data = exchange_code_for_token(oauth_state.auth_code)

        # Clear the authorization code
        oauth_state.auth_code = None
        oauth_state.auth_state = None

        return {
            "status": "success",
            "message": "Successfully authenticated with DigiKey",
            "token_type": token_data.get("token_type"),
            "expires_in": token_data.get("expires_in"),
            "has_refresh_token": oauth_state.refresh_token is not None
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@mcp.tool()
def oauth_status():
    """Check the current OAuth authentication status.

    Returns:
        dict: Current authentication status
    """
    return {
        "client_token_available": oauth_state.client_token is not None,
        "user_token_available": oauth_state.user_token is not None,
        "refresh_token_available": oauth_state.refresh_token is not None,
        "oauth_server_running": oauth_state.server_thread and oauth_state.server_thread.is_alive(),
        "message": "User authenticated" if oauth_state.user_token else "User not authenticated - call oauth_start_login() to begin"
    }

@mcp.tool()
def oauth_refresh():
    """Refresh the user access token using the refresh token.

    Returns:
        dict: Status of the token refresh
    """
    if not oauth_state.refresh_token:
        return {
            "status": "error",
            "error": "No refresh token available",
            "suggestion": "User must re-authenticate using oauth_start_login()"
        }

    try:
        token_data = refresh_user_token()
        return {
            "status": "success",
            "message": "Successfully refreshed access token",
            "expires_in": token_data.get("expires_in")
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }

@mcp.tool()
def oauth_logout():
    """Log out and clear all stored tokens.

    Returns:
        dict: Confirmation of logout
    """
    oauth_state.user_token = None
    oauth_state.refresh_token = None
    oauth_state.auth_code = None
    oauth_state.auth_state = None

    # Delete the auth code file
    delete_auth_code_file()

    return {
        "status": "success",
        "message": "Logged out successfully. All tokens and saved auth code cleared."
    }

# ============================================================================
# API Request Helpers
# ============================================================================

def _get_headers(customer_id: str = "0", use_user_token: bool = False):
    """Get standard headers for DigiKey API requests.

    Args:
        customer_id: Customer ID for the request
        use_user_token: If True, use user token (for MyLists), otherwise use client token
    """
    token = oauth_state.user_token if use_user_token else oauth_state.client_token

    return {
        "Authorization": f"Bearer {token}",
        "X-DIGIKEY-Client-Id": CLIENT_ID,
        "Content-Type": "application/json",
        "X-DIGIKEY-Locale-Site": "US",
        "X-DIGIKEY-Locale-Language": "en",
        "X-DIGIKEY-Locale-Currency": "USD",
        "X-DIGIKEY-Customer-Id": customer_id,
    }

def _make_request(method: str, url: str, headers: dict, data: dict = None) -> dict:
    """Make an API request with error handling and logging."""
    logger.info(f"Making {method} request to {url}")
    logger.debug(f"Headers: {json.dumps({k: v for k, v in headers.items() if 'Authorization' not in k}, indent=2)}")
    if data:
        logger.debug(f"Request body: {json.dumps(data, indent=2)}")

    method = method.upper()

    if method == "GET":
        resp = requests.get(url, headers=headers)
    elif method == "POST":
        resp = requests.post(url, headers=headers, json=data)
    elif method == "PUT":
        resp = requests.put(url, headers=headers, json=data)
    elif method == "DELETE":
        resp = requests.delete(url, headers=headers)
    else:
        raise ValueError(f"Unsupported HTTP method: {method}")

    logger.info(f"Response status: {resp.status_code}")
    if resp.status_code not in [200, 201, 204]:
        logger.error(f"API error: {resp.status_code} - {resp.text}")
        resp.raise_for_status()

    # Handle empty responses (e.g., DELETE operations)
    if resp.status_code == 204 or not resp.content:
        return {"status": "success", "message": "Operation completed successfully"}

    return resp.json()


def initialize_user_token_from_file():
    """Initialize user token from saved auth code file if it exists."""
    if oauth_state.has_user_token():
        logger.debug("User token already available")
        return True

    # Try to load auth code from file
    auth_data = load_auth_code()
    if not auth_data:
        return False

    try:
        # Exchange the saved auth code for tokens
        code = auth_data.get("auth_code")
        if code:
            logger.info("Exchanging saved authorization code for tokens...")
            token_data = exchange_code_for_token(code)
            logger.info("✓ User token initialized from saved auth code")
            return True
    except Exception as e:
        logger.warning(f"Failed to exchange saved auth code: {e}")
        logger.info("Auth code may have expired. Deleting file...")
        delete_auth_code_file()
        return False

    return False

def _require_user_auth():
    """Check if user is authenticated, raise error if not."""
    if oauth_state.has_user_token():
        return

    # Try to initialize from saved auth code
    if initialize_user_token_from_file():
        logger.info("✓ User authenticated from saved auth code")
        return

    # No saved auth code, trigger auto-launch
    logger.info("No saved authentication. Triggering OAuth flow...")
    auto_launch_oauth_if_needed()

    # Wait for user to complete auth (with timeout)
    logger.info("Waiting for user to complete browser authentication...")
    timeout = 300  # 5 minutes
    start_time = time.time()

    while not oauth_state.auth_code and (time.time() - start_time) < timeout:
        time.sleep(1)

    if not oauth_state.auth_code:
        raise ValueError(
            "OAuth authentication timed out. "
            "Please complete the browser authorization within 5 minutes."
        )

    # Exchange the auth code for tokens
    try:
        exchange_code_for_token(oauth_state.auth_code)
        logger.info("✓ User authenticated successfully")
    except Exception as e:
        raise ValueError(f"Failed to complete authentication: {e}")

# ============================================================================
# Initialize Server
# ============================================================================

logger.info("=== STARTING DIGIKEY MCP SERVER ===")
oauth_state.client_token = get_client_token()

# Try to initialize user token from saved auth code
initialize_user_token_from_file()

logger.info("=== SERVER READY ===")

# ============================================================================
# Product Search API Methods (use client credentials token)
# ============================================================================

@mcp.tool()
def keyword_search(keywords: str, limit: int = 5, manufacturer_id: str = None, category_id: str = None, search_options: str = None, sort_field: str = None, sort_order: str = "Ascending"):
    """Search DigiKey products by keyword.

    Args:
        keywords: Search terms or part numbers
        limit: Maximum number of results (default: 5)
        manufacturer_id: Filter by specific manufacturer ID
        category_id: Filter by specific category ID
        search_options: Comma-delimited filters like LeadFree,RoHSCompliant,InStock
        sort_field: Field to sort by. Options: None, Packaging, ProductStatus, DigiKeyProductNumber, ManufacturerProductNumber, Manufacturer, MinimumQuantity, QuantityAvailable, Price, Supplier, PriceManufacturerStandardPackage
        sort_order: Sort direction - Ascending or Descending (default: Ascending)
    """
    url = f"{API_BASE}/products/v4/search/keyword"
    headers = _get_headers()

    body = {
        "Keywords": keywords,
        "Limit": limit
    }

    if manufacturer_id:
        body["ManufacturerId"] = manufacturer_id
    if category_id:
        body["CategoryId"] = category_id
    if search_options:
        body["SearchOptionList"] = search_options.split(",")

    # Add sort options if specified
    if sort_field:
        body["SortOptions"] = {
            "Field": sort_field,
            "SortOrder": sort_order
        }

    return _make_request("POST", url, headers, body)

@mcp.tool()
def product_details(product_number: str, manufacturer_id: str = None, customer_id: str = "0"):
    """Get detailed information for a specific product.

    Args:
        product_number: DigiKey or manufacturer part number
        manufacturer_id: Optional manufacturer ID for disambiguation
        customer_id: Customer ID for pricing (default: "0")
    """
    url = f"{API_BASE}/products/v4/search/{product_number}/productdetails"
    headers = _get_headers(customer_id)

    params = {}
    if manufacturer_id:
        params["manufacturerId"] = manufacturer_id

    if params:
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return _make_request("GET", url, headers)

@mcp.tool()
def search_manufacturers():
    """Search and retrieve all product manufacturers."""
    url = f"{API_BASE}/products/v4/search/manufacturers"
    headers = _get_headers()
    return _make_request("GET", url, headers)

@mcp.tool()
def search_categories():
    """Search and retrieve all product categories."""
    url = f"{API_BASE}/products/v4/search/categories"
    headers = _get_headers()
    return _make_request("GET", url, headers)

@mcp.tool()
def get_category_by_id(category_id: int):
    """Get specific category details by ID.

    Args:
        category_id: The category ID to retrieve
    """
    url = f"{API_BASE}/products/v4/search/categories/{category_id}"
    headers = _get_headers()
    return _make_request("GET", url, headers)

@mcp.tool()
def search_product_substitutions(product_number: str, limit: int = 10, search_options: str = None, exclude_marketplace: bool = False):
    """Search for product substitutions for a given product.

    Args:
        product_number: The product to get substitutions for
        limit: Number of substitutions (default: 10)
        search_options: Filters like LeadFree,RoHSCompliant,InStock
        exclude_marketplace: Exclude marketplace products (default: False)
    """
    url = f"{API_BASE}/products/v4/search/{product_number}/substitutions"
    headers = _get_headers()

    params = {"limit": limit, "excludeMarketPlaceProducts": exclude_marketplace}
    if search_options:
        params["searchOptionList"] = search_options

    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    return _make_request("GET", url, headers)

@mcp.tool()
def get_product_media(product_number: str):
    """Get media (images, documents, videos) for a product.

    Args:
        product_number: The product to get media for
    """
    url = f"{API_BASE}/products/v4/search/{product_number}/media"
    headers = _get_headers()
    return _make_request("GET", url, headers)

@mcp.tool()
def get_product_pricing(product_number: str, customer_id: str = "0", requested_quantity: int = 1):
    """Get detailed pricing information for a product.

    Args:
        product_number: The product to get pricing for
        customer_id: Customer ID for pricing (default: "0")
        requested_quantity: Quantity for pricing calculation (default: 1)
    """
    url = f"{API_BASE}/products/v4/search/{product_number}/productpricing"
    headers = _get_headers(customer_id)

    params = {"requestedQuantity": requested_quantity}
    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return _make_request("GET", url, headers)

@mcp.tool()
def get_digi_reel_pricing(product_number: str, requested_quantity: int, customer_id: str = "0"):
    """Get DigiReel pricing for a product.

    Args:
        product_number: DigiKey product number (must be DigiReel compatible)
        requested_quantity: Quantity for DigiReel pricing
        customer_id: Customer ID for pricing (default: "0")
    """
    url = f"{API_BASE}/products/v4/search/{product_number}/digireelpricing"
    headers = _get_headers(customer_id)

    params = {"requestedQuantity": requested_quantity}
    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return _make_request("GET", url, headers)

# ============================================================================
# MyLists API Methods (require user authentication)
# ============================================================================

@mcp.tool()
def get_all_lists(customer_id: str = "0"):
    """Get all MyLists for the authenticated user.

    ⚠️ Requires user authentication via oauth_start_login()

    Args:
        customer_id: Customer ID (default: "0")

    Returns:
        List of all user's lists with metadata
    """
    _require_user_auth()
    url = f"{API_BASE}/mylists/v1/lists"
    headers = _get_headers(customer_id, use_user_token=True)
    return _make_request("GET", url, headers)

@mcp.tool()
def create_list(list_name: str, notes: str = None, customer_id: str = "0"):
    """Create a new MyList.

    ⚠️ Requires user authentication via oauth_start_login()

    Args:
        list_name: Name for the new list (required)
        notes: Optional notes/description for the list
        customer_id: Customer ID (default: "0")

    Returns:
        Created list information including list_id
    """
    _require_user_auth()
    url = f"{API_BASE}/mylists/v1/lists"
    headers = _get_headers(customer_id, use_user_token=True)

    body = {"listName": list_name}
    if notes:
        body["notes"] = notes

    return _make_request("POST", url, headers, body)

@mcp.tool()
def get_list_by_id(list_id: int, include_parts: bool = False, customer_id: str = "0"):
    """Get detailed information about a specific list.

    ⚠️ Requires user authentication via oauth_start_login()

    Args:
        list_id: The list ID to retrieve
        include_parts: Whether to include the parts list in response (default: False)
        customer_id: Customer ID (default: "0")

    Returns:
        Detailed list information and optionally parts data
    """
    _require_user_auth()
    url = f"{API_BASE}/mylists/v1/lists/{list_id}"
    headers = _get_headers(customer_id, use_user_token=True)

    if include_parts:
        url += "?includePartsList=true"

    return _make_request("GET", url, headers)

@mcp.tool()
def update_list_name(list_id: int, new_name: str, customer_id: str = "0"):
    """Update the name of an existing list.

    ⚠️ Requires user authentication via oauth_start_login()

    Args:
        list_id: The list ID to update
        new_name: New name for the list
        customer_id: Customer ID (default: "0")

    Returns:
        Updated list information
    """
    _require_user_auth()
    url = f"{API_BASE}/mylists/v1/lists/{list_id}"
    headers = _get_headers(customer_id, use_user_token=True)

    body = {"listName": new_name}
    return _make_request("PUT", url, headers, body)

@mcp.tool()
async def delete_list(list_id: int, customer_id: str = "0", ctx=None):
    """⚠️ DESTRUCTIVE: Permanently delete a list and all its contents.

    ⚠️ Requires user authentication via oauth_start_login()

    This operation cannot be undone. The list and all associated parts,
    settings, and metadata will be permanently removed.

    This tool will prompt for user confirmation before proceeding.

    Args:
        list_id: The list ID to delete
        customer_id: Customer ID (default: "0")

    Returns:
        Deletion confirmation response
    """
    _require_user_auth()

    # Request user confirmation
    result = await ctx.elicit(
        f"⚠️ WARNING: You are about to permanently delete list ID {list_id} and ALL its contents. "
        "This action CANNOT be undone. Do you want to proceed?",
        response_type=None
    )

    if result.action != "accept":
        raise ValueError(f"List deletion cancelled by user (action: {result.action})")

    url = f"{API_BASE}/mylists/v1/lists/{list_id}"
    headers = _get_headers(customer_id, use_user_token=True)

    return _make_request("DELETE", url, headers)

# Parts Management Methods

@mcp.tool()
def get_parts_by_list_id(list_id: int, start_index: int = None, limit: int = None, customer_id: str = "0"):
    """Get all parts from a specific list with optional pagination.

    ⚠️ Requires user authentication via oauth_start_login()

    Args:
        list_id: The list ID to get parts from
        start_index: Optional starting index for pagination
        limit: Optional number of parts to return
        customer_id: Customer ID (default: "0")

    Returns:
        List of parts with details including pricing, availability, etc.
    """
    _require_user_auth()
    url = f"{API_BASE}/mylists/v1/lists/{list_id}/parts"
    headers = _get_headers(customer_id, use_user_token=True)

    params = []
    if start_index is not None:
        params.append(f"startIndex={start_index}")
    if limit is not None:
        params.append(f"limit={limit}")

    if params:
        url += "?" + "&".join(params)

    return _make_request("GET", url, headers)

@mcp.tool()
def add_parts_to_list(list_id: int, parts: str, customer_id: str = "0"):
    """Add parts to a list.

    ⚠️ Requires user authentication via oauth_start_login()

    Args:
        list_id: The list ID to add parts to
        parts: JSON string containing parts data. Example format:
               '[{"digiKeyPartNumber": "296-8875-1-ND", "quantity": 10, "customerReference": "R1"}]'
        customer_id: Customer ID (default: "0")

    Returns:
        Response with added parts information
    """
    _require_user_auth()
    url = f"{API_BASE}/mylists/v1/lists/{list_id}/parts"
    headers = _get_headers(customer_id, use_user_token=True)

    # Parse the JSON string
    parts_data = json.loads(parts) if isinstance(parts, str) else parts

    body = {"parts": parts_data}

    return _make_request("POST", url, headers, body)

@mcp.tool()
def get_part_from_list(list_id: int, part_id: int, customer_id: str = "0"):
    """Get a specific part from a list by its part ID.

    ⚠️ Requires user authentication via oauth_start_login()

    Args:
        list_id: The list ID
        part_id: The ID of the part in the list
        customer_id: Customer ID (default: "0")

    Returns:
        Detailed part information
    """
    _require_user_auth()
    url = f"{API_BASE}/mylists/v1/lists/{list_id}/parts/{part_id}"
    headers = _get_headers(customer_id, use_user_token=True)

    return _make_request("GET", url, headers)

@mcp.tool()
def update_part_in_list(list_id: int, part_id: int, part_data: str, customer_id: str = "0"):
    """Update part information in a list.

    ⚠️ Requires user authentication via oauth_start_login()

    Args:
        list_id: The list ID
        part_id: The ID of the part to update
        part_data: JSON string with updated part data. Example:
                   '{"quantity": 20, "customerReference": "R1-Updated"}'
        customer_id: Customer ID (default: "0")

    Returns:
        Updated part information
    """
    _require_user_auth()
    url = f"{API_BASE}/mylists/v1/lists/{list_id}/parts/{part_id}"
    headers = _get_headers(customer_id, use_user_token=True)

    # Parse the JSON string
    data = json.loads(part_data) if isinstance(part_data, str) else part_data

    return _make_request("PUT", url, headers, data)

@mcp.tool()
async def delete_part_from_list(list_id: int, part_id: int, customer_id: str = "0", ctx=None):
    """⚠️ DESTRUCTIVE: Permanently delete a part from a list.

    ⚠️ Requires user authentication via oauth_start_login()

    This operation cannot be undone. The part will be permanently removed from the list.

    This tool will prompt for user confirmation before proceeding.

    Args:
        list_id: The list ID
        part_id: The ID of the part to delete
        customer_id: Customer ID (default: "0")

    Returns:
        Deletion confirmation response
    """
    _require_user_auth()

    # Request user confirmation
    result = await ctx.elicit(
        f"⚠️ WARNING: You are about to permanently delete part ID {part_id} from list ID {list_id}. "
        "This action CANNOT be undone. Do you want to proceed?",
        response_type=None
    )

    if result.action != "accept":
        raise ValueError(f"Part deletion cancelled by user (action: {result.action})")

    url = f"{API_BASE}/mylists/v1/lists/{list_id}/parts/{part_id}"
    headers = _get_headers(customer_id, use_user_token=True)

    return _make_request("DELETE", url, headers)


def main():
    mcp.run()

if __name__ == "__main__":
    main()
