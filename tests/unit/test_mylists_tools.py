"""Unit tests for MyLists MCP tools.

Tests the MyLists API tools using a fake DigiKey server.
"""

import pytest
from unittest.mock import patch

from fastmcp import FastMCP

from tests.fake_server.responses.mylists import SAMPLE_LISTS


class TestGetAllLists:
    """Tests for the get_all_lists tool."""

    @pytest.mark.unit
    def test_get_all_lists_returns_dict_with_lists(
        self, authenticated_state, patched_api_base, fake_server
    ):
        """Test that get_all_lists returns a dict with 'lists' key containing array."""
        # Import after patching to get the patched API_BASE
        from src.tools.mylists_tools import register_mylists_tools

        # Create a test MCP instance and register tools
        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        # Get the registered tool function
        tools = mcp._tool_manager._tools
        get_all_lists = tools["get_all_lists"].fn

        # Call the tool
        result = get_all_lists()

        # Verify result is a dict with 'lists' key (FastMCP requires dict for structured_content)
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"
        assert "lists" in result, "Expected 'lists' key in result"
        assert isinstance(result["lists"], list), f"Expected list, got {type(result['lists'])}"
        assert len(result["lists"]) > 0, "Expected non-empty list"

    @pytest.mark.unit
    def test_get_all_lists_contains_required_fields(
        self, authenticated_state, patched_api_base, fake_server
    ):
        """Test that returned lists contain required fields."""
        from src.tools.mylists_tools import register_mylists_tools

        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        tools = mcp._tool_manager._tools
        get_all_lists = tools["get_all_lists"].fn

        result = get_all_lists()

        # Check first list has required fields
        required_fields = ["ListId", "ListName", "TotalParts", "DateCreated"]
        first_list = result["lists"][0]

        for field in required_fields:
            assert field in first_list, f"Missing required field: {field}"

    @pytest.mark.unit
    def test_get_all_lists_matches_sample_data(
        self, authenticated_state, patched_api_base, fake_server
    ):
        """Test that returned lists match expected sample data."""
        from src.tools.mylists_tools import register_mylists_tools

        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        tools = mcp._tool_manager._tools
        get_all_lists = tools["get_all_lists"].fn

        result = get_all_lists()

        # Verify we got the expected sample lists
        list_ids = [lst["ListId"] for lst in result["lists"]]
        assert "list-001" in list_ids, "Expected list-001 in results"
        assert "list-002" in list_ids, "Expected list-002 in results"

        # Verify list names match
        list_names = {lst["ListId"]: lst["ListName"] for lst in result["lists"]}
        assert list_names["list-001"] == "Test Components"
        assert list_names["list-002"] == "Project Alpha BOM"

    @pytest.mark.unit
    def test_get_all_lists_without_auth_raises_error(
        self, reset_oauth_state, patched_api_base, fake_server
    ):
        """Test that calling without authentication raises ValueError."""
        from src.tools.mylists_tools import register_mylists_tools

        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        tools = mcp._tool_manager._tools
        get_all_lists = tools["get_all_lists"].fn

        # Should raise ValueError when not authenticated
        with pytest.raises(ValueError) as exc_info:
            get_all_lists()

        assert "Authentication" in str(exc_info.value) or "Authenticate" in str(
            exc_info.value
        )

    @pytest.mark.unit
    def test_get_all_lists_with_custom_customer_id(
        self, authenticated_state, patched_api_base, fake_server
    ):
        """Test that customer_id parameter is accepted."""
        from src.tools.mylists_tools import register_mylists_tools

        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        tools = mcp._tool_manager._tools
        get_all_lists = tools["get_all_lists"].fn

        # Should work with custom customer_id
        result = get_all_lists(customer_id="12345")

        # Verify it returns a dict with lists key
        assert isinstance(result, dict)
        assert "lists" in result


class TestCreateList:
    """Tests for the create_list tool."""

    @pytest.mark.unit
    def test_create_list_returns_list_id(
        self, authenticated_state, patched_api_base, fake_server, reset_fake_server
    ):
        """Test that create_list returns a list ID string."""
        from src.tools.mylists_tools import register_mylists_tools

        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        tools = mcp._tool_manager._tools
        create_list = tools["create_list"].fn

        result = create_list(list_name="New Test List")

        # Result should be a string (list ID)
        assert isinstance(result, str), f"Expected string, got {type(result)}"
        assert len(result) > 0, "List ID should not be empty"

    @pytest.mark.unit
    def test_create_list_with_tags(
        self, authenticated_state, patched_api_base, fake_server, reset_fake_server
    ):
        """Test that create_list accepts tags parameter."""
        from src.tools.mylists_tools import register_mylists_tools

        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        tools = mcp._tool_manager._tools
        create_list = tools["create_list"].fn

        result = create_list(list_name="Tagged List", tags=["tag1", "tag2"])

        assert isinstance(result, str)

    @pytest.mark.unit
    def test_create_list_empty_name_raises_error(
        self, authenticated_state, patched_api_base, fake_server
    ):
        """Test that create_list with empty name raises ValueError."""
        from src.tools.mylists_tools import register_mylists_tools

        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        tools = mcp._tool_manager._tools
        create_list = tools["create_list"].fn

        with pytest.raises(ValueError) as exc_info:
            create_list(list_name="")

        assert "empty" in str(exc_info.value).lower()


