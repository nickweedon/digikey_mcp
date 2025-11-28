"""API Request Helpers"""
import json
import logging
import requests
from src.config import CLIENT_ID
from src.oauth.state import oauth_state
from src.oauth.flow import get_client_token, refresh_user_token

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


def _make_request(method: str, url: str, headers: dict, data: dict = None, use_user_token: bool = False) -> dict:
    """Make an API request with error handling and logging.

    Args:
        method: HTTP method (GET, POST, PUT, DELETE)
        url: URL to request
        headers: Request headers
        data: Optional request body data
        use_user_token: If True, using user token (will refresh user token on 401)
    """
    logger.info(f"Making {method} request to {url}")
    logger.debug(f"Headers: {json.dumps({k: v for k, v in headers.items() if 'Authorization' not in k}, indent=2)}")
    if data:
        logger.debug(f"Request body: {json.dumps(data, indent=2)}")

    method = method.upper()

    def _execute_request():
        """Execute the HTTP request."""
        if method == "GET":
            return requests.get(url, headers=headers)
        elif method == "POST":
            return requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            return requests.put(url, headers=headers, json=data)
        elif method == "DELETE":
            return requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")

    # First attempt
    resp = _execute_request()
    logger.info(f"Response status: {resp.status_code}")

    # Check for token expiry error (401)
    if resp.status_code == 401:
        try:
            error_data = resp.json()
            # Check if this is a token expiry error
            if "Bearer token is expired" in error_data.get("detail", ""):
                logger.warning("Token expired, attempting to refresh...")

                # Refresh the appropriate token
                if use_user_token:
                    refresh_user_token()
                    # Update headers with new user token
                    headers["Authorization"] = f"Bearer {oauth_state.user_token}"
                else:
                    oauth_state.client_token = get_client_token()
                    # Update headers with new client token
                    headers["Authorization"] = f"Bearer {oauth_state.client_token}"

                logger.info("Token refreshed, retrying request...")
                # Retry the request with the new token
                resp = _execute_request()
                logger.info(f"Retry response status: {resp.status_code}")
        except (ValueError, KeyError, json.JSONDecodeError):
            # Not a JSON response or missing expected fields, proceed with normal error handling
            pass

    # Handle errors
    if resp.status_code not in [200, 201, 204]:
        logger.error(f"API error: {resp.status_code} - {resp.text}")
        resp.raise_for_status()

    # Handle empty responses (e.g., DELETE operations)
    if resp.status_code == 204 or not resp.content:
        return {"status": "success", "message": "Operation completed successfully"}

    return resp.json()
