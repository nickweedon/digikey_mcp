"""OAuth Callback HTTP Server"""
import ssl
import logging
import threading
import urllib.parse
from http.server import HTTPServer, BaseHTTPRequestHandler
from src.config import OAUTH_PORT, SSL_CERT_FILE, SSL_KEY_FILE
from src.oauth.state import oauth_state

logger = logging.getLogger(__name__)


class OAuthCallbackHandler(BaseHTTPRequestHandler):
    """HTTP request handler for OAuth callback."""

    def do_GET(self):
        """Handle GET requests to the callback endpoint."""
        parsed = urllib.parse.urlparse(self.path)

        if parsed.path == '/callback':
            params = urllib.parse.parse_qs(parsed.query)

            if 'code' in params:
                code = params['code'][0]
                state = params.get('state', [None])[0]

                if state == oauth_state.auth_state:
                    oauth_state.auth_code = code

                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    html_response = """
                    <html>
                    <head><title>Authorization Successful</title></head>
                    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; text-align: center;">
                        <h1 style="color: #28a745;">&#10003; Authorization Successful!</h1>
                        <p>You have successfully authorized the DigiKey MCP Server.</p>
                        <p>You can now close this window and return to your application.</p>
                        <p style="margin-top: 30px; color: #666;">The server will now exchange the authorization code for an access token.</p>
                    </body>
                    </html>
                    """
                    self.wfile.write(html_response.encode('utf-8'))
                    logger.info("✓ Authorization code received successfully")
                else:
                    self.send_response(400)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    html_response = """
                    <html>
                    <head><title>Authorization Failed</title></head>
                    <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; text-align: center;">
                        <h1 style="color: #dc3545;">&#10007; Authorization Failed</h1>
                        <p>State parameter mismatch. Possible CSRF attack detected.</p>
                        <p>Please try again.</p>
                    </body>
                    </html>
                    """
                    self.wfile.write(html_response.encode('utf-8'))
                    logger.error("State parameter mismatch in OAuth callback")

            elif 'error' in params:
                error = params['error'][0]
                error_desc = params.get('error_description', ['Unknown error'])[0]

                self.send_response(400)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                html_response = f"""
                <html>
                <head><title>Authorization Denied</title></head>
                <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; text-align: center;">
                    <h1 style="color: #dc3545;">&#10007; Authorization Denied</h1>
                    <p><strong>Error:</strong> {error}</p>
                    <p><strong>Description:</strong> {error_desc}</p>
                </body>
                </html>
                """
                self.wfile.write(html_response.encode('utf-8'))
                logger.warning(f"User denied authorization: {error} - {error_desc}")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        """Override to use our logger instead of printing to stderr."""
        logger.debug(f"OAuth callback server: {format % args}")


def start_oauth_server():
    """Start the OAuth callback HTTPS server in a background thread."""
    if oauth_state.server_thread and oauth_state.server_thread.is_alive():
        logger.info("OAuth callback server already running")
        return

    def run_server():
        try:
            oauth_state.http_server = HTTPServer(('0.0.0.0', OAUTH_PORT), OAuthCallbackHandler)

            if not SSL_CERT_FILE.exists() or not SSL_KEY_FILE.exists():
                logger.error(f"SSL certificate files not found: {SSL_CERT_FILE}, {SSL_KEY_FILE}")
                logger.error("Please generate SSL certificates using:")
                logger.error('openssl req -x509 -newkey rsa:4096 -nodes -keyout localhost-key.pem -out localhost-cert.pem -days 365 -subj "/CN=localhost"')
                raise FileNotFoundError("SSL certificate files not found")

            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            ssl_context.load_cert_chain(certfile=str(SSL_CERT_FILE), keyfile=str(SSL_KEY_FILE))
            oauth_state.http_server.socket = ssl_context.wrap_socket(
                oauth_state.http_server.socket,
                server_side=True
            )

            logger.info(f"✓ OAuth callback server started on https://localhost:{OAUTH_PORT}")
            logger.info("⚠️  Using self-signed certificate - browser will show security warning (this is normal)")
            oauth_state.http_server.serve_forever()
        except Exception as e:
            logger.error(f"OAuth callback server error: {e}")

    oauth_state.server_thread = threading.Thread(target=run_server, daemon=True)
    oauth_state.server_thread.start()


def stop_oauth_server():
    """Stop the OAuth callback HTTPS server."""
    if oauth_state.http_server:
        oauth_state.http_server.shutdown()
        logger.info("OAuth callback server stopped")
