"""API Authentication Helpers"""
import logging
from src.oauth.state import oauth_state
from src.oauth.storage import load_auth_code, delete_auth_code_file
from src.oauth.flow import exchange_code_for_token

logger = logging.getLogger(__name__)


def initialize_user_token_from_file():
    """Initialize user token from saved auth code file if it exists."""
    if oauth_state.has_user_token():
        logger.debug("User token already available")
        return True

    auth_data = load_auth_code()
    if not auth_data:
        return False

    try:
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

    if initialize_user_token_from_file():
        logger.info("✓ User authenticated from saved auth code")
        return

    logger.info("No saved authentication. Authenticate at http://localhost:8139")
    raise ValueError(
        "No Authentication code, Authenticate at http://localhost:8139."
    )