class TestGetListById:
    """Tests for the get_list_by_id tool."""

    @pytest.mark.unit
    def test_get_list_by_id_returns_list_details(
        self, authenticated_state, patched_api_base, fake_server
    ):
        """Test that get_list_by_id returns list details."""
        from src.tools.mylists_tools import register_mylists_tools

        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        tools = mcp._tool_manager._tools
        get_list_by_id = tools["get_list_by_id"].fn

        result = get_list_by_id(list_id="list-001")

        assert isinstance(result, dict)
        assert result["ListId"] == "list-001"
        assert result["ListName"] == "Test Components"

    @pytest.mark.unit
    def test_get_list_by_id_not_found(
        self, authenticated_state, patched_api_base, fake_server
    ):
        """Test that get_list_by_id returns error for non-existent list."""
        from src.tools.mylists_tools import register_mylists_tools

        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        tools = mcp._tool_manager._tools
        get_list_by_id = tools["get_list_by_id"].fn

        result = get_list_by_id(list_id="nonexistent-list")

        # Should return an error dict
        assert isinstance(result, dict)
        assert "error" in result


class TestRequestedPartConversion:
    """Tests for RequestedPart and PartQuantity dataclass conversions."""

    @pytest.mark.unit
    def test_requested_part_simple_conversion(self):
        """Test RequestedPart converts to correct API format with basic fields."""
        from src.tools.mylists_tools import RequestedPart

        part = RequestedPart(
            requested_part_number="296-8875-1-ND",
            customer_reference="R1"
        )
        result = part.to_dict()

        assert result["RequestedPartNumber"] == "296-8875-1-ND"
        assert result["CustomerReference"] == "R1"
        # None values should be excluded
        assert "PartId" not in result
        assert "ManufacturerName" not in result
        assert "Notes" not in result

    @pytest.mark.unit
    def test_requested_part_with_all_fields(self):
        """Test RequestedPart includes all non-None fields."""
        from src.tools.mylists_tools import RequestedPart

        part = RequestedPart(
            part_id="12345",
            requested_part_number="296-8875-1-ND",
            manufacturer_name="Texas Instruments",
            customer_reference="R1",
            reference_designator="R1",
            notes="Test note",
            selected_quantity_index=0,
            attrition=5
        )
        result = part.to_dict()

        assert result["PartId"] == "12345"
        assert result["RequestedPartNumber"] == "296-8875-1-ND"
        assert result["ManufacturerName"] == "Texas Instruments"
        assert result["CustomerReference"] == "R1"
        assert result["ReferenceDesignator"] == "R1"
        assert result["Notes"] == "Test note"
        assert result["SelectedQuantityIndex"] == 0
        assert result["Attrition"] == 5

    @pytest.mark.unit
    def test_part_quantity_conversion(self):
        """Test PartQuantity converts to correct API format."""
        from src.tools.mylists_tools import PartQuantity

        qty = PartQuantity(
            quantity=10,
            target_price=1.50
        )
        result = qty.to_dict()

        assert result["Quantity"] == 10
        assert result["TargetPrice"] == 1.50
        # None values should be excluded
        assert "SelectedPackType" not in result

    @pytest.mark.unit
    def test_part_quantity_excludes_none_values(self):
        """Test PartQuantity excludes None values from dict."""
        from src.tools.mylists_tools import PartQuantity

        qty = PartQuantity(quantity=10)
        result = qty.to_dict()

        assert result == {"Quantity": 10}
        assert "SelectedPackType" not in result
        assert "TargetPrice" not in result

    @pytest.mark.unit
    def test_requested_part_with_quantities(self):
        """Test RequestedPart with nested quantities list."""
        from src.tools.mylists_tools import RequestedPart, PartQuantity

        part = RequestedPart(
            requested_part_number="296-8875-1-ND",
            customer_reference="R1",
            reference_designator="R1",
            quantities=[
                PartQuantity(quantity=10),
                PartQuantity(quantity=20, target_price=1.50)
            ]
        )
        result = part.to_dict()

        assert len(result["Quantities"]) == 2
        assert result["Quantities"][0]["Quantity"] == 10
        assert result["Quantities"][1]["Quantity"] == 20
        assert result["Quantities"][1]["TargetPrice"] == 1.50
        # First quantity should not have TargetPrice
        assert "TargetPrice" not in result["Quantities"][0]

    @pytest.mark.unit
    def test_parts_list_produces_valid_array(self):
        """Test that multiple RequestedParts produce valid JSON array."""
        from src.tools.mylists_tools import RequestedPart
        import json

        parts = [
            RequestedPart(requested_part_number="296-8875-1-ND", customer_reference="R1"),
            RequestedPart(requested_part_number="P5555-ND", reference_designator="C1")
        ]
        parts_list = [p.to_dict() for p in parts]

        # Should be serializable as JSON array
        json_output = json.dumps(parts_list)
        parsed = json.loads(json_output)

        assert isinstance(parsed, list)
        assert len(parsed) == 2
        assert parsed[0]["RequestedPartNumber"] == "296-8875-1-ND"
        assert parsed[1]["RequestedPartNumber"] == "P5555-ND"
