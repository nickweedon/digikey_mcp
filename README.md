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

### 3. Run the server
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

Add this to your Claude Desktop config (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

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