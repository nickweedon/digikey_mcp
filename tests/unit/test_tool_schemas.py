"""Unit tests for MCP tool schema validation.

Tests that introspect MCP tools and verify their output schemas
conform to DigiKey API responses.
"""

import asyncio
import pytest
from typing import Any, Dict, List, Set
from dataclasses import is_dataclass, fields

from fastmcp import FastMCP


def get_all_mcp_tools():
    """Get all MCP tools from the server."""
    from src.tools.oauth_tools import register_oauth_tools
    from src.tools.product_tools import register_product_tools
    from src.tools.mylists_tools import register_mylists_tools

    mcp = FastMCP("test")
    register_oauth_tools(mcp)
    register_product_tools(mcp)
    register_mylists_tools(mcp)

    return mcp._tool_manager._tools


def extract_dict_keys_recursive(data: Any, prefix: str = "") -> Set[str]:
    """Extract all keys from a nested dictionary structure."""
    keys = set()

    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            keys.add(full_key)
            keys.update(extract_dict_keys_recursive(value, full_key))
    elif isinstance(data, list) and data:
        # Process first item in list to get structure
        keys.update(extract_dict_keys_recursive(data[0], f"{prefix}[]"))

    return keys


def dataclass_to_dict_keys(dc_type: type, prefix: str = "") -> Set[str]:
    """Extract expected keys from a dataclass type."""
    keys = set()

    if not is_dataclass(dc_type):
        return keys

    for field in fields(dc_type):
        full_key = f"{prefix}.{field.name}" if prefix else field.name
        keys.add(full_key)

        # Handle nested dataclasses
        field_type = field.type
        if hasattr(field_type, "__origin__"):
            # Handle List[X], Optional[X], etc.
            args = getattr(field_type, "__args__", ())
            for arg in args:
                if is_dataclass(arg):
                    keys.update(dataclass_to_dict_keys(arg, f"{full_key}[]"))
        elif is_dataclass(field_type):
            keys.update(dataclass_to_dict_keys(field_type, full_key))

    return keys


class TestToolIntrospection:
    """Tests for MCP tool introspection and registration."""

    @pytest.mark.unit
    def test_all_tools_registered(self):
        """Test that all expected tools are registered."""
        tools = get_all_mcp_tools()

        # OAuth tools
        oauth_tools = [
            "oauth_start_login",
            "oauth_complete_login",
            "oauth_status",
            "oauth_refresh",
            "oauth_logout",
        ]

        # Product tools
        product_tools = [
            "keyword_search",
            "product_details",
            "search_manufacturers",
            "search_categories",
            "get_category_by_id",
            "search_product_substitutions",
            "get_product_media",
            "get_product_pricing",
            "get_digi_reel_pricing",
        ]

        # MyLists tools
        mylists_tools = [
            "get_all_lists",
            "create_list",
            "get_list_by_id",
            "update_list_name",
            "delete_list",
            "get_parts_by_list_id",
            "add_parts_to_list",
            "get_part_from_list",
            "update_part_in_list",
            "delete_part_from_list",
        ]

        all_expected = oauth_tools + product_tools + mylists_tools

        for tool_name in all_expected:
            assert tool_name in tools, f"Tool '{tool_name}' not registered"

        # Verify count
        assert len(tools) == len(all_expected), \
            f"Expected {len(all_expected)} tools, got {len(tools)}"

    @pytest.mark.unit
    def test_all_tools_have_descriptions(self):
        """Test that all tools have descriptions."""
        tools = get_all_mcp_tools()

        for name, tool in tools.items():
            assert tool.description, f"Tool '{name}' has no description"
            assert len(tool.description) > 10, \
                f"Tool '{name}' has very short description"

    @pytest.mark.unit
    def test_all_tools_have_parameters_schema(self):
        """Test that all tools have parameters (input schema)."""
        tools = get_all_mcp_tools()

        for name, tool in tools.items():
            assert tool.parameters is not None, \
                f"Tool '{name}' has no parameters schema"
            assert isinstance(tool.parameters, dict), \
                f"Tool '{name}' parameters is not a dict"

    @pytest.mark.unit
    def test_tool_functions_are_callable(self):
        """Test that all tool functions are callable."""
        tools = get_all_mcp_tools()

        for name, tool in tools.items():
            assert callable(tool.fn), f"Tool '{name}' function is not callable"

    @pytest.mark.unit
    def test_product_tools_have_output_schemas(self):
        """Test that all product tools have output schemas for LLM understanding."""
        tools = get_all_mcp_tools()

        # These tools should have output schemas (return type annotations)
        product_tools_requiring_schema = [
            "keyword_search",
            "product_details",
            "search_manufacturers",
            "search_categories",
            "get_category_by_id",
            "search_product_substitutions",
            "get_product_media",
            "get_product_pricing",
            "get_digi_reel_pricing",
        ]

        for tool_name in product_tools_requiring_schema:
            tool = tools[tool_name]
            has_schema = hasattr(tool, 'output_schema') and tool.output_schema is not None
            assert has_schema, \
                f"Tool '{tool_name}' is missing output_schema. " \
                f"Add a return type annotation to generate schema for LLM."


