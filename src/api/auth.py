"""API Authentication Helpers"""
import logging
from src.oauth.state import oauth_state
from src.oauth.storage import load_tokens, delete_token_file

logger = logging.getLogger(__name__)


def initialize_user_token_from_file():
    """Initialize user token from saved token file if it exists.

    Loads saved tokens and attempts to refresh if the access token is expired.
    """
    if oauth_state.has_user_token():
        logger.debug("User token already available")
        return True

    token_data = load_tokens()
    if not token_data:
        return False

    try:
        # Load tokens into oauth_state
        oauth_state.user_token = token_data.get("user_token")
        oauth_state.refresh_token = token_data.get("refresh_token")

        if oauth_state.user_token and oauth_state.refresh_token:
            logger.info("✓ User tokens loaded from file")
            return True

    except Exception as e:
        logger.warning(f"Failed to load saved tokens: {e}")
        logger.info("Deleting invalid token file...")
        delete_token_file()
        return False

    return False


def _require_user_auth():
    """Check if user is authenticated, raise error if not."""
    if oauth_state.has_user_token():
        return

    if initialize_user_token_from_file():
        logger.info("✓ User authenticated from saved tokens")
        return

    logger.info("No saved authentication. Authenticate at http://localhost:8139")
    raise ValueError(
        "No Authentication code, Authenticate at http://localhost:8139."
    )
