# DigiKey MCP Server

A Model Context Protocol (MCP) server for DigiKey's Product Search API using FastMCP.

## Documentation

- **[Code Breakdown](CODE_BREAKDOWN.md)** - Detailed technical documentation with architecture diagrams, code explanations, and integration guides

## Requirements

- Python 3.10+
- uv package manager
- DigiKey API credentials (CLIENT_ID and CLIENT_SECRET)

## Setup

### 1. Install dependencies
```bash
uv sync
```

### 2. Set up environment variables
Create a `.env` file in the project root:
```
CLIENT_ID=your_digikey_client_id
CLIENT_SECRET=your_digikey_client_secret
USE_SANDBOX=false
```

Set `USE_SANDBOX=true` to use DigiKey's sandbox environment for testing.

### 3. Generate SSL certificates for OAuth (HTTPS callback)
For MyLists API access, you need to generate SSL certificates for the HTTPS callback endpoint:
```bash
openssl req -x509 -newkey rsa:4096 -nodes -keyout localhost-key.pem -out localhost-cert.pem -days 365 -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
```

**Note:** When completing OAuth authorization, your browser will show a security warning about the self-signed certificate. This is normal - click "Advanced" and "Proceed to localhost" to continue.

### 4. Run the server
```bash
uv run python digikey_mcp_server.py
```

## Available Tools

### Search Methods
- `keyword_search(keywords, limit=5, manufacturer_id=None, category_id=None, search_options=None, sort_field=None, sort_order="Ascending")` - Search DigiKey products by keyword with sorting and filtering
- `search_manufacturers()` - Get all product manufacturers
- `search_categories()` - Get all product categories
- `search_product_substitutions(product_number, limit=10, search_options=None, exclude_marketplace=False)` - Find substitute products

### Product Details
- `product_details(product_number, manufacturer_id=None, customer_id="0")` - Get detailed product information
- `get_category_by_id(category_id)` - Get specific category details
- `get_product_media(product_number)` - Get product images, documents, and videos
- `get_product_pricing(product_number, customer_id="0", requested_quantity=1)` - Get detailed pricing information
- `get_digi_reel_pricing(product_number, requested_quantity, customer_id="0")` - Get DigiReel pricing

### MyLists - List Management
- `get_all_lists(customer_id="0")` - Get all MyLists for the user
- `create_list(list_name, notes=None, customer_id="0")` - Create a new MyList
- `get_list_by_id(list_id, include_parts=False, customer_id="0")` - Get detailed list information
- `update_list_name(list_id, new_name, customer_id="0")` - Update a list's name
- `is_valid_list_name(list_name, customer_id="0")` - Check if list name is available
- `get_valid_list_name(list_name, customer_id="0")` - Get a valid list name (adds number suffix if needed)
- `delete_list(list_id, customer_id="0")` - ⚠️ DESTRUCTIVE: Permanently delete a list (prompts for confirmation)

### MyLists - Parts Management
- `get_parts_by_list_id(list_id, start_index=None, count=None, customer_id="0")` - Get all parts from a list with pagination
- `add_parts_to_list(list_id, parts, customer_id="0")` - Add parts to a list
- `get_part_from_list(list_id, unique_id, customer_id="0")` - Get specific part from a list
- `update_part_in_list(list_id, unique_id, part_data, customer_id="0")` - Update part information in a list
- `delete_part_from_list(list_id, unique_id, customer_id="0")` - ⚠️ DESTRUCTIVE: Delete a part from a list (prompts for confirmation)

### MyLists - Tags & Organization
- `create_tag(tag_name, customer_id="0")` - Create a new tag for organizing lists
- `delete_tag(tag_id, customer_id="0")` - ⚠️ DESTRUCTIVE: Delete a tag (prompts for confirmation)

### MyLists - Revisions
- `create_revision(list_id, revision_name, customer_id="0")` - Create a new list revision
- `get_revision_by_id(revision_id, customer_id="0")` - Get details of a specific revision
- `delete_revision(revision_id, customer_id="0")` - ⚠️ DESTRUCTIVE: Delete a revision (prompts for confirmation)

### MyLists - Additional Features
- `get_price_table(list_id, customer_id="0")` - Get aggregate pricing for all parts in a list
- `get_alternate_part_info(part_number, customer_id="0")` - Get alternate/substitute part information
- `update_list_settings(list_id, settings, customer_id="0")` - Update list settings (visibility, package preferences)

### Sort Options for keyword_search
Available sort fields:
- `Packaging` - Sort by packaging type
- `ProductStatus` - Sort by product status
- `DigiKeyProductNumber` - Sort by DigiKey part number
- `ManufacturerProductNumber` - Sort by manufacturer part number
- `Manufacturer` - Sort by manufacturer name
- `MinimumQuantity` - Sort by minimum order quantity
- `QuantityAvailable` - Sort by available quantity
- `Price` - Sort by price
- `Supplier` - Sort by supplier
- `PriceManufacturerStandardPackage` - Sort by manufacturer standard package price

Sort orders: `Ascending` or `Descending`

### Search Options
Available filters for search methods:
- `LeadFree` - Lead-free products only
- `RoHSCompliant` - RoHS compliant products only
- `InStock` - In-stock products only
- `HasDatasheet` - Products with datasheets
- `HasProductPhoto` - Products with photos
- `Has3DModel` - Products with 3D models
- `NewProduct` - New products only

## Example Usage

The server exposes MCP tools that can be used by MCP clients like Claude Desktop, or programmatically via FastMCP clients.

