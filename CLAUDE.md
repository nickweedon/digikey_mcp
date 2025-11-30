# DigiKey MCP Server - Claude Context

This is an MCP (Model Context Protocol) server for interfacing with the DigiKey API. It enables AI assistants to search for electronic components, manage MyLists, and access product information through DigiKey's product database.

## Project Structure

Follow standard Python project conventions with a modular architecture. Tools should be organized into separate modules by domain.

```
digikey_mcp/
├── src/
│   ├── __init__.py           # Package initialization
│   ├── config.py             # Configuration and logging
│   ├── api/
│   │   ├── __init__.py       # API module initialization
│   │   ├── auth.py           # Authentication helpers
│   │   └── client.py         # HTTP client for DigiKey API
│   ├── oauth/
│   │   ├── __init__.py       # OAuth module initialization
│   │   ├── flow.py           # OAuth flow implementation
│   │   ├── server.py         # Local HTTPS server for OAuth callback
│   │   ├── state.py          # OAuth state management
│   │   └── storage.py        # Token persistence
│   └── tools/
│       ├── __init__.py       # Tools module initialization
│       ├── oauth_tools.py    # OAuth-related MCP tools
│       ├── product_tools.py  # Product search MCP tools
│       └── mylists_tools.py  # MyLists management MCP tools
├── tests/
│   └── test_*.py             # Test files
├── digikey_mcp_server.py     # Main MCP server entry point
├── pyproject.toml            # Project configuration and dependencies
├── .env                      # Environment variables (credentials)
├── localhost-cert.pem        # SSL certificate for OAuth callback
├── localhost-key.pem         # SSL private key for OAuth callback
├── Dockerfile                # Container image definition
├── docker-compose.yml        # Production container configuration
├── docker-compose.devcontainer.yml  # Development container configuration
├── .devcontainer/
│   └── devcontainer.json     # VS Code devcontainer settings
├── README.md                 # User documentation
└── CLAUDE.md                 # This file - context for Claude
```

## Code Organization Guidelines

1. **Modular Tools**: Each tool domain (OAuth, Products, MyLists) MUST be implemented in its own Python module under `src/tools/`.

2. **Separation of Concerns**:
   - `src/api/client.py` - HTTP client and base request handling
   - `src/api/auth.py` - Authentication helpers and token management
   - `src/oauth/` - Complete OAuth 2.0 flow implementation
   - `src/tools/*.py` - Domain-specific MCP tools
   - `src/config.py` - Configuration and logging setup
   - `digikey_mcp_server.py` - MCP server setup and tool registration

3. **Standard Python Conventions**:
   - Use `src/` layout for proper package isolation
   - Include `__init__.py` files in all packages
   - Follow PEP 8 naming conventions
   - Use type hints throughout
   - Keep modules focused and cohesive

4. **Import Structure**: Each tools module should import shared clients and expose registration functions. The main server imports and registers tools from each module.

## Design Documentation

The design always aims to:
- Provide JMESPath filtering and projection when the tool method can return large or complex data types
- Never change the structure or field names in the default JMESPath query as this can confuse the LLM
- Provide Strongly-typed return values
- Always provide a JMESPath example in the docstring when the tool accepts JMESPath queries
- Error handling patterns
- Implementation examples with code


## OAuth Implementation

DigiKey requires OAuth 2.0 authentication for user-specific operations (MyLists). The implementation includes:
- Local HTTPS callback server on port 8139
- Self-signed SSL certificates for localhost
- Token persistence for session continuity

See [OAUTH_GUIDE.md](OAUTH_GUIDE.md) for detailed OAuth setup instructions.

## API Reference

**API Documentation:** https://developer.digikey.com/

### Authentication
- **Client Credentials**: For product search (public data)
- **OAuth 2.0**: For MyLists and user-specific operations

### Key API Endpoints
- Product Search: `/products/v4/search/keyword`
- Product Details: `/products/v4/search/{digiKeyPartNumber}/productdetails`
- MyLists: `/mylists/v1/lists`

## Development Notes

- Uses FastMCP framework for MCP server implementation
- Uses `requests` library for HTTP calls
- Uses `jmespath` for response filtering
- Environment variables loaded via `python-dotenv`
- Requires Python 3.10+

## Git Commit Guidelines

- Do NOT include "Generated with Claude Code" or similar AI attribution in commit messages.
- Do NOT include "Co-Authored-By: Claude" or similar co-author tags.
- Always do a 'git commit -a' and include all modified files.
- Always include descriptive commit comments that succinctly describe the changes made in the summary and a separate line with a asterisk bullet point that describes each feature or notable change in more detail. 
- Write commit messages as if authored solely by the developer.

## Running the Server

```bash
uv sync
uv run python digikey_mcp_server.py
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `CLIENT_ID` | DigiKey API Client ID |
| `CLIENT_SECRET` | DigiKey API Client Secret |
| `USE_SANDBOX` | Set to `true` for sandbox environment, `false` for production |

## Docker

Build and run with Docker:
```bash
docker-compose build
docker-compose up -d
```

The container exposes port 8139 for OAuth callbacks and mounts:
- `.env` - Environment variables
- `localhost-cert.pem` - SSL certificate (read-only)
- `localhost-key.pem` - SSL private key (read-only)

## Testing

Test the server with:
```bash
uv run python -c "from digikey_mcp_server import mcp; print('Server loads OK')"
```

Run specific tests:
```bash
uv run python test_keyword_search.py
uv run python test_mylists.py
```
