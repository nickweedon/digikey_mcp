"""MyLists API MCP Tools

Provides tools for interacting with the DigiKey MyLists API.
All tools require user authentication via OAuth 2.0.
"""
from typing import Optional, List, Dict, Any, Literal
from src.config import API_BASE
from src.api.client import _get_headers, _make_request
from src.api.auth import _require_user_auth


# Type aliases for clarity
ListId = str
PartId = str
CustomerId = str
ListSource = Literal["other", "internal", "external", "mobile", "search", "b2b"]


def _to_dict_excluding_none(data: Dict[str, Any]) -> Dict[str, Any]:
    """Helper to remove None values from a dictionary."""
    return {k: v for k, v in data.items() if v is not None}


class PartQuantity:
    """Quantity information for a part in a MyList.

    Attributes:
        selected_pack_type: Pack type selection index
        quantity: Quantity amount
        target_price: Target price per unit
    """
    def __init__(
        self,
        selected_pack_type: Optional[int] = None,
        quantity: Optional[int] = None,
        target_price: Optional[float] = None
    ):
        self.selected_pack_type = selected_pack_type
        self.quantity = quantity
        self.target_price = target_price

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API request format."""
        return _to_dict_excluding_none({
            "SelectedPackType": self.selected_pack_type,
            "Quantity": self.quantity,
            "TargetPrice": self.target_price
        })


class RequestedPart:
    """Part to add to a MyList.

    At minimum, provide one of: part_id, requested_part_number, or manufacturer_name.

    Attributes:
        part_id: DigiKey part ID
        requested_part_number: DigiKey part number (e.g., "296-8875-1-ND")
        manufacturer_name: Manufacturer name
        customer_reference: Your reference for this part
        reference_designator: Component reference designator (e.g., "R1", "C5")
        notes: Additional notes about this part
        selected_quantity_index: Index of selected quantity
        attrition: Attrition value
        quantities: List of quantity configurations
    """
    def __init__(
        self,
        part_id: Optional[str] = None,
        requested_part_number: Optional[str] = None,
        manufacturer_name: Optional[str] = None,
        customer_reference: Optional[str] = None,
        reference_designator: Optional[str] = None,
        notes: Optional[str] = None,
        selected_quantity_index: Optional[int] = None,
        attrition: Optional[int] = None,
        quantities: Optional[List[PartQuantity]] = None
    ):
        self.part_id = part_id
        self.requested_part_number = requested_part_number
        self.manufacturer_name = manufacturer_name
        self.customer_reference = customer_reference
        self.reference_designator = reference_designator
        self.notes = notes
        self.selected_quantity_index = selected_quantity_index
        self.attrition = attrition
        self.quantities = quantities

    def to_dict(self) -> Dict[str, Any]:
        """Convert to API request format."""
        result = _to_dict_excluding_none({
            "PartId": self.part_id,
            "RequestedPartNumber": self.requested_part_number,
            "ManufacturerName": self.manufacturer_name,
            "CustomerReference": self.customer_reference,
            "ReferenceDesignator": self.reference_designator,
            "Notes": self.notes,
            "SelectedQuantityIndex": self.selected_quantity_index,
            "Attrition": self.attrition
        })

        if self.quantities is not None:
            result["Quantities"] = [q.to_dict() for q in self.quantities]

        return result


def register_mylists_tools(mcp):
    """Register MyLists API MCP tools."""

    @mcp.tool()
    def get_all_lists(customer_id: CustomerId = "0") -> Dict[str, Any]:
        """Get all MyLists for the authenticated user.

        Retrieves a list of all lists created by or accessible to the authenticated user.
        Each list includes metadata such as list name, ID, creation date, and item counts.

        ⚠️ Requires user authentication via oauth_start_login()

        API Endpoint: GET /mylists/v1/lists

        Args:
            customer_id: DigiKey Customer ID. Use "0" for default account (default: "0")

        Returns:
            Array of list objects, each containing:
            - ListId: Unique identifier for the list
            - ListName: Name of the list
            - CreatedDate: ISO 8601 timestamp when the list was created
            - TotalParts: Number of parts in the list
            - Other list metadata

        Raises:
            ValueError: If user is not authenticated
            requests.HTTPError: If the API request fails
        """
        _require_user_auth()
        url = f"{API_BASE}/mylists/v1/lists"
        headers = _get_headers(customer_id, use_user_token=True)
        return _make_request("GET", url, headers, use_user_token=True)

    @mcp.tool()
    def create_list(
        list_name: str,
        tags: Optional[List[str]] = None,
        source: Optional[ListSource] = None,
        customer_id: CustomerId = "0"
    ) -> str:
        """Create a new MyList.

        Creates a new list with the specified name and optional metadata.
        Returns the ID of the newly created list.

        ⚠️ Requires user authentication via oauth_start_login()

        API Endpoint: POST /mylists/v1/lists

        Args:
            list_name: Name for the new list (required, minimum length: 1)
            tags: Optional list of tags to categorize the list
            source: Optional source identifier. One of:
                   "other", "internal", "external", "mobile", "search", "b2b"
            customer_id: DigiKey Customer ID (default: "0")

        Returns:
            String containing the unique list ID of the created list

        Raises:
            ValueError: If user is not authenticated or list_name is empty
            requests.HTTPError: If the API request fails (e.g., 400 for invalid input)

        Example:
            list_id = create_list("My Components", tags=["resistors", "capacitors"])
        """
        _require_user_auth()

        if not list_name or not list_name.strip():
            raise ValueError("list_name cannot be empty")

        url = f"{API_BASE}/mylists/v1/lists"
        headers = _get_headers(customer_id, use_user_token=True)

        body = _to_dict_excluding_none({
            "ListName": list_name,
            "Tags": tags,
            "Source": source
        })

        return _make_request("POST", url, headers, body, use_user_token=True)

    @mcp.tool()
    def get_list_by_id(
        list_id: ListId,
        include_parts: bool = False,
        customer_id: CustomerId = "0"
    ) -> Dict[str, Any]:
        """Get detailed information about a specific list.

        Retrieves comprehensive metadata and optionally all parts for a specified list.
        Use this when you need detailed list information or want to retrieve both
        list metadata and parts data in a single request.

        ⚠️ Requires user authentication via oauth_start_login()

        API Endpoint: GET /mylists/v1/lists/{listId}

        Args:
            list_id: The unique identifier of the list to retrieve
            include_parts: If True, includes full parts data in the response.
                          If False, returns only list metadata (default: False)
            customer_id: DigiKey Customer ID (default: "0")

        Returns:
            Dictionary containing:
            - ListId: Unique identifier
            - ListName: Name of the list
            - CreatedDate: Creation timestamp
            - ModifiedDate: Last modification timestamp
            - TotalParts: Number of parts in the list
            - PartsList: (only if include_parts=True) Array of part objects

        Raises:
            ValueError: If user is not authenticated
            requests.HTTPError: If the API request fails (e.g., 404 if list not found)
        """
        _require_user_auth()
        url = f"{API_BASE}/mylists/v1/lists/{list_id}"
        headers = _get_headers(customer_id, use_user_token=True)

        if include_parts:
            url += "?includePartsList=true"

        return _make_request("GET", url, headers, use_user_token=True)

    @mcp.tool()
    def update_list_name(
        list_id: ListId,
        new_name: str,
        customer_id: CustomerId = "0"
    ) -> None:
        """Update the name of an existing list.

        Renames a list to the specified new name. The operation succeeds silently
        with no return value (HTTP 204 No Content).

        ⚠️ Requires user authentication via oauth_start_login()

        API Endpoint: PUT /mylists/v1/lists/{listId}/listName/{listName}

        Args:
            list_id: The unique identifier of the list to rename
            new_name: The new name for the list (must not be empty)
            customer_id: DigiKey Customer ID (default: "0")

        Returns:
            None (HTTP 204 No Content on success)

        Raises:
            ValueError: If user is not authenticated or new_name is empty
            requests.HTTPError: If the API request fails (e.g., 404 if list not found)

        Example:
            update_list_name("abc123", "My Renamed List")
        """
        _require_user_auth()

        if not new_name or not new_name.strip():
            raise ValueError("new_name cannot be empty")

        # API expects both listId and listName in the path
        url = f"{API_BASE}/mylists/v1/lists/{list_id}/listName/{new_name}"
        headers = _get_headers(customer_id, use_user_token=True)

        return _make_request("PUT", url, headers, use_user_token=True)

    @mcp.tool()
    async def delete_list(
        list_id: ListId,
        customer_id: CustomerId = "0",
        ctx=None
    ) -> None:
        """⚠️ DESTRUCTIVE: Permanently delete a list and all its contents.

        Deletes the specified list and all its parts, settings, and metadata.
        This operation is irreversible and will prompt for user confirmation.

        ⚠️ Requires user authentication via oauth_start_login()

        API Endpoint: DELETE /mylists/v1/lists/{listId}

        Args:
            list_id: The unique identifier of the list to delete
            customer_id: DigiKey Customer ID (default: "0")
            ctx: Context object (automatically provided by FastMCP)

        Returns:
            None (HTTP 204 No Content on success)

        Raises:
            ValueError: If user is not authenticated or cancels the deletion
            requests.HTTPError: If the API request fails (e.g., 404 if list not found)

        Note:
            This tool requires explicit user confirmation before deletion proceeds.
            The deletion cannot be undone once confirmed.
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
    def get_parts_by_list_id(
        list_id: ListId,
        start_index: Optional[int] = None,
        limit: Optional[int] = None,
        assemblies: Optional[int] = None,
        include_attrition: bool = False,
        customer_id: CustomerId = "0"
    ) -> Dict[str, Any]:
        """Get all parts from a specific list with optional pagination.

        Retrieves detailed information about all parts in a list, including pricing,
        availability, lead times, datasheets, and compliance data. Supports pagination
        for large lists.

        ⚠️ Requires user authentication via oauth_start_login()

        API Endpoint: GET /mylists/v1/lists/{listId}/parts

        Args:
            list_id: The unique identifier of the list
            start_index: Starting position for pagination (default: 0)
            limit: Maximum number of parts to return (default: 100, max varies by API)
            assemblies: Units per part, minimum 1 (default: 1)
            include_attrition: If True, includes attrition data in response (default: False)
            customer_id: DigiKey Customer ID (default: "0")

        Returns:
            Dictionary containing:
            - PartsList: Array of part objects with detailed information
            - TotalParts: Total number of parts in the list
            Each part includes: part number, pricing, availability, datasheets,
            quantities, lead times, RoHS status, and other metadata

        Raises:
            ValueError: If user is not authenticated
            requests.HTTPError: If the API request fails (e.g., 404 if list not found)

        Example:
            # Get first 50 parts from a list
            parts = get_parts_by_list_id("abc123", start_index=0, limit=50)
            print(f"Total parts: {parts['TotalParts']}")
            for part in parts['PartsList']:
                print(part['DigiKeyPartNumber'])
        """
        _require_user_auth()
        url = f"{API_BASE}/mylists/v1/lists/{list_id}/parts"
        headers = _get_headers(customer_id, use_user_token=True)

        params = []
        if start_index is not None:
            params.append(f"startIndex={start_index}")
        if limit is not None:
            params.append(f"limit={limit}")
        if assemblies is not None:
            params.append(f"assemblies={assemblies}")
        if include_attrition:
            params.append(f"includeAttrition=true")

        if params:
            url += "?" + "&".join(params)

        return _make_request("GET", url, headers, use_user_token=True)

    @mcp.tool()
    def add_parts_to_list(
        list_id: ListId,
        parts: List[Dict[str, Any]],
        index: int = 0,
        customer_id: CustomerId = "0"
    ) -> List[str]:
        """Add parts to a list.

        Adds one or more parts to the specified list at the given index position.
        Each part must have at least one identifier (part_id, requested_part_number,
        or manufacturer_name).

        ⚠️ Requires user authentication via oauth_start_login()

        API Endpoint: POST /mylists/v1/lists/{listId}/parts

        Args:
            list_id: The unique identifier of the list to add parts to
            parts: List of part objects to add. Each part should contain:
                   - part_id (optional): DigiKey part ID
                   - requested_part_number (optional): DigiKey part number (e.g., "296-8875-1-ND")
                   - manufacturer_name (optional): Manufacturer name
                   - customer_reference (optional): Your reference for this part
                   - reference_designator (optional): Reference designator (e.g., "R1", "C5")
                   - notes (optional): Additional notes
                   - selected_quantity_index (optional): Selected quantity index
                   - attrition (optional): Attrition value
                   - quantities (optional): List of quantity objects with:
                       - selected_pack_type (optional): Pack type
                       - quantity (optional): Quantity amount
                       - target_price (optional): Target price
            index: Position at which to insert the parts (default: 0)
            customer_id: DigiKey Customer ID (default: "0")

        Returns:
            Array of unique part identifiers for the added parts

        Raises:
            ValueError: If user is not authenticated
            requests.HTTPError: If the API request fails (e.g., 400 for invalid input)

        Example:
            part_ids = add_parts_to_list(
                "abc123",
                [
                    {
                        "requested_part_number": "296-8875-1-ND",
                        "customer_reference": "R1",
                        "quantities": [{"quantity": 10}]
                    },
                    {
                        "requested_part_number": "P5555-ND",
                        "reference_designator": "C1"
                    }
                ]
            )
        """
        _require_user_auth()
        url = f"{API_BASE}/mylists/v1/lists/{list_id}/parts"
        headers = _get_headers(customer_id, use_user_token=True)

        # Add index query parameter if specified
        if index != 0:
            url += f"?index={index}"

        # Convert parts to API format using RequestedPart dataclass
        parts_list = []
        for part_data in parts:
            # Handle PartQuantity objects if present
            quantities = None
            if "quantities" in part_data and part_data["quantities"]:
                quantities = [
                    PartQuantity(
                        selected_pack_type=q.get("selected_pack_type"),
                        quantity=q.get("quantity"),
                        target_price=q.get("target_price")
                    )
                    for q in part_data["quantities"]
                ]

            requested_part = RequestedPart(
                part_id=part_data.get("part_id"),
                requested_part_number=part_data.get("requested_part_number"),
                manufacturer_name=part_data.get("manufacturer_name"),
                customer_reference=part_data.get("customer_reference"),
                reference_designator=part_data.get("reference_designator"),
                notes=part_data.get("notes"),
                selected_quantity_index=part_data.get("selected_quantity_index"),
                attrition=part_data.get("attrition"),
                quantities=quantities
            )
            parts_list.append(requested_part.to_dict())

        # Send the array directly as the body (not wrapped in an object)
        return _make_request("POST", url, headers, parts_list, use_user_token=True)

    @mcp.tool()
    def get_part_from_list(
        list_id: ListId,
        part_id: PartId,
        customer_id: CustomerId = "0"
    ) -> Dict[str, Any]:
        """Get a specific part from a list by its unique part ID.

        Retrieves detailed information about a single part including pricing,
        availability, datasheets, specifications, and custom fields.

        ⚠️ Requires user authentication via oauth_start_login()

        API Endpoint: GET /mylists/v1/lists/{listId}/parts/{partId}

        Args:
            list_id: The unique identifier of the list
            part_id: The unique identifier of the part within the list
            customer_id: DigiKey Customer ID (default: "0")

        Returns:
            Dictionary containing detailed part information including:
            - DigiKeyPartNumber: The DigiKey part number
            - ManufacturerPartNumber: The manufacturer's part number
            - Pricing: Pricing tiers and availability
            - CustomerReference: Your custom reference
            - ReferenceDesignator: Component designator
            - Quantity information and other metadata

        Raises:
            ValueError: If user is not authenticated
            requests.HTTPError: If the API request fails (e.g., 404 if part not found)
        """
        _require_user_auth()
        url = f"{API_BASE}/mylists/v1/lists/{list_id}/parts/{part_id}"
        headers = _get_headers(customer_id, use_user_token=True)

        return _make_request("GET", url, headers, use_user_token=True)

    @mcp.tool()
    def update_part_in_list(
        list_id: ListId,
        part_id: PartId,
        part_data: Dict[str, Any],
        customer_id: CustomerId = "0"
    ) -> Dict[str, Any]:
        """Update part information in a list.

        Updates custom fields and quantities for an existing part in a list.
        You can update fields like customer_reference, reference_designator,
        notes, and quantity information.

        ⚠️ Requires user authentication via oauth_start_login()

        API Endpoint: PUT /mylists/v1/lists/{listId}/parts/{partId}

        Args:
            list_id: The unique identifier of the list
            part_id: The unique identifier of the part to update
            part_data: Dictionary with fields to update. Can include:
                      - customer_reference: Your custom reference
                      - reference_designator: Component designator (e.g., "R1")
                      - notes: Additional notes
                      - selected_quantity_index: Selected quantity index
                      - attrition: Attrition value
                      - quantities: Updated quantity information
            customer_id: DigiKey Customer ID (default: "0")

        Returns:
            Dictionary containing the updated part information

        Raises:
            ValueError: If user is not authenticated
            requests.HTTPError: If the API request fails (e.g., 404 if part not found)

        Example:
            updated = update_part_in_list(
                "abc123",
                "part456",
                {
                    "customer_reference": "R1-Updated",
                    "reference_designator": "R1",
                    "notes": "Changed to higher wattage"
                }
            )
        """
        _require_user_auth()
        url = f"{API_BASE}/mylists/v1/lists/{list_id}/parts/{part_id}"
        headers = _get_headers(customer_id, use_user_token=True)

        # Convert snake_case to PascalCase for API
        api_data = {}
        field_mapping = {
            "customer_reference": "CustomerReference",
            "reference_designator": "ReferenceDesignator",
            "notes": "Notes",
            "selected_quantity_index": "SelectedQuantityIndex",
            "attrition": "Attrition",
            "quantities": "Quantities"
        }

        for key, value in part_data.items():
            api_key = field_mapping.get(key, key)
            api_data[api_key] = value

        return _make_request("PUT", url, headers, api_data, use_user_token=True)

    @mcp.tool()
    async def delete_part_from_list(
        list_id: ListId,
        part_id: PartId,
        customer_id: CustomerId = "0",
        ctx=None
    ) -> None:
        """⚠️ DESTRUCTIVE: Permanently delete a part from a list.

        Removes the specified part from the list. This operation is irreversible
        and will prompt for user confirmation before proceeding.

        ⚠️ Requires user authentication via oauth_start_login()

        API Endpoint: DELETE /mylists/v1/lists/{listId}/parts/{partId}

        Args:
            list_id: The unique identifier of the list
            part_id: The unique identifier of the part to delete
            customer_id: DigiKey Customer ID (default: "0")
            ctx: Context object (automatically provided by FastMCP)

        Returns:
            None (HTTP 204 No Content on success)

        Raises:
            ValueError: If user is not authenticated or cancels the deletion
            requests.HTTPError: If the API request fails (e.g., 404 if part not found)

        Note:
            This tool requires explicit user confirmation before deletion proceeds.
            The deletion cannot be undone once confirmed.
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
