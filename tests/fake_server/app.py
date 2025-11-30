"""Fake DigiKey API server for testing.

Flask application that mimics DigiKey API endpoints for unit testing.
Runs on a random free port to avoid conflicts.
"""

import socket
import threading
from contextlib import contextmanager
from typing import Generator

from flask import Flask

from .oauth_endpoints import oauth_bp
from .mylists_endpoints import mylists_bp, reset_state as reset_mylists_state
from .product_endpoints import products_bp


def create_app() -> Flask:
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Disable strict slashes to match DigiKey API behavior
    app.url_map.strict_slashes = False

    # Register blueprints
    app.register_blueprint(oauth_bp)
    app.register_blueprint(mylists_bp)
    app.register_blueprint(products_bp)

    return app


def reset_state():
    """Reset all fake server state."""
    reset_mylists_state()


def find_free_port() -> int:
    """Find a free port on localhost."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        s.listen(1)
        port = s.getsockname()[1]
    return port


class FakeServer:
    """Manages the fake DigiKey API server lifecycle."""

    def __init__(self):
        self.app = create_app()
        self.port = find_free_port()
        self.base_url = f"http://127.0.0.1:{self.port}"
        self._server_thread: threading.Thread | None = None
        self._shutdown_event = threading.Event()

    def start(self):
        """Start the server in a background thread."""
        from werkzeug.serving import make_server

        self._server = make_server(
            "127.0.0.1",
            self.port,
            self.app,
            threaded=True
        )

        def run():
            self._server.serve_forever()

        self._server_thread = threading.Thread(target=run, daemon=True)
        self._server_thread.start()

    def stop(self):
        """Stop the server."""
        if hasattr(self, "_server"):
            self._server.shutdown()
        if self._server_thread:
            self._server_thread.join(timeout=5)

    def reset(self):
        """Reset the server state."""
        reset_state()


@contextmanager
def fake_server_context() -> Generator[FakeServer, None, None]:
    """Context manager for running the fake server."""
    server = FakeServer()
    server.start()
    try:
        yield server
    finally:
        server.stop()
