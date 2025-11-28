"""OAuth State Management"""

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


# Global OAuth state instance
oauth_state = OAuthState()
