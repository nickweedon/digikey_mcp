import os
import json
import logging
from fastmcp import FastMCP
from dotenv import load_dotenv
import requests

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
USE_SANDBOX = os.getenv("USE_SANDBOX", "true").lower() == "false"

# DigiKey OAuth2 token endpoint
if USE_SANDBOX:
    TOKEN_URL = "https://sandbox-api.digikey.com/v1/oauth2/token"
    API_BASE = "https://sandbox-api.digikey.com"
else:
    TOKEN_URL = "https://api.digikey.com/v1/oauth2/token"
    API_BASE = "https://api.digikey.com"

# Initialize FastMCP server
mcp = FastMCP("DigiKey MCP Server")

def get_access_token():
    """Get OAuth2 access token from DigiKey."""
    # Check if credentials are loaded
    if not CLIENT_ID or not CLIENT_SECRET:
        raise ValueError("CLIENT_ID and CLIENT_SECRET must be set in .env file")
    
    data = {
        "grant_type": "client_credentials",
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
    }
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    
    endpoint = "SANDBOX" if USE_SANDBOX else "PRODUCTION"
    logger.info(f"Requesting token from {endpoint} with CLIENT_ID: {CLIENT_ID[:10]}...")
    resp = requests.post(TOKEN_URL, data=data, headers=headers)
    
    if resp.status_code != 200:
        logger.error(f"OAuth error: {resp.status_code} - {resp.text}")
        resp.raise_for_status()
    
    logger.info("Successfully obtained access token")
    return resp.json()["access_token"]

# Get access token at startup
logger.info("=== STARTING DIGIKEY MCP SERVER ===")
access_token = get_access_token()
logger.info("=== SERVER READY ===")

def _get_headers(customer_id: str = "0"):
    """Get standard headers for DigiKey API requests."""
    return {
        "Authorization": f"Bearer {access_token}",
        "X-DIGIKEY-Client-Id": CLIENT_ID,
        "Content-Type": "application/json",
        "X-DIGIKEY-Locale-Site": "US",
        "X-DIGIKEY-Locale-Language": "en",
        "X-DIGIKEY-Locale-Currency": "USD",
        "X-DIGIKEY-Customer-Id": customer_id,
    }

def _make_request(method: str, url: str, headers: dict, data: dict = None) -> dict:
    """Make an API request with error handling and logging."""
    logger.info(f"Making {method} request to {url}")
    logger.debug(f"Headers: {json.dumps({k: v for k, v in headers.items() if 'Authorization' not in k}, indent=2)}")
    if data:
        logger.debug(f"Request body: {json.dumps(data, indent=2)}")
    
    if method.upper() == "GET":
        resp = requests.get(url, headers=headers)
    else:
        resp = requests.post(url, headers=headers, json=data)
    
    logger.info(f"Response status: {resp.status_code}")
    if resp.status_code != 200:
        logger.error(f"API error: {resp.status_code} - {resp.text}")
        resp.raise_for_status()
    
    return resp.json()

@mcp.tool()
def keyword_search(keywords: str, limit: int = 5, manufacturer_id: str = None, category_id: str = None, search_options: str = None, sort_field: str = None, sort_order: str = "Ascending"):
    """Search DigiKey products by keyword.
    
    Args:
        keywords: Search terms or part numbers
        limit: Maximum number of results (default: 5)
        manufacturer_id: Filter by specific manufacturer ID
        category_id: Filter by specific category ID  
        search_options: Comma-delimited filters like LeadFree,RoHSCompliant,InStock
        sort_field: Field to sort by. Options: None, Packaging, ProductStatus, DigiKeyProductNumber, ManufacturerProductNumber, Manufacturer, MinimumQuantity, QuantityAvailable, Price, Supplier, PriceManufacturerStandardPackage
        sort_order: Sort direction - Ascending or Descending (default: Ascending)
    """
    url = f"{API_BASE}/products/v4/search/keyword"
    headers = _get_headers()
    
    body = {
        "Keywords": keywords,
        "Limit": limit
    }
    
    if manufacturer_id:
        body["ManufacturerId"] = manufacturer_id
    if category_id:
        body["CategoryId"] = category_id
    if search_options:
        body["SearchOptionList"] = search_options.split(",")
    
    # Add sort options if specified
    if sort_field:
        body["SortOptions"] = {
            "Field": sort_field,
            "SortOrder": sort_order
        }
    
    return _make_request("POST", url, headers, body)

