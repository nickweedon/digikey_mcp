"""DigiKey MCP Server Configuration"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Client credentials
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")

# Environment configuration
USE_SANDBOX = os.getenv("USE_SANDBOX", "true").lower() == "true"

# OAuth configuration
REDIRECT_URI = os.getenv("REDIRECT_URI", "https://localhost:8139/callback")
OAUTH_PORT = int(os.getenv("OAUTH_PORT", "8139"))
SSL_CERT_FILE = Path(os.getenv("SSL_CERT_FILE", "localhost-cert.pem"))
SSL_KEY_FILE = Path(os.getenv("SSL_KEY_FILE", "localhost-key.pem"))


def get_redirect_uri() -> str:
    """Get the OAuth redirect URI with discovered or configured port.

    Returns:
        str: The redirect URI to use for OAuth callbacks. If REDIRECT_URI is
             explicitly set in environment, uses that. Otherwise discovers the
             host port via Docker API if running in a container, or falls back
             to the configured OAUTH_PORT.
    """
    from src.oauth.port_discovery import port_discovery

    # If user explicitly set REDIRECT_URI, use that (user override)
    if os.getenv("REDIRECT_URI"):
        return REDIRECT_URI

    # Otherwise use discovered port
    discovered_port = port_discovery.get_callback_port()
    return f"https://localhost:{discovered_port}/callback"

# Token file storage
TOKEN_FILE = Path(os.getenv("TOKEN_FILE", ".digikey_tokens"))

# DigiKey OAuth2 endpoints
if USE_SANDBOX:
    TOKEN_URL = "https://sandbox-api.digikey.com/v1/oauth2/token"
    AUTHORIZE_URL = "https://sandbox-api.digikey.com/v1/oauth2/authorize"
    API_BASE = "https://sandbox-api.digikey.com"
else:
    TOKEN_URL = "https://api.digikey.com/v1/oauth2/token"
    AUTHORIZE_URL = "https://api.digikey.com/v1/oauth2/authorize"
    API_BASE = "https://api.digikey.com"

# Log environment (use logger.info instead of print to avoid breaking MCP JSON-RPC)
logger.info(f"Using {'SANDBOX' if USE_SANDBOX else 'PRODUCTION'} environment")