class TestProductToolsWithFakeServer:
    """Tests for Product API tools using the fake server."""

    @pytest.mark.unit
    def test_keyword_search_returns_valid_response(
        self, client_authenticated_state, patched_api_base, fake_server
    ):
        """Test keyword_search returns response matching schema."""
        from src.tools.product_tools import register_product_tools

        mcp = FastMCP("test")
        register_product_tools(mcp)

        tools = mcp._tool_manager._tools
        keyword_search = tools["keyword_search"].fn

        result = keyword_search(keywords="resistor", limit=5)

        # Check it's a dict (JMESPath filtered result)
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"

        # Check required fields from default JMESPath query
        assert "ProductsCount" in result, "Missing ProductsCount"
        assert "Products" in result, "Missing Products"
        assert isinstance(result["Products"], list), "Products should be a list"

        # Check each product has expected filtered fields
        if result["Products"]:
            product = result["Products"][0]
            expected_fields = [
                "DigiKeyPartNumber",
                "ManufacturerPartNumber",
                "Manufacturer",
                "Description",
                "UnitPrice",
                "QuantityAvailable",
            ]
            for field in expected_fields:
                assert field in product, f"Missing field '{field}' in product"

    @pytest.mark.unit
    def test_keyword_search_custom_jmespath(
        self, client_authenticated_state, patched_api_base, fake_server
    ):
        """Test keyword_search with custom JMESPath query."""
        from src.tools.product_tools import register_product_tools

        mcp = FastMCP("test")
        register_product_tools(mcp)

        tools = mcp._tool_manager._tools
        keyword_search = tools["keyword_search"].fn

        # Custom query to get just count and part numbers
        custom_query = "{Count: ProductsCount, Parts: Products[].ManufacturerProductNumber}"
        result = keyword_search(keywords="resistor", limit=5, jmespath_query=custom_query)

        assert isinstance(result, dict)
        assert "Count" in result
        assert "Parts" in result
        assert isinstance(result["Parts"], list)

    @pytest.mark.unit
    def test_product_details_returns_valid_response(
        self, client_authenticated_state, patched_api_base, fake_server
    ):
        """Test product_details returns response with expected fields."""
        from src.tools.product_tools import register_product_tools

        mcp = FastMCP("test")
        register_product_tools(mcp)

        tools = mcp._tool_manager._tools
        product_details = tools["product_details"].fn

        result = product_details(product_number="RMCF0805JT10K0CT-ND")

        assert isinstance(result, dict), f"Expected dict, got {type(result)}"

        # Check required fields
        expected_fields = [
            "DigiKeyPartNumber",
            "ManufacturerPartNumber",
            "Manufacturer",
            "Description",
            "UnitPrice",
            "QuantityAvailable",
            "ProductStatus",
        ]
        for field in expected_fields:
            assert field in result, f"Missing field '{field}' in product details"

    @pytest.mark.unit
    def test_search_manufacturers_returns_valid_response(
        self, client_authenticated_state, patched_api_base, fake_server
    ):
        """Test search_manufacturers returns response with manufacturers."""
        from src.tools.product_tools import register_product_tools

        mcp = FastMCP("test")
        register_product_tools(mcp)

        tools = mcp._tool_manager._tools
        search_manufacturers = tools["search_manufacturers"].fn

        result = search_manufacturers()

        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "Manufacturers" in result, "Missing Manufacturers field"
        assert isinstance(result["Manufacturers"], list)

        if result["Manufacturers"]:
            mfr = result["Manufacturers"][0]
            assert "Id" in mfr, "Missing Id in manufacturer"
            assert "Name" in mfr, "Missing Name in manufacturer"

    @pytest.mark.unit
    def test_search_categories_returns_valid_response(
        self, client_authenticated_state, patched_api_base, fake_server
    ):
        """Test search_categories returns response with categories."""
        from src.tools.product_tools import register_product_tools

        mcp = FastMCP("test")
        register_product_tools(mcp)

        tools = mcp._tool_manager._tools
        search_categories = tools["search_categories"].fn

        result = search_categories()

        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "Categories" in result, "Missing Categories field"
        assert isinstance(result["Categories"], list)

        if result["Categories"]:
            cat = result["Categories"][0]
            assert "CategoryId" in cat, "Missing CategoryId"
            assert "Name" in cat, "Missing Name"

    @pytest.mark.unit
    def test_get_category_by_id_returns_valid_response(
        self, client_authenticated_state, patched_api_base, fake_server
    ):
        """Test get_category_by_id returns response with category details."""
        from src.tools.product_tools import register_product_tools

        mcp = FastMCP("test")
        register_product_tools(mcp)

        tools = mcp._tool_manager._tools
        get_category_by_id = tools["get_category_by_id"].fn

        result = get_category_by_id(category_id="52")

        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "CategoryId" in result, "Missing CategoryId"
        assert "Name" in result, "Missing Name"

    @pytest.mark.unit
    def test_search_product_substitutions_returns_valid_response(
        self, client_authenticated_state, patched_api_base, fake_server
    ):
        """Test search_product_substitutions returns response with substitutes."""
        from src.tools.product_tools import register_product_tools

        mcp = FastMCP("test")
        register_product_tools(mcp)

        tools = mcp._tool_manager._tools
        search_substitutions = tools["search_product_substitutions"].fn

        result = search_substitutions(product_number="RMCF0805JT10K0")

        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "Products" in result, "Missing Products field"
        assert isinstance(result["Products"], list)

    @pytest.mark.unit
    def test_get_product_media_returns_valid_response(
        self, client_authenticated_state, patched_api_base, fake_server
    ):
        """Test get_product_media returns response with media links."""
        from src.tools.product_tools import register_product_tools

        mcp = FastMCP("test")
        register_product_tools(mcp)

        tools = mcp._tool_manager._tools
        get_media = tools["get_product_media"].fn

        result = get_media(product_number="RMCF0805JT10K0CT-ND")

        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "MediaLinks" in result, "Missing MediaLinks field"
        assert isinstance(result["MediaLinks"], list)

    @pytest.mark.unit
    def test_get_product_pricing_returns_valid_response(
        self, client_authenticated_state, patched_api_base, fake_server
    ):
        """Test get_product_pricing returns response with pricing info."""
        from src.tools.product_tools import register_product_tools

        mcp = FastMCP("test")
        register_product_tools(mcp)

        tools = mcp._tool_manager._tools
        get_pricing = tools["get_product_pricing"].fn

        result = get_pricing(product_number="RMCF0805JT10K0CT-ND", requested_quantity=10)

        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "DigiKeyPartNumber" in result, "Missing DigiKeyPartNumber"
        assert "StandardPricing" in result, "Missing StandardPricing"
        assert "CalculatedPrice" in result or "UnitPrice" in result, "Missing price field"

    @pytest.mark.unit
    def test_get_digi_reel_pricing_returns_valid_response(
        self, client_authenticated_state, patched_api_base, fake_server
    ):
        """Test get_digi_reel_pricing returns response with DigiReel pricing."""
        from src.tools.product_tools import register_product_tools

        mcp = FastMCP("test")
        register_product_tools(mcp)

        tools = mcp._tool_manager._tools
        get_digireel = tools["get_digi_reel_pricing"].fn

        result = get_digireel(product_number="RMCF0805JT10K0CT-ND", requested_quantity=100)

        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "DigiKeyPartNumber" in result, "Missing DigiKeyPartNumber"
        assert "DigiReelFee" in result, "Missing DigiReelFee"
        assert "TotalPrice" in result or "ExtendedPrice" in result, "Missing price field"

    @pytest.mark.unit
    def test_keyword_search_with_regex_replace(
        self, client_authenticated_state, patched_api_base, fake_server
    ):
        """Test keyword_search with regex_replace custom function."""
        from src.tools.product_tools import register_product_tools

        mcp = FastMCP("test")
        register_product_tools(mcp)

        tools = mcp._tool_manager._tools
        keyword_search = tools["keyword_search"].fn

        # Use regex_replace to clean part numbers
        query = "Products[].{PartNum: regex_replace('[^A-Z0-9]', '', ManufacturerProductNumber)}"
        result = keyword_search(keywords="resistor", limit=5, jmespath_query=query)

        assert isinstance(result, list)
        if result:
            assert "PartNum" in result[0]
            # Verify that the part number has been cleaned (no special chars)
            assert all(c.isalnum() for c in result[0]["PartNum"] if c)

    @pytest.mark.unit
    def test_keyword_search_with_int_conversion(
        self, client_authenticated_state, patched_api_base, fake_server
    ):
        """Test keyword_search with int custom function."""
        from src.tools.product_tools import register_product_tools

        mcp = FastMCP("test")
        register_product_tools(mcp)

        tools = mcp._tool_manager._tools
        keyword_search = tools["keyword_search"].fn

        # Use int to convert quantity to integer
        query = "Products[].{Part: ManufacturerProductNumber, Qty: int(QuantityAvailable)}"
        result = keyword_search(keywords="resistor", limit=5, jmespath_query=query)

        assert isinstance(result, list)
        if result:
            assert "Part" in result[0]
            assert "Qty" in result[0]
            # Verify that Qty is an integer (or null if conversion failed)
            assert result[0]["Qty"] is None or isinstance(result[0]["Qty"], int)

    @pytest.mark.unit
    def test_keyword_search_with_combined_functions(
        self, client_authenticated_state, patched_api_base, fake_server
    ):
        """Test keyword_search with combined regex_replace + int functions."""
        from src.tools.product_tools import register_product_tools

        mcp = FastMCP("test")
        register_product_tools(mcp)

        tools = mcp._tool_manager._tools
        keyword_search = tools["keyword_search"].fn

        # Simulate extracting numeric value from a field with units
        # Since fake server data may not have parametric data with units,
        # we'll test the chaining capability with a simple numeric string
        query = """
        Products[].{
            Part: ManufacturerProductNumber,
            QtyNumeric: int(regex_replace('[^0-9]', '', ManufacturerProductNumber))
        }
        """
        result = keyword_search(keywords="resistor", limit=5, jmespath_query=query)

        assert isinstance(result, list)
        if result:
            assert "Part" in result[0]
            assert "QtyNumeric" in result[0]
            # QtyNumeric should be an integer or null
            assert result[0]["QtyNumeric"] is None or isinstance(result[0]["QtyNumeric"], int)

    @pytest.mark.unit
    def test_keyword_search_filter_by_converted_value(
        self, client_authenticated_state, patched_api_base, fake_server
    ):
        """Test filtering products by converted numeric value."""
        from src.tools.product_tools import register_product_tools

        mcp = FastMCP("test")
        register_product_tools(mcp)

        tools = mcp._tool_manager._tools
        keyword_search = tools["keyword_search"].fn

        # Filter products with QuantityAvailable >= 100 using int conversion
        query = "Products[?int(QuantityAvailable) >= `100`]"
        result = keyword_search(keywords="resistor", limit=50, jmespath_query=query)

        assert isinstance(result, list)
        # All results should have QuantityAvailable >= 100
        for product in result:
            if "QuantityAvailable" in product:
                qty = product["QuantityAvailable"]
                # Should be either an int >= 100, or could be the raw value
                if isinstance(qty, int):
                    assert qty >= 100