@mcp.tool()
def product_details(product_number: str, manufacturer_id: str = None, customer_id: str = "0"):
    """Get detailed information for a specific product.
    
    Args:
        product_number: DigiKey or manufacturer part number
        manufacturer_id: Optional manufacturer ID for disambiguation
        customer_id: Customer ID for pricing (default: "0")
    """
    url = f"{API_BASE}/products/v4/search/{product_number}/productdetails"
    headers = _get_headers(customer_id)
    
    params = {}
    if manufacturer_id:
        params["manufacturerId"] = manufacturer_id
    
    if params:
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    
    return _make_request("GET", url, headers)

@mcp.tool()
def search_manufacturers():
    """Search and retrieve all product manufacturers."""
    url = f"{API_BASE}/products/v4/search/manufacturers"
    headers = _get_headers()
    return _make_request("GET", url, headers)

@mcp.tool()
def search_categories():
    """Search and retrieve all product categories."""
    url = f"{API_BASE}/products/v4/search/categories"
    headers = _get_headers()
    return _make_request("GET", url, headers)

@mcp.tool()
def get_category_by_id(category_id: int):
    """Get specific category details by ID.
    
    Args:
        category_id: The category ID to retrieve
    """
    url = f"{API_BASE}/products/v4/search/categories/{category_id}"
    headers = _get_headers()
    return _make_request("GET", url, headers)

@mcp.tool()
def search_product_substitutions(product_number: str, limit: int = 10, search_options: str = None, exclude_marketplace: bool = False):
    """Search for product substitutions for a given product.
    
    Args:
        product_number: The product to get substitutions for
        limit: Number of substitutions (default: 10)
        search_options: Filters like LeadFree,RoHSCompliant,InStock
        exclude_marketplace: Exclude marketplace products (default: False)
    """
    url = f"{API_BASE}/products/v4/search/{product_number}/substitutions"
    headers = _get_headers()
    
    params = {"limit": limit, "excludeMarketPlaceProducts": exclude_marketplace}
    if search_options:
        params["searchOptionList"] = search_options
    
    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    return _make_request("GET", url, headers)

@mcp.tool()
def get_product_media(product_number: str):
    """Get media (images, documents, videos) for a product.
    
    Args:
        product_number: The product to get media for
    """
    url = f"{API_BASE}/products/v4/search/{product_number}/media"
    headers = _get_headers()
    return _make_request("GET", url, headers)

@mcp.tool()
def get_product_pricing(product_number: str, customer_id: str = "0", requested_quantity: int = 1):
    """Get detailed pricing information for a product.
    
    Args:
        product_number: The product to get pricing for
        customer_id: Customer ID for pricing (default: "0")
        requested_quantity: Quantity for pricing calculation (default: 1)
    """
    url = f"{API_BASE}/products/v4/search/{product_number}/productpricing"
    headers = _get_headers(customer_id)
    
    params = {"requestedQuantity": requested_quantity}
    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    
    return _make_request("GET", url, headers)

@mcp.tool()
def get_digi_reel_pricing(product_number: str, requested_quantity: int, customer_id: str = "0"):
    """Get DigiReel pricing for a product.

    Args:
        product_number: DigiKey product number (must be DigiReel compatible)
        requested_quantity: Quantity for DigiReel pricing
        customer_id: Customer ID for pricing (default: "0")
    """
    url = f"{API_BASE}/products/v4/search/{product_number}/digireelpricing"
    headers = _get_headers(customer_id)

    params = {"requestedQuantity": requested_quantity}
    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return _make_request("GET", url, headers)

# ============================================================================
# MyLists API Methods
# ============================================================================

@mcp.tool()
def get_all_lists(customer_id: str = "0"):
    """Get all MyLists for the user.

    Args:
        customer_id: Customer ID (default: "0")

    Returns:
        List of all user's lists with metadata
    """
    url = f"{API_BASE}/mylists/v2/Lists"
    headers = _get_headers(customer_id)
    return _make_request("GET", url, headers)

