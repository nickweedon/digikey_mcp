"""Pytest configuration and fixtures for DigiKey MCP Server tests.

This module provides shared fixtures for testing with a fake DigiKey API server.
"""

import pytest
from unittest.mock import patch

from tests.fake_server.app import FakeServer
from tests.fake_server.oauth_endpoints import VALID_ACCESS_TOKEN, VALID_REFRESH_TOKEN


@pytest.fixture(scope="session")
def fake_server():
    """Start the fake DigiKey API server for the test session.

    This fixture starts a Flask server on a random free port that mimics
    DigiKey API endpoints. The server runs for the entire test session.

    Yields:
        FakeServer: The running server instance with .base_url attribute
    """
    server = FakeServer()
    server.start()
    yield server
    server.stop()


@pytest.fixture
def patched_api_base(fake_server):
    """Patch src.config.API_BASE to point to the fake server.

    This fixture redirects all API calls to the fake server instead of
    the real DigiKey API.

    Args:
        fake_server: The running fake server fixture

    Yields:
        str: The fake server base URL
    """
    with patch("src.config.API_BASE", fake_server.base_url):
        # Also patch in the tools modules where it's imported
        with patch("src.tools.mylists_tools.API_BASE", fake_server.base_url):
            with patch("src.tools.product_tools.API_BASE", fake_server.base_url):
                yield fake_server.base_url


@pytest.fixture
def authenticated_state(fake_server):
    """Set up authenticated OAuth state with valid tokens.

    This fixture injects valid test tokens into the global oauth_state,
    simulating a successfully authenticated user session.

    Args:
        fake_server: The running fake server fixture

    Yields:
        The oauth_state instance with tokens set
    """
    from src.oauth.state import oauth_state

    # Save original state
    original_user_token = oauth_state.user_token
    original_refresh_token = oauth_state.refresh_token

    # Set valid tokens
    oauth_state.user_token = VALID_ACCESS_TOKEN
    oauth_state.refresh_token = VALID_REFRESH_TOKEN

    yield oauth_state

    # Restore original state
    oauth_state.user_token = original_user_token
    oauth_state.refresh_token = original_refresh_token


@pytest.fixture
def reset_oauth_state(fake_server):
    """Reset OAuth state to unauthenticated.

    This fixture clears all tokens from oauth_state, simulating a
    user who has not authenticated yet.

    Args:
        fake_server: The running fake server fixture

    Yields:
        The oauth_state instance with tokens cleared
    """
    from src.oauth.state import oauth_state

    # Save original state
    original_user_token = oauth_state.user_token
    original_refresh_token = oauth_state.refresh_token
    original_client_token = oauth_state.client_token

    # Clear all tokens
    oauth_state.user_token = None
    oauth_state.refresh_token = None
    oauth_state.client_token = None

    yield oauth_state

    # Restore original state
    oauth_state.user_token = original_user_token
    oauth_state.refresh_token = original_refresh_token
    oauth_state.client_token = original_client_token


@pytest.fixture
def reset_fake_server(fake_server):
    """Reset the fake server state between tests.

    This fixture clears any data created during tests (e.g., lists, parts)
    to ensure test isolation.

    Args:
        fake_server: The running fake server fixture
    """
    fake_server.reset()
    yield
    fake_server.reset()


@pytest.fixture
def client_authenticated_state():
    """Set up authenticated OAuth state with a client credentials token.

    This fixture injects a valid client token into the global oauth_state,
    simulating a client credentials authentication for product search APIs.

    Yields:
        The oauth_state instance with client token set
    """
    from src.oauth.state import oauth_state

    # Save original state
    original_client_token = oauth_state.client_token

    # Set valid client token
    oauth_state.client_token = "client_credentials_token"

    yield oauth_state

    # Restore original state
    oauth_state.client_token = original_client_token
