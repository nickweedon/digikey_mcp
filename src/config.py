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

# Log environment (use logger.info instead of print to avoid breaking MCP JSON-RPC)
logger.info(f"Using {'SANDBOX' if USE_SANDBOX else 'PRODUCTION'} environment")
