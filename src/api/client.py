"""API Request Helpers"""
import json
import logging
import requests
from src.config import CLIENT_ID
from src.oauth.state import oauth_state

logger = logging.getLogger(__name__)


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
