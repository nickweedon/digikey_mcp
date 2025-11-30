"""OAuth MCP Tools"""
import time
import logging
from src.config import REDIRECT_URI
from src.oauth.state import oauth_state
from src.oauth.server import start_oauth_server
from src.oauth.flow import generate_authorization_url, exchange_code_for_token, refresh_user_token
from src.oauth.storage import delete_token_file

logger = logging.getLogger(__name__)


def register_oauth_tools(mcp):
    """Register OAuth-related MCP tools."""

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
        start_oauth_server()
        auth_url = generate_authorization_url()

        return {
            "status": "ready",
            "authorization_url": auth_url,
            "instructions": [
                "1. Open the authorization_url in your web browser",
                "2. Log in to your DigiKey account",
                "3. Authorize the application to access your MyLists",
                "4. You will be redirected to a success page",
                "5. Let me know once you have done this and I will call oauth_complete_login() to finalize the authentication"
            ]
        }

    @mcp.tool()
    def oauth_complete_login():
        """Complete the OAuth login process by exchanging the authorization code for tokens.

        This should be called after the user has visited the authorization URL and completed login.
        The authorization code received from the callback will be exchanged for access tokens.

        Returns:
            dict: Status of the login completion
        """

        if not oauth_state.auth_code:
            return {
                "status": "Missing auth code",
                "error": "No authorization code received",
                "suggestion": "Please call oauth_start_login() again and complete the browser authorization"
            }

        try:
            # This will update the oauth_state with user_token and refresh_token
            token_data = exchange_code_for_token(oauth_state.auth_code)

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
            "auth_code_available": oauth_state.auth_code is not None,
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

        delete_token_file()

        return {
            "status": "success",
            "message": "Logged out successfully. All tokens cleared."
        }