@mcp.tool()
def create_list(list_name: str, notes: str = None, customer_id: str = "0"):
    """Create a new MyList.

    Args:
        list_name: Name for the new list (required)
        notes: Optional notes/description for the list
        customer_id: Customer ID (default: "0")

    Returns:
        Created list information including list_id
    """
    url = f"{API_BASE}/mylists/v2/CreateList"
    headers = _get_headers(customer_id)

    body = {"ListName": list_name}
    if notes:
        body["Notes"] = notes

    return _make_request("POST", url, headers, body)

@mcp.tool()
def get_list_by_id(list_id: int, include_parts: bool = False, customer_id: str = "0"):
    """Get detailed information about a specific list.

    Args:
        list_id: The list ID to retrieve
        include_parts: Whether to include the parts list in response (default: False)
        customer_id: Customer ID (default: "0")

    Returns:
        Detailed list information and optionally parts data
    """
    url = f"{API_BASE}/mylists/v2/GetListByListId"
    headers = _get_headers(customer_id)

    params = {"listId": list_id, "includePartsList": str(include_parts).lower()}
    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return _make_request("GET", url, headers)

@mcp.tool()
def update_list_name(list_id: int, new_name: str, customer_id: str = "0"):
    """Update the name of an existing list.

    Args:
        list_id: The list ID to update
        new_name: New name for the list
        customer_id: Customer ID (default: "0")

    Returns:
        Updated list information
    """
    url = f"{API_BASE}/mylists/v2/UpdateListName"
    headers = _get_headers(customer_id)

    body = {"ListId": list_id, "ListName": new_name}
    return _make_request("PUT", url, headers, body)

@mcp.tool()
def is_valid_list_name(list_name: str, customer_id: str = "0"):
    """Check if a list name is valid (not already in use).

    Args:
        list_name: The name to validate
        customer_id: Customer ID (default: "0")

    Returns:
        Boolean indicating if the name is available
    """
    url = f"{API_BASE}/mylists/v2/IsValidListName"
    headers = _get_headers(customer_id)

    params = {"listName": list_name}
    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return _make_request("GET", url, headers)

@mcp.tool()
def get_valid_list_name(list_name: str, customer_id: str = "0"):
    """Get a valid list name (adds number suffix if name exists).

    Args:
        list_name: The desired list name
        customer_id: Customer ID (default: "0")

    Returns:
        A valid list name (original or with number suffix)
    """
    url = f"{API_BASE}/mylists/v2/ValidListName"
    headers = _get_headers(customer_id)

    params = {"listName": list_name}
    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return _make_request("GET", url, headers)

@mcp.tool()
async def delete_list(list_id: int, customer_id: str = "0", ctx=None):
    """⚠️ DESTRUCTIVE: Permanently delete a list and all its contents.

    This operation cannot be undone. The list and all associated parts,
    settings, and metadata will be permanently removed.

    This tool will prompt for user confirmation before proceeding.

    Args:
        list_id: The list ID to delete
        customer_id: Customer ID (default: "0")

    Returns:
        Deletion confirmation response
    """
    # Request user confirmation
    result = await ctx.elicit(
        f"⚠️ WARNING: You are about to permanently delete list ID {list_id} and ALL its contents. "
        "This action CANNOT be undone. Do you want to proceed?",
        response_type=None
    )

    if result.action != "accept":
        raise ValueError(f"List deletion cancelled by user (action: {result.action})")

    url = f"{API_BASE}/mylists/v2/DeleteList"
    headers = _get_headers(customer_id)

    params = {"listId": list_id}
    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return _make_request("DELETE", url, headers)

# Parts Management Methods

@mcp.tool()
def get_parts_by_list_id(list_id: int, start_index: int = None, count: int = None, customer_id: str = "0"):
    """Get all parts from a specific list with optional pagination.

    Args:
        list_id: The list ID to get parts from
        start_index: Optional starting index for pagination
        count: Optional number of parts to return
        customer_id: Customer ID (default: "0")

    Returns:
        List of parts with details including pricing, availability, etc.
    """
    url = f"{API_BASE}/mylists/v2/GetPartsByListId"
    headers = _get_headers(customer_id)

    params = {"listId": list_id}
    if start_index is not None:
        params["startIndex"] = start_index
    if count is not None:
        params["numberOfParts"] = count

    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
    return _make_request("GET", url, headers)