class TestMyListsToolsWithFakeServer:
    """Tests for MyLists API tools using the fake server."""

    @pytest.mark.unit
    def test_get_all_lists_returns_valid_response(
        self, authenticated_state, patched_api_base, fake_server
    ):
        """Test get_all_lists returns response matching schema."""
        from src.tools.mylists_tools import register_mylists_tools

        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        tools = mcp._tool_manager._tools
        get_all_lists = tools["get_all_lists"].fn

        result = get_all_lists()

        # Returns dict with 'lists' key (FastMCP requires dict for structured_content)
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "lists" in result, "Missing 'lists' key in result"
        assert isinstance(result["lists"], list), f"Expected list, got {type(result['lists'])}"

        if result["lists"]:
            lst = result["lists"][0]
            expected_fields = ["ListId", "ListName", "TotalParts", "DateCreated"]
            for field in expected_fields:
                assert field in lst, f"Missing field '{field}' in list"

    @pytest.mark.unit
    def test_get_parts_by_list_id_returns_valid_response(
        self, authenticated_state, patched_api_base, fake_server
    ):
        """Test get_parts_by_list_id returns response matching schema."""
        from src.tools.mylists_tools import register_mylists_tools

        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        tools = mcp._tool_manager._tools
        get_parts = tools["get_parts_by_list_id"].fn

        result = get_parts(list_id="list-001", limit=10)

        # With default JMESPath, returns dict with TotalParts and PartsList
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "TotalParts" in result, "Missing TotalParts"
        assert "PartsList" in result, "Missing PartsList"
        assert isinstance(result["PartsList"], list)

        if result["PartsList"]:
            part = result["PartsList"][0]
            expected_fields = [
                "UniqueId",
                "PartId",
                "ManufacturerPartNumber",
                "Manufacturer",
                "Description",
            ]
            for field in expected_fields:
                assert field in part, f"Missing field '{field}' in part"

    @pytest.mark.unit
    def test_get_parts_by_list_id_custom_jmespath(
        self, authenticated_state, patched_api_base, fake_server
    ):
        """Test get_parts_by_list_id with custom JMESPath query."""
        from src.tools.mylists_tools import register_mylists_tools

        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        tools = mcp._tool_manager._tools
        get_parts = tools["get_parts_by_list_id"].fn

        custom_query = "{Total: TotalParts, Parts: PartsList[].DigiKeyPartNumber}"
        result = get_parts(list_id="list-001", limit=10, jmespath_query=custom_query)

        assert isinstance(result, dict)
        assert "Total" in result
        assert "Parts" in result
        assert isinstance(result["Parts"], list)

    @pytest.mark.unit
    def test_get_part_from_list_returns_valid_response(
        self, authenticated_state, patched_api_base, fake_server
    ):
        """Test get_part_from_list returns response with part details."""
        from src.tools.mylists_tools import register_mylists_tools

        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        tools = mcp._tool_manager._tools
        get_part = tools["get_part_from_list"].fn

        result = get_part(list_id="list-001", part_id="unique-part-001")

        assert isinstance(result, dict), f"Expected dict, got {type(result)}"

        expected_fields = [
            "UniqueId",
            "DigiKeyPartNumber",
            "ManufacturerPartNumber",
        ]
        for field in expected_fields:
            assert field in result, f"Missing field '{field}' in part"

    @pytest.mark.unit
    def test_update_part_in_list_returns_valid_response(
        self, authenticated_state, patched_api_base, fake_server
    ):
        """Test update_part_in_list returns response with updated part."""
        from src.tools.mylists_tools import register_mylists_tools

        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        tools = mcp._tool_manager._tools
        update_part = tools["update_part_in_list"].fn

        result = update_part(
            list_id="list-001",
            part_id="unique-part-001",
            part_data={"customer_reference": "R1-Updated", "notes": "Test note"}
        )

        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "UniqueId" in result, "Missing UniqueId in updated part"


