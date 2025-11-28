"""MyLists API MCP Tools"""
import json
from src.config import API_BASE
from src.api.client import _get_headers, _make_request
from src.api.auth import _require_user_auth


def register_mylists_tools(mcp):
    """Register MyLists API MCP tools."""

    @mcp.tool()
    def get_all_lists(customer_id: str = "0"):
        """Get all MyLists for the authenticated user.

        ⚠️ Requires user authentication via oauth_start_login()

        Args:
            customer_id: Customer ID (default: "0")

        Returns:
            List of all user's lists with metadata
        """
        _require_user_auth()
        url = f"{API_BASE}/mylists/v1/lists"
        headers = _get_headers(customer_id, use_user_token=True)
        return _make_request("GET", url, headers, use_user_token=True)

    @mcp.tool()
    def create_list(list_name: str, notes: str = None, customer_id: str = "0"):
        """Create a new MyList.

        ⚠️ Requires user authentication via oauth_start_login()

        Args:
            list_name: Name for the new list (required)
            notes: Optional notes/description for the list
            customer_id: Customer ID (default: "0")

        Returns:
            Created list information including list_id
        """
        _require_user_auth()
        url = f"{API_BASE}/mylists/v1/lists"
        headers = _get_headers(customer_id, use_user_token=True)

        body = {"listName": list_name}
        if notes:
            body["notes"] = notes

        return _make_request("POST", url, headers, body, use_user_token=True)

    @mcp.tool()
    def get_list_by_id(list_id: str, include_parts: bool = False, customer_id: str = "0"):
        """Get detailed information about a specific list.

        ⚠️ Requires user authentication via oauth_start_login()

        Args:
            list_id: The list ID to retrieve
            include_parts: Whether to include the parts list in response (default: False)
            customer_id: Customer ID (default: "0")

        Returns:
            Detailed list information and optionally parts data
        """
        _require_user_auth()
        url = f"{API_BASE}/mylists/v1/lists/{list_id}"
        headers = _get_headers(customer_id, use_user_token=True)

        if include_parts:
            url += "?includePartsList=true"

        return _make_request("GET", url, headers, use_user_token=True)

    @mcp.tool()
    def update_list_name(list_id: str, new_name: str, customer_id: str = "0"):
        """Update the name of an existing list.

        ⚠️ Requires user authentication via oauth_start_login()

        Args:
            list_id: The list ID to update
            new_name: New name for the list
            customer_id: Customer ID (default: "0")

        Returns:
            Updated list information
        """
        _require_user_auth()
        url = f"{API_BASE}/mylists/v1/lists/{list_id}"
        headers = _get_headers(customer_id, use_user_token=True)

        body = {"listName": new_name}
        return _make_request("PUT", url, headers, body, use_user_token=True)

    @mcp.tool()
    async def delete_list(list_id: str, customer_id: str = "0", ctx=None):
        """⚠️ DESTRUCTIVE: Permanently delete a list and all its contents.

        ⚠️ Requires user authentication via oauth_start_login()

        This operation cannot be undone. The list and all associated parts,
        settings, and metadata will be permanently removed.

        This tool will prompt for user confirmation before proceeding.

        Args:
            list_id: The list ID to delete
            customer_id: Customer ID (default: "0")

        Returns:
            Deletion confirmation response
        """
        _require_user_auth()

        result = await ctx.elicit(
            f"⚠️ WARNING: You are about to permanently delete list ID {list_id} and ALL its contents. "
            "This action CANNOT be undone. Do you want to proceed?",
            response_type=None
        )

        if result.action != "accept":
            raise ValueError(f"List deletion cancelled by user (action: {result.action})")

        url = f"{API_BASE}/mylists/v1/lists/{list_id}"
        headers = _get_headers(customer_id, use_user_token=True)

        return _make_request("DELETE", url, headers, use_user_token=True)

    @mcp.tool()
    def get_parts_by_list_id(list_id: str, start_index: int = None, limit: int = None, customer_id: str = "0"):
        """Get all parts from a specific list with optional pagination.

        ⚠️ Requires user authentication via oauth_start_login()

        Args:
            list_id: The list ID to get parts from
            start_index: Optional starting index for pagination
            limit: Optional number of parts to return
            customer_id: Customer ID (default: "0")

        Returns:
            List of parts with details including pricing, availability, etc.
        """
        _require_user_auth()
        url = f"{API_BASE}/mylists/v1/lists/{list_id}/parts"
        headers = _get_headers(customer_id, use_user_token=True)

        params = []
        if start_index is not None:
            params.append(f"startIndex={start_index}")
        if limit is not None:
            params.append(f"limit={limit}")

        if params:
            url += "?" + "&".join(params)

        return _make_request("GET", url, headers, use_user_token=True)

    @mcp.tool()
    def add_parts_to_list(list_id: str, parts: str, customer_id: str = "0"):
        """Add parts to a list.

        ⚠️ Requires user authentication via oauth_start_login()

        Args:
            list_id: The list ID to add parts to
            parts: JSON string containing parts data. Example format:
                   '[{"digiKeyPartNumber": "296-8875-1-ND", "quantity": 10, "customerReference": "R1"}]'
            customer_id: Customer ID (default: "0")

        Returns:
            Response with added parts information
        """
        _require_user_auth()
        url = f"{API_BASE}/mylists/v1/lists/{list_id}/parts"
        headers = _get_headers(customer_id, use_user_token=True)

        parts_data = json.loads(parts) if isinstance(parts, str) else parts

        body = {"parts": parts_data}

        return _make_request("POST", url, headers, body, use_user_token=True)

    @mcp.tool()
    def get_part_from_list(list_id: str, part_id: str, customer_id: str = "0"):
        """Get a specific part from a list by its part ID.

        ⚠️ Requires user authentication via oauth_start_login()

        Args:
            list_id: The list ID
            part_id: The ID of the part in the list
            customer_id: Customer ID (default: "0")

        Returns:
            Detailed part information
        """
        _require_user_auth()
        url = f"{API_BASE}/mylists/v1/lists/{list_id}/parts/{part_id}"
        headers = _get_headers(customer_id, use_user_token=True)

        return _make_request("GET", url, headers, use_user_token=True)

    @mcp.tool()
    def update_part_in_list(list_id: str, part_id: str, part_data: str, customer_id: str = "0"):
        """Update part information in a list.

        ⚠️ Requires user authentication via oauth_start_login()

        Args:
            list_id: The list ID
            part_id: The ID of the part to update
            part_data: JSON string with updated part data. Example:
                       '{"quantity": 20, "customerReference": "R1-Updated"}'
            customer_id: Customer ID (default: "0")

        Returns:
            Updated part information
        """
        _require_user_auth()
        url = f"{API_BASE}/mylists/v1/lists/{list_id}/parts/{part_id}"
        headers = _get_headers(customer_id, use_user_token=True)

        data = json.loads(part_data) if isinstance(part_data, str) else part_data

        return _make_request("PUT", url, headers, data, use_user_token=True)

    @mcp.tool()
    async def delete_part_from_list(list_id: str, part_id: str, customer_id: str = "0", ctx=None):
        """⚠️ DESTRUCTIVE: Permanently delete a part from a list.

        ⚠️ Requires user authentication via oauth_start_login()

        This operation cannot be undone. The part will be permanently removed from the list.

        This tool will prompt for user confirmation before proceeding.

        Args:
            list_id: The list ID
            part_id: The ID of the part to delete
            customer_id: Customer ID (default: "0")

        Returns:
            Deletion confirmation response
        """
        _require_user_auth()

        result = await ctx.elicit(
            f"⚠️ WARNING: You are about to permanently delete part ID {part_id} from list ID {list_id}. "
            "This action CANNOT be undone. Do you want to proceed?",
            response_type=None
        )

        if result.action != "accept":
            raise ValueError(f"Part deletion cancelled by user (action: {result.action})")

        url = f"{API_BASE}/mylists/v1/lists/{list_id}/parts/{part_id}"
        headers = _get_headers(customer_id, use_user_token=True)

        return _make_request("DELETE", url, headers, use_user_token=True)