@mcp.tool()
def add_parts_to_list(list_id: int, parts: str, customer_id: str = "0"):
    """Add parts to a list.

    Args:
        list_id: The list ID to add parts to
        parts: JSON string containing parts data. Example format:
               '[{"DigiKeyPartNumber": "296-8875-1-ND", "Quantity": 10, "CustomerReference": "R1"}]'
        customer_id: Customer ID (default: "0")

    Returns:
        Response with added parts information
    """
    url = f"{API_BASE}/mylists/v2/AddPartsToListId"
    headers = _get_headers(customer_id)

    # Parse the JSON string
    parts_data = json.loads(parts) if isinstance(parts, str) else parts

    body = {
        "ListId": list_id,
        "Parts": parts_data
    }

    return _make_request("POST", url, headers, body)

@mcp.tool()
def get_part_from_list(list_id: int, unique_id: str, customer_id: str = "0"):
    """Get a specific part from a list by its unique ID.

    Args:
        list_id: The list ID
        unique_id: The unique ID of the part in the list
        customer_id: Customer ID (default: "0")

    Returns:
        Detailed part information
    """
    url = f"{API_BASE}/mylists/v2/GetPartFromListByUniqueId"
    headers = _get_headers(customer_id)

    params = {"listId": list_id, "uniqueId": unique_id}
    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return _make_request("GET", url, headers)

@mcp.tool()
def update_part_in_list(list_id: int, unique_id: str, part_data: str, customer_id: str = "0"):
    """Update part information in a list.

    Args:
        list_id: The list ID
        unique_id: The unique ID of the part to update
        part_data: JSON string with updated part data. Example:
                   '{"Quantity": 20, "CustomerReference": "R1-Updated"}'
        customer_id: Customer ID (default: "0")

    Returns:
        Updated part information
    """
    url = f"{API_BASE}/mylists/v2/UpdatePartFromListByUniqueId"
    headers = _get_headers(customer_id)

    # Parse the JSON string
    data = json.loads(part_data) if isinstance(part_data, str) else part_data

    body = {
        "ListId": list_id,
        "UniqueId": unique_id,
        **data
    }

    return _make_request("PUT", url, headers, body)

@mcp.tool()
async def delete_part_from_list(list_id: int, unique_id: str, customer_id: str = "0", ctx=None):
    """⚠️ DESTRUCTIVE: Permanently delete a part from a list.

    This operation cannot be undone. The part will be permanently removed from the list.

    This tool will prompt for user confirmation before proceeding.

    Args:
        list_id: The list ID
        unique_id: The unique ID of the part to delete
        customer_id: Customer ID (default: "0")

    Returns:
        Deletion confirmation response
    """
    # Request user confirmation
    result = await ctx.elicit(
        f"⚠️ WARNING: You are about to permanently delete part '{unique_id}' from list ID {list_id}. "
        "This action CANNOT be undone. Do you want to proceed?",
        response_type=None
    )

    if result.action != "accept":
        raise ValueError(f"Part deletion cancelled by user (action: {result.action})")

    url = f"{API_BASE}/mylists/v2/DeletePartFromListByUniqueId"
    headers = _get_headers(customer_id)

    params = {"listId": list_id, "uniqueId": unique_id}
    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return _make_request("DELETE", url, headers)

# Tag Methods

@mcp.tool()
def create_tag(tag_name: str, customer_id: str = "0"):
    """Create a new tag for organizing lists.

    Args:
        tag_name: Name for the new tag
        customer_id: Customer ID (default: "0")

    Returns:
        Created tag information
    """
    url = f"{API_BASE}/mylists/v2/CreateTag"
    headers = _get_headers(customer_id)

    body = {"TagName": tag_name}
    return _make_request("POST", url, headers, body)

@mcp.tool()
async def delete_tag(tag_id: int, customer_id: str = "0", ctx=None):
    """⚠️ DESTRUCTIVE: Permanently delete a tag.

    This operation cannot be undone. The tag will be removed from all lists using it.

    This tool will prompt for user confirmation before proceeding.

    Args:
        tag_id: The tag ID to delete
        customer_id: Customer ID (default: "0")

    Returns:
        Deletion confirmation response
    """
    # Request user confirmation
    result = await ctx.elicit(
        f"⚠️ WARNING: You are about to permanently delete tag ID {tag_id}. "
        "This will remove the tag from ALL lists using it. This action CANNOT be undone. Do you want to proceed?",
        response_type=None
    )

    if result.action != "accept":
        raise ValueError(f"Tag deletion cancelled by user (action: {result.action})")

    url = f"{API_BASE}/mylists/v2/DeleteTag"
    headers = _get_headers(customer_id)

    params = {"tagId": tag_id}
    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return _make_request("DELETE", url, headers)