class TestOAuthToolsSchema:
    """Tests for OAuth tool response schemas."""

    @pytest.mark.unit
    def test_oauth_status_returns_valid_response(self):
        """Test oauth_status returns response with expected fields."""
        from src.tools.oauth_tools import register_oauth_tools

        mcp = FastMCP("test")
        register_oauth_tools(mcp)

        tools = mcp._tool_manager._tools
        oauth_status = tools["oauth_status"].fn

        result = oauth_status()

        assert isinstance(result, dict), f"Expected dict, got {type(result)}"

        expected_fields = [
            "auth_code_available",
            "client_token_available",
            "user_token_available",
            "refresh_token_available",
            "oauth_server_running",
            "message",
        ]
        for field in expected_fields:
            assert field in result, f"Missing field '{field}' in oauth_status"

    @pytest.mark.unit
    def test_oauth_logout_returns_valid_response(self):
        """Test oauth_logout returns response with expected fields."""
        from src.tools.oauth_tools import register_oauth_tools

        mcp = FastMCP("test")
        register_oauth_tools(mcp)

        tools = mcp._tool_manager._tools
        oauth_logout = tools["oauth_logout"].fn

        result = oauth_logout()

        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "status" in result, "Missing 'status' field"
        assert result["status"] == "success", f"Expected success, got {result['status']}"


