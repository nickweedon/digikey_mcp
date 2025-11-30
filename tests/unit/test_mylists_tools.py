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
    def test_get_all_lists_returns_list_array(
        self, authenticated_state, patched_api_base, fake_server
    ):
        """Test that get_all_lists returns an array of lists."""
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

        # Verify result is a list
        assert isinstance(result, list), f"Expected list, got {type(result)}"
        assert len(result) > 0, "Expected non-empty list"

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
        first_list = result[0]

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
        list_ids = [lst["ListId"] for lst in result]
        assert "list-001" in list_ids, "Expected list-001 in results"
        assert "list-002" in list_ids, "Expected list-002 in results"

        # Verify list names match
        list_names = {lst["ListId"]: lst["ListName"] for lst in result}
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

        # Just verify it returns a list without error
        assert isinstance(result, list)


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