### Search Examples
```python
# Basic keyword search
keyword_search("resistor", limit=10)

# Search with sorting by price (lowest first)
keyword_search("capacitor", limit=5, sort_field="Price", sort_order="Ascending")

# Search with filters
keyword_search("LED", limit=10, search_options="InStock,RoHSCompliant")

# Get product details
product_details("296-8875-1-ND")

# Get pricing for specific quantity
get_product_pricing("296-8875-1-ND", requested_quantity=100)
```

### MyLists Examples
```python
# Create a new list
create_list("My BOM", notes="Parts for Project X")

# Get all your lists
get_all_lists()

# Add parts to a list
parts_json = '[{"DigiKeyPartNumber": "296-8875-1-ND", "Quantity": 10, "CustomerReference": "R1"}]'
add_parts_to_list(list_id=12345, parts=parts_json)

# Get parts from a list
get_parts_by_list_id(list_id=12345)

# Get pricing summary for entire list
get_price_table(list_id=12345)

# Update list settings
settings_json = '{"Visibility": "ReadOnly"}'
update_list_settings(list_id=12345, settings=settings_json)

# Delete a list (will prompt user for confirmation)
delete_list(list_id=12345)
```

### Important Notes for Destructive Operations

All destructive operations (`delete_list`, `delete_part_from_list`, `delete_tag`, `delete_revision`) **automatically prompt the user for confirmation** before executing. This uses FastMCP's `ctx.elicit()` feature to request user approval at runtime.

When a destructive operation is called:
1. The tool pauses execution
2. A warning message is displayed to the user with details about what will be deleted
3. The user must explicitly approve or decline the action
4. If declined or cancelled, the operation is aborted with an error

This provides strong protection against accidental deletions while maintaining a clean API (no manual `confirm=True` parameters needed).

## Claude Desktop Integration

Add this to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS or `%APPDATA%\Claude\claude_desktop_config.json` on Windows):

### Local Installation

```json
{
  "mcpServers": {
    "digikey": {
      "command": "uv",
      "args": ["run", "python", "digikey_mcp_server.py"],
      "cwd": "/path/to/project"
    }
  }
}
```

### Docker Installation

The DigiKey MCP server supports automatic port discovery when running in Docker. The container automatically detects which host port is mapped to its OAuth callback server, enabling ephemeral port binding that avoids port conflicts.

#### Starting the Container

First, start the container using docker-compose:

```bash
docker-compose build
docker-compose up -d
```

The container will log the actual callback URL on startup:
```
✓ OAuth callback server started
  Container listening on: https://0.0.0.0:8139
  OAuth callback URL: https://localhost:54321/callback
  Host port mapping: 54321 → 8139
```

#### Claude Desktop Configuration

**Option 1: Using docker-compose (Recommended)**

First, start the container with docker-compose:
```bash
docker-compose up -d
```

Then connect via `docker exec`:
```json
{
  "mcpServers": {
    "digikey": {
      "command": "docker",
      "args": [
        "exec",
        "-i",
        "digikey-mcp-server",
        "uv",
        "run",
        "python",
        "digikey_mcp_server.py"
      ]
    }
  }
}
```

**Option 2: Standalone docker run with ephemeral port**

Run the container directly with all necessary mounts and ephemeral port binding:

```json
{
  "mcpServers": {
    "digikey": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "-p",
        "0:8139",
        "-v",
        "C:/docker/digikey-mcp-env:/workspace/.env:ro",
        "-v",
        "C:/docker/digikey-localhost-key.pem:/workspace/localhost-key.pem:ro",
        "-v",
        "C:/docker/digikey-localhost-cert.pem:/workspace/localhost-cert.pem:ro",
        "-v",
        "C:/docker/digikey-tokens:/workspace/.digikey_tokens",
        "-v",
        "/var/run/docker.sock:/var/run/docker.sock:ro",
        "digikey-mcp:latest",
        "/bin/bash",
        "-c",
        "cd /workspace && uv run digikey_mcp_server.py"
      ]
    }
  }
}
```

**Volume mappings:**
- `.env` - Environment variables (CLIENT_ID, CLIENT_SECRET, etc.) - read-only
- `localhost-key.pem` - SSL private key for OAuth callback - read-only
- `localhost-cert.pem` - SSL certificate for OAuth callback - read-only
- `.digikey_tokens` - OAuth token storage - read-write (persists between container runs)
- `/var/run/docker.sock` - Docker socket for port discovery - read-only

**Note:**
- Adjust the paths (`C:/docker/...`) to match your local file locations
- On Linux/macOS, use Unix-style paths (e.g., `/home/user/docker/...`)
- On Windows, use WSL paths if running Docker via WSL (e.g., `/mnt/c/docker/...`)
- Port mapping `-p 0:8139` enables ephemeral port binding with automatic discovery

#### Finding the Assigned Port (for troubleshooting)

To check which port was assigned:

```bash
# View port mapping
docker port digikey-mcp-server 8139

# View callback URL in logs
docker logs digikey-mcp-server | grep "OAuth callback URL"
```

#### Using a Fixed Port (Optional)

If you prefer a fixed port instead of ephemeral assignment, set it in `.env`:

```bash
OAUTH_PORT=8139
```

And update `docker-compose.yml`:
```yaml
ports:
  - "8139:8139"
```

#### How Automatic Port Discovery Works

- Docker assigns an available host port when using `0:8139` mapping
- Container queries Docker API via `/var/run/docker.sock` to discover the mapping
- OAuth callback URL dynamically uses the discovered port
- DigiKey OAuth works because the app is registered with `localhost` (no specific port required) 

# Developing

This project is designed to work with vscode and the devcontainers plugin. I recommend also running claude --dangerously-skip-permissions once inside the devcontainer for best results 😁