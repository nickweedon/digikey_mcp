"""Auth Code File Storage"""
import json
import time
import logging
from src.config import AUTH_CODE_FILE

logger = logging.getLogger(__name__)


def save_auth_code(code: str, state: str):
    """Save authorization code to file."""
    try:
        data = {
            "auth_code": code,
            "state": state,
            "timestamp": time.time()
        }
        with open(AUTH_CODE_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"✓ Authorization code saved to {AUTH_CODE_FILE}")
    except Exception as e:
        logger.error(f"Failed to save auth code: {e}")


def load_auth_code():
    """Load authorization code from file."""
    try:
        if not AUTH_CODE_FILE.exists():
            logger.debug(f"Auth code file not found: {AUTH_CODE_FILE}")
            return None

        with open(AUTH_CODE_FILE, 'r') as f:
            data = json.load(f)

        logger.info(f"✓ Authorization code loaded from {AUTH_CODE_FILE}")
        return data
    except Exception as e:
        logger.error(f"Failed to load auth code: {e}")
        return None


def delete_auth_code_file():
    """Delete the authorization code file."""
    try:
        if AUTH_CODE_FILE.exists():
            AUTH_CODE_FILE.unlink()
            logger.info(f"✓ Deleted auth code file: {AUTH_CODE_FILE}")
    except Exception as e:
        logger.error(f"Failed to delete auth code file: {e}")
