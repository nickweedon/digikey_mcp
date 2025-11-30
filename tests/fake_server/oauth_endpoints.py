"""OAuth endpoints for fake DigiKey API server.

Simulates DigiKey's OAuth 2.0 token and authorization endpoints.
"""

import secrets
from flask import Blueprint, request, jsonify, redirect

oauth_bp = Blueprint("oauth", __name__)

# Valid test tokens
VALID_ACCESS_TOKEN = "test_access_token_12345"
VALID_REFRESH_TOKEN = "test_refresh_token_67890"
EXPIRED_TOKEN = "expired_token"

# Store authorization codes (simulated)
_auth_codes: dict[str, str] = {}


@oauth_bp.route("/v1/oauth2/token", methods=["POST"])
def token_endpoint():
    """Handle OAuth token requests.

    Supports:
    - client_credentials grant
    - authorization_code grant
    - refresh_token grant
    """
    grant_type = request.form.get("grant_type")

    if grant_type == "client_credentials":
        # Return a client credentials token (for product search)
        return jsonify({
            "access_token": "client_credentials_token",
            "token_type": "Bearer",
            "expires_in": 86400
        })

    elif grant_type == "authorization_code":
        code = request.form.get("code")
        if not code or code not in _auth_codes:
            return jsonify({
                "error": "invalid_grant",
                "error_description": "Invalid authorization code"
            }), 400

        # Clear the code (single use)
        del _auth_codes[code]

        return jsonify({
            "access_token": VALID_ACCESS_TOKEN,
            "refresh_token": VALID_REFRESH_TOKEN,
            "token_type": "Bearer",
            "expires_in": 86400
        })

    elif grant_type == "refresh_token":
        refresh_token = request.form.get("refresh_token")
        if refresh_token != VALID_REFRESH_TOKEN:
            return jsonify({
                "error": "invalid_grant",
                "error_description": "Invalid refresh token"
            }), 400

        return jsonify({
            "access_token": VALID_ACCESS_TOKEN,
            "refresh_token": VALID_REFRESH_TOKEN,
            "token_type": "Bearer",
            "expires_in": 86400
        })

    return jsonify({
        "error": "unsupported_grant_type",
        "error_description": f"Grant type '{grant_type}' is not supported"
    }), 400


@oauth_bp.route("/v1/oauth2/authorize", methods=["GET"])
def authorize_endpoint():
    """Handle OAuth authorization requests.

    Simulates DigiKey login by auto-redirecting with a code.
    In real flow, user would log in and authorize.
    """
    redirect_uri = request.args.get("redirect_uri")
    state = request.args.get("state", "")

    if not redirect_uri:
        return jsonify({
            "error": "invalid_request",
            "error_description": "redirect_uri is required"
        }), 400

    # Generate an authorization code
    code = secrets.token_urlsafe(32)
    _auth_codes[code] = state

    # Auto-redirect with the code (simulates successful login)
    separator = "&" if "?" in redirect_uri else "?"
    redirect_url = f"{redirect_uri}{separator}code={code}"
    if state:
        redirect_url += f"&state={state}"

    return redirect(redirect_url)


def is_valid_token(token: str | None) -> bool:
    """Check if a token is valid."""
    if not token:
        return False
    # Handle "Bearer <token>" format
    if token.startswith("Bearer "):
        token = token[7:]
    return token == VALID_ACCESS_TOKEN


def is_expired_token(token: str | None) -> bool:
    """Check if a token is the special expired token."""
    if not token:
        return False
    if token.startswith("Bearer "):
        token = token[7:]
    return token == EXPIRED_TOKEN