# Revision Methods

@mcp.tool()
def create_revision(list_id: int, revision_name: str, customer_id: str = "0"):
    """Create a new revision of a list.

    Args:
        list_id: The list ID to create a revision for
        revision_name: Name for the revision
        customer_id: Customer ID (default: "0")

    Returns:
        Created revision information
    """
    url = f"{API_BASE}/mylists/v2/CreateRevision"
    headers = _get_headers(customer_id)

    body = {"ListId": list_id, "RevisionName": revision_name}
    return _make_request("POST", url, headers, body)

@mcp.tool()
def get_revision_by_id(revision_id: int, customer_id: str = "0"):
    """Get details of a specific revision.

    Args:
        revision_id: The revision ID to retrieve
        customer_id: Customer ID (default: "0")

    Returns:
        Revision details including parts list
    """
    url = f"{API_BASE}/mylists/v2/GetRevisionByRevisionId"
    headers = _get_headers(customer_id)

    params = {"revisionId": revision_id}
    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return _make_request("GET", url, headers)

@mcp.tool()
async def delete_revision(revision_id: int, customer_id: str = "0", ctx=None):
    """⚠️ DESTRUCTIVE: Permanently delete a list revision.

    This operation cannot be undone. The revision and its history will be permanently removed.

    This tool will prompt for user confirmation before proceeding.

    Args:
        revision_id: The revision ID to delete
        customer_id: Customer ID (default: "0")

    Returns:
        Deletion confirmation response
    """
    # Request user confirmation
    result = await ctx.elicit(
        f"⚠️ WARNING: You are about to permanently delete revision ID {revision_id} and its history. "
        "This action CANNOT be undone. Do you want to proceed?",
        response_type=None
    )

    if result.action != "accept":
        raise ValueError(f"Revision deletion cancelled by user (action: {result.action})")

    url = f"{API_BASE}/mylists/v2/DeleteRevision"
    headers = _get_headers(customer_id)

    params = {"revisionId": revision_id}
    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return _make_request("DELETE", url, headers)

# Additional MyLists Methods

@mcp.tool()
def get_price_table(list_id: int, customer_id: str = "0"):
    """Get aggregate pricing information for all parts in a list.

    Args:
        list_id: The list ID to get pricing for
        customer_id: Customer ID (default: "0")

    Returns:
        Price table with total costs at different quantity breaks
    """
    url = f"{API_BASE}/mylists/v2/GetPriceTable"
    headers = _get_headers(customer_id)

    params = {"listId": list_id}
    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return _make_request("GET", url, headers)

@mcp.tool()
def get_alternate_part_info(part_number: str, customer_id: str = "0"):
    """Get alternate/substitute part information.

    Args:
        part_number: The DigiKey part number
        customer_id: Customer ID (default: "0")

    Returns:
        Information about alternate and substitute parts
    """
    url = f"{API_BASE}/mylists/v2/GetAlternatePartInfo"
    headers = _get_headers(customer_id)

    params = {"partNumber": part_number}
    url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

    return _make_request("GET", url, headers)

@mcp.tool()
def update_list_settings(list_id: int, settings: str, customer_id: str = "0"):
    """Update list settings (visibility, package preferences, etc.).

    Args:
        list_id: The list ID to update settings for
        settings: JSON string with settings. Example:
                  '{"Visibility": "ReadOnly", "PackagePreference": "CutTape"}'
        customer_id: Customer ID (default: "0")

    Returns:
        Updated list settings
    """
    url = f"{API_BASE}/mylists/v2/UpdateListSettings"
    headers = _get_headers(customer_id)

    # Parse the JSON string
    settings_data = json.loads(settings) if isinstance(settings, str) else settings

    body = {
        "ListId": list_id,
        **settings_data
    }

    return _make_request("PUT", url, headers, body)


def main():
    mcp.run()

if __name__ == "__main__":
    main() 