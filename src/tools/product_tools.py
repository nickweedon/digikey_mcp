"""Product Search API MCP Tools"""
from src.config import API_BASE
from src.api.client import _get_headers, _make_request


def register_product_tools(mcp):
    """Register Product Search API MCP tools."""

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
