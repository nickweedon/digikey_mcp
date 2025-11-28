"""DigiKey MCP Server - Main Entry Point"""
from fastmcp import FastMCP
from src.config import logger
from src.oauth.state import oauth_state
from src.oauth.flow import get_client_token, auto_launch_oauth_if_needed
from src.api.auth import initialize_user_token_from_file
from src.tools.oauth_tools import register_oauth_tools
from src.tools.product_tools import register_product_tools
from src.tools.mylists_tools import register_mylists_tools

# Initialize FastMCP server
mcp = FastMCP("DigiKey MCP Server")

# Register all tool groups
register_oauth_tools(mcp)
register_product_tools(mcp)
register_mylists_tools(mcp)

# Initialize server
logger.info("=== STARTING DIGIKEY MCP SERVER ===")
oauth_state.client_token = get_client_token()

# Try to initialize user token from saved auth code
initialize_user_token_from_file()

logger.info("=== SERVER READY ===")


def main():
    """Main entry point for the MCP server."""
    #auto_launch_oauth_if_needed()
    mcp.run()


if __name__ == "__main__":
    main()