class TestToolSchemaConsistency:
    """Tests that verify tool schemas match DigiKey API response structures."""

    @pytest.mark.unit
    def test_keyword_search_response_fields_match_digikey_api(
        self, client_authenticated_state, patched_api_base, fake_server
    ):
        """Verify keyword_search response fields match DigiKey API structure."""
        from src.tools.product_tools import register_product_tools

        mcp = FastMCP("test")
        register_product_tools(mcp)

        tools = mcp._tool_manager._tools
        keyword_search = tools["keyword_search"].fn

        # Get raw response (no JMESPath)
        raw_query = "@"  # Identity - returns full response
        result = keyword_search(keywords="resistor", limit=2, jmespath_query=raw_query)

        # These fields should exist in DigiKey API v4 keyword search response
        api_fields = [
            "Products",
            "ProductsCount",
        ]

        for field in api_fields:
            assert field in result, \
                f"Field '{field}' missing - API schema may have changed"

        # Check product structure
        if result.get("Products"):
            product = result["Products"][0]
            product_fields = [
                "Description",
                "Manufacturer",
                "ManufacturerProductNumber",
                "UnitPrice",
                "ProductUrl",
                "ProductVariations",
                "QuantityAvailable",
                "ProductStatus",
            ]
            for field in product_fields:
                assert field in product, \
                    f"Product field '{field}' missing - API schema may have changed"

    @pytest.mark.unit
    def test_mylists_parts_response_fields_match_digikey_api(
        self, authenticated_state, patched_api_base, fake_server
    ):
        """Verify get_parts_by_list_id response fields match DigiKey API structure."""
        from src.tools.mylists_tools import register_mylists_tools

        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        tools = mcp._tool_manager._tools
        get_parts = tools["get_parts_by_list_id"].fn

        # Get raw response
        raw_query = "@"
        result = get_parts(list_id="list-001", limit=10, jmespath_query=raw_query)

        # These fields should exist in DigiKey MyLists API v1 parts response
        api_fields = [
            "PartsList",
            "TotalParts",
        ]

        for field in api_fields:
            assert field in result, \
                f"Field '{field}' missing - API schema may have changed"

        # Check part structure
        if result.get("PartsList"):
            part = result["PartsList"][0]
            part_fields = [
                "PartId",
                "UniqueId",
                "DigiKeyPartNumber",
                "ManufacturerPartNumber",
                "Manufacturer",
                "Description",
                "QuantityAvailable",
                "Quantities",
                "Flags",
            ]
            for field in part_fields:
                assert field in part, \
                    f"Part field '{field}' missing - API schema may have changed"
