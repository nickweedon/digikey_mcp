"""OAuth Flow Functions"""
import secrets
import urllib.parse
import logging
import requests
import webbrowser
from src.config import (
    CLIENT_ID, CLIENT_SECRET, TOKEN_URL, AUTHORIZE_URL,
    REDIRECT_URI
)
from src.oauth.state import oauth_state
from src.oauth.server import start_oauth_server
from src.oauth.storage import save_tokens

logger = logging.getLogger(__name__)


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

    from src.config import USE_SANDBOX
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

    # Save tokens to file for persistence across restarts
    if oauth_state.refresh_token:
        save_tokens(oauth_state.user_token, oauth_state.refresh_token)

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

    # Save updated tokens to file
    if oauth_state.refresh_token:
        save_tokens(oauth_state.user_token, oauth_state.refresh_token)

    logger.info("✓ Successfully refreshed user access token")
    return token_data


