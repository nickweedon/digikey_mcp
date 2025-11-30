"""OAuth Token File Storage

Handles persistence of OAuth tokens (user_token, refresh_token) to disk
for session continuity across server restarts.
"""
import json
import time
import logging
from src.config import TOKEN_FILE

logger = logging.getLogger(__name__)


def save_tokens(user_token: str, refresh_token: str):
    """Save OAuth tokens to file for persistence across restarts."""
    try:
        data = {
            "user_token": user_token,
            "refresh_token": refresh_token,
            "timestamp": time.time()
        }
        with open(TOKEN_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"✓ OAuth tokens saved to {TOKEN_FILE}")
    except Exception as e:
        logger.error(f"Failed to save tokens: {e}")


def load_tokens():
    """Load OAuth tokens from file.

    Returns:
        dict with 'user_token' and 'refresh_token' keys, or None if not found.
    """
    try:
        if not TOKEN_FILE.exists():
            logger.debug(f"Token file not found: {TOKEN_FILE}")
            return None

        with open(TOKEN_FILE, 'r') as f:
            data = json.load(f)

        if "user_token" in data and "refresh_token" in data:
            logger.info(f"✓ OAuth tokens loaded from {TOKEN_FILE}")
            return data

        logger.debug("Token file exists but missing required fields")
        return None
    except Exception as e:
        logger.error(f"Failed to load tokens: {e}")
        return None


def delete_token_file():
    """Delete the token file."""
    try:
        if TOKEN_FILE.exists():
            TOKEN_FILE.unlink()
            logger.info(f"✓ Deleted token file: {TOKEN_FILE}")
    except Exception as e:
        logger.error(f"Failed to delete token file: {e}")
