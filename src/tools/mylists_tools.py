"""MyLists API MCP Tools

Provides tools for interacting with the DigiKey MyLists API.
All tools require user authentication via OAuth 2.0.
"""
from typing import Optional, List, Dict, Any, Literal, Union
from dataclasses import dataclass
from src.config import API_BASE
from src.api.client import _get_headers, _make_request
from src.api.auth import _require_user_auth
from src.jmespath_extensions import search_with_custom_functions


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


# MyLists API Response Models - Dataclasses based on DigiKey API JSON schema
@dataclass
class SubPackOption:
    """Sub-package option for parts."""
    __root__: Optional[Any] = None


@dataclass
class PackOption:
    """Package option details for a part."""
    PartId: int
    DigiKeyPartNumber: str
    ManufacturerPartNumber: str
    Quantity: int
    PackType: str
    QuantityAvailable: int
    MinimumOrderQuantity: int
    CalculatedUnitPrice: float
    ExtendedPrice: float
    BreakPrice: float
    BreakQuantity: int
    IsUpsell: bool
    ValueAdditionalFee: float
    SubPackOptions: List[Optional[Any]]
    FormattedUnitPrice: str
    FormattedExtendedPrice: str


@dataclass
class Quantity:
    """Quantity information for a part in a list."""
    QuantityRequested: int
    CalculatedQuantity: int
    TargetPrice: float | None
    SelectedPackType: str
    SelectedSubPackType: str
    IsInactive: bool
    SelectedPackOptionIndex: int
    SelectedSubPackOptionIndex: int
    PackOptions: Optional[List[PackOption]] = None


@dataclass
class Flags:
    """Status flags for a part."""
    NonStock: bool
    IsNCNR: bool
    IsSDS: bool
    IsValueAdd: bool
    IsMatched: bool
    IsMarketPlace: bool
    BoNotAllowed: bool
    DisplayRegularLeadTime: bool
    DisplayCheckActiveLeadTime: bool
    MultipleCrefsForPart: bool
    MultiplePartsForCref: bool
    IsChecked: bool
    IsEditable: bool
    IsDeniedByCountry: bool
    IsDeniedByCurrency: bool
    IsDeniedByCustomerId: bool


@dataclass
class Substitute:
    """Substitute part information."""
    PartId: int
    DigiKeyPartNumber: str
    Manufacturer: str
    ManufacturerPartNumber: str
    Description: str
    PartDetailUrl: str
    SubstituteType: str
    MinimumOrderQuantity: int
    QuantityAvailable: str
    TariffStatus: str
    MasterPartId: int
    UnitPrice: str


@dataclass
class AlternatePart:
    """Alternate part information."""
    PartId: int
    DigiKeyPartNumber: str
    Manufacturer: str
    ManufacturerPartNumber: str
    Description: str
    PartDetailUrl: str
    SubstituteType: str
    MinimumOrderQuantity: int
    QuantityAvailable: str
    TariffStatus: str
    MasterPartId: int
    UnitPrice: str


@dataclass
class PartsAvailableForCrefItem:
    """Part available for customer reference."""
    ManufacturerPartnumber: str
    Manufacturer: str
    MinimumOrderQuantity: int
    Description: str
    QuantityAvailable: int


@dataclass
class Part:
    """Complete part information from a MyList."""
    PartId: int
    UniqueId: str
    CustomerReference: str
    ReferenceDesignator: str
    Notes: str
    MinOrderQty: int
    MaxOrderQty: int
    OriginalPartNumber: str
    RequestedPartNumber: str
    DigiKeyPartNumber: str
    ManufacturerPartNumber: str
    RequestedManufacturerName: str
    Manufacturer: str
    Description: str
    PartStatus: str
    PartStatusCode: str
    Availability: str | None
    TariffCode: str
    QuantityAvailable: int
    SelectedQuantityIndex: int
    Attrition: int | float
    Quantities: List[Quantity]
    VendorLeadWeeks: int
    PartDetailUrl: str
    PrimaryDatasheetUrl: str
    ImageUrl: str
    ThumbnailUrl: str
    MarketPlaceSupplierLink: str
    SupplierName: str
    Substitutes: Optional[List[Substitute]]
    AlternateParts: List[AlternatePart]
    Flags: Any
    ReachStatus: str
    RohsStatusMessage: str
    Eccn: str
    Htsus: str
    CountryOfOrigin: str
    EnvironmentalDocs: Dict[str, str]
    Category: str
    PartsAvailableForCref: List[PartsAvailableForCrefItem]
    CrefsAvailableForPart: List[str]


@dataclass
class PartsListResponse:
    """Response containing a list of parts."""
    PartsList: List[Part]
    TotalParts: int


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
            Dictionary with 'lists' key containing array of list objects, each with:
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
        result = _make_request("GET", url, headers, use_user_token=True)
        # Wrap list in dict for FastMCP compatibility (structured_content must be dict)
        if isinstance(result, list):
            return {"lists": result}
        return result

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
    def delete_list(
        list_id: ListId,
        customer_id: CustomerId = "0"
    ) -> None:
        """⚠️ DESTRUCTIVE: Permanently delete a list and all its contents.

        Deletes the specified list and all its parts, settings, and metadata.
        This operation is irreversible.

        ⚠️ Requires user authentication via oauth_start_login()

        API Endpoint: DELETE /mylists/v1/lists/{listId}

        Args:
            list_id: The unique identifier of the list to delete
            customer_id: DigiKey Customer ID (default: "0")

        Returns:
            None (HTTP 204 No Content on success)

        Raises:
            ValueError: If user is not authenticated
            requests.HTTPError: If the API request fails (e.g., 404 if list not found)

        Note:
            The deletion cannot be undone once confirmed.
        """
        _require_user_auth()

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
        customer_id: CustomerId = "0",
        jmespath_query: Optional[str] = None
    ) -> Union[PartsListResponse, Dict[str, Any]]:
        """Get all parts from a specific list with optional pagination.

        Retrieves detailed information about all parts in a list, including pricing,
        availability, lead times, datasheets, and compliance data. Supports pagination
        for large lists.

        Optional JMESPath filtering can be applied to shape the response. If omitted,
        a default query selects commonly used fields. Custom queries operate on the
        same response structure (use PartsList[] to access the parts array).

        ⚠️ Requires user authentication via oauth_start_login()

        API Endpoint: GET /mylists/v1/lists/{listId}/parts

        Args:
            list_id: The unique identifier of the list
            start_index: Starting position for pagination (default: 0)
            limit: Maximum number of parts to return (default: 100 if not specified, there is no upper limit)
            assemblies: Units per part, minimum 1 (default: 1)
            include_attrition: If True, includes attrition data in response
            customer_id: DigiKey Customer ID (default: "0")
            jmespath_query: Optional JMESPath expression to filter the response

        Returns:
            Dict with parts data filtered by JMESPath query. Response schema:
            {
              "TotalParts": int,
              "PartsList": [{
                "PartId": int,
                "UniqueId": str,
                "CustomerReference": str,
                "ReferenceDesignator": str,
                "Notes": str,
                "MinOrderQty": int,
                "MaxOrderQty": int,
                "OriginalPartNumber": str,
                "RequestedPartNumber": str,
                "DigiKeyPartNumber": str,
                "ManufacturerPartNumber": str,
                "RequestedManufacturerName": str,
                "Manufacturer": str,
                "Description": str,
                "PartStatus": str,
                "PartStatusCode": str,
                "Availability": str|null,
                "TariffCode": str,
                "QuantityAvailable": int,
                "SelectedQuantityIndex": int,
                "Attrition": int,
                "VendorLeadWeeks": int,
                "PartDetailUrl": str,
                "PrimaryDatasheetUrl": str,
                "ImageUrl": str,
                "ThumbnailUrl": str,
                "ReachStatus": str,
                "RohsStatusMessage": str,
                "Eccn": str,
                "Htsus": str,
                "CountryOfOrigin": str,
                "Category": str,
                "Quantities": [{
                  "QuantityRequested": int,
                  "CalculatedQuantity": int,
                  "TargetPrice": float|null,
                  "SelectedPackType": str,
                  "SelectedSubPackType": str,
                  "IsInactive": bool,
                  "SelectedPackOptionIndex": int,
                  "SelectedSubPackOptionIndex": int,
                  "PackOptions": [{
                    "PartId": int,
                    "DigiKeyPartNumber": str,
                    "ManufacturerPartNumber": str,
                    "Quantity": int,
                    "PackType": str,
                    "QuantityAvailable": int,
                    "MinimumOrderQuantity": int,
                    "CalculatedUnitPrice": float,
                    "ExtendedPrice": float,
                    "BreakPrice": float,
                    "BreakQuantity": int,
                    "IsUpsell": bool,
                    "FormattedUnitPrice": str,
                    "FormattedExtendedPrice": str
                  }]
                }],
                "Flags": {
                  "NonStock": bool,
                  "IsNCNR": bool,
                  "IsSDS": bool,
                  "IsValueAdd": bool,
                  "IsMatched": bool,
                  "IsMarketPlace": bool,
                  "BoNotAllowed": bool,
                  "IsEditable": bool
                },
                "Substitutes": [{
                  "PartId": int,
                  "DigiKeyPartNumber": str,
                  "Manufacturer": str,
                  "ManufacturerPartNumber": str,
                  "Description": str,
                  "SubstituteType": str,
                  "QuantityAvailable": str,
                  "UnitPrice": str
                }],
                "AlternateParts": []
              }]
            }

        Custom JMESPath Functions:
            The following custom functions are available for use in jmespath_query:

            - regex_replace(pattern, replacement, string): Performs regex find-and-replace
              Example: regex_replace(' ohm$', '', '100 ohm') → '100'
              Example: regex_replace('[^0-9.]', '', '4.7uF') → '4.7'

            - int(value): Converts string to integer, returns null on failure
              Example: int('100') → 100
              Example: int('invalid') → null

            - str(value): Converts any value to string
              Example: str(100) → '100'
              Example: str(null) → 'null'

            - nvl(value, default): Returns default if value is null (like Oracle NVL)
              Example: nvl(int(Field), 0) → 0 if Field is not a valid number
              Example: nvl(MissingField, 'N/A') → 'N/A'

            Combined usage for filtering by numeric values:
              PartsList[?int(regex_replace('[^0-9]', '', QuantityField)) >= 100]

            Using nvl() for safe defaults:
              PartsList[].{Part: DigiKeyPartNumber, Qty: nvl(int(RequestedQuantity), 0)}

        Raises:
            ValueError: If user is not authenticated
            requests.HTTPError: If the API request fails

        Example:
            # Default filtered fields (returns PartsList array)
            result = get_parts_by_list_id("abc123", start_index=0, limit=150)

            # Custom JMESPath to extract part IDs and pricing
            # Note: Always use PartsList[] to access the parts array in custom queries
            q = '{TotalParts: TotalParts, PartsList: PartsList[].{Id: PartId, Number: DigiKeyPartNumber, Prices: Quantities[].PackOptions[].{Unit: CalculatedUnitPrice, Ext: ExtendedPrice}}}'
            result = get_parts_by_list_id("abc123", start_index=0, limit=150, jmespath_query=q)

            # Clean and convert requested quantities
            q = 'PartsList[].{Part: DigiKeyPartNumber, Qty: int(regex_replace("[^0-9]", "", RequestedQuantity))}'
            result = get_parts_by_list_id("abc123", jmespath_query=q)
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
            params.append("includeAttrition=true")

        if params:
            url += "?" + "&".join(params)

        response = _make_request("GET", url, headers, use_user_token=True)

        # If a JMESPath query is provided or default selection should be applied,
        # return the filtered dict directly.
        default_query = (
            '{TotalParts: TotalParts, PartsList: PartsList[].{'
            'UniqueId: UniqueId,'
            'PartId: PartId,'
            'ManufacturerPartNumber: ManufacturerPartNumber,'
            'Manufacturer: Manufacturer,'
            'Description: Description,'
            'Availability: Availability,'
            'PartStatus: PartStatus,'
            'RequestedQuantity: Quantities[].QuantityRequested,'
            'PackQuantity: Quantities[].PackOptions[].Quantity,'
            'PackType: Quantities[].PackOptions[].PackType,'
            'DigiKeyPartNumber: DigiKeyPartNumber,'
            'UnitPrice: Quantities[].PackOptions[].CalculatedUnitPrice,'
            'ExtendedPrice: Quantities[].PackOptions[].ExtendedPrice,'
            'MinOrderQty: MinOrderQty,'
            'RequestedPartNumber: RequestedPartNumber,'
            'Htsus: Htsus,'
            'Notes: Notes,'
            'CountryOfOrigin: CountryOfOrigin,'
            'OriginalPartNumber: OriginalPartNumber,'
            'ImageUrl: ImageUrl}}'
        )

        query_to_use = jmespath_query or default_query
        try:
            filtered = search_with_custom_functions(query_to_use, response)
            if filtered is not None:
                return filtered
        except Exception:
            # Fall back to schema build with error metadata
            pass

        # Build dataclass response according to schema, preserving extra fields
        try:
            raw_parts = response.get("PartsList", [])
            total_parts = response.get("TotalParts", 0)

            parts_dc: List[Part] = []
            for p in raw_parts:
                # Quantities
                quantities_dc: List[Quantity] = []
                for q in p.get("Quantities", []):
                    pack_options_raw = q.get("PackOptions") or []
                    pack_options_dc = []
                    for po in pack_options_raw:
                        pack_options_dc.append(
                            PackOption(
                                PartId=int(po.get("PartId", 0)),
                                DigiKeyPartNumber=po.get("DigiKeyPartNumber", ""),
                                ManufacturerPartNumber=po.get("ManufacturerPartNumber", ""),
                                Quantity=int(po.get("Quantity", 0)),
                                PackType=po.get("PackType", ""),
                                QuantityAvailable=int(po.get("QuantityAvailable", 0)),
                                MinimumOrderQuantity=int(po.get("MinimumOrderQuantity", 0)),
                                CalculatedUnitPrice=float(po.get("CalculatedUnitPrice", 0.0)),
                                ExtendedPrice=float(po.get("ExtendedPrice", 0.0)),
                                BreakPrice=float(po.get("BreakPrice", 0.0)),
                                BreakQuantity=int(po.get("BreakQuantity", 0)),
                                IsUpsell=bool(po.get("IsUpsell", False)),
                                ValueAdditionalFee=float(po.get("ValueAdditionalFee", 0.0)),
                                SubPackOptions=po.get("SubPackOptions", []) or [],
                                FormattedUnitPrice=po.get("FormattedUnitPrice", ""),
                                FormattedExtendedPrice=po.get("FormattedExtendedPrice", ""),
                            )
                        )

                    quantities_dc.append(
                        Quantity(
                            QuantityRequested=int(q.get("QuantityRequested", 0)),
                            CalculatedQuantity=int(q.get("CalculatedQuantity", 0)),
                            TargetPrice=(q.get("TargetPrice") if q.get("TargetPrice") is not None else None),
                            SelectedPackType=q.get("SelectedPackType", ""),
                            SelectedSubPackType=q.get("SelectedSubPackType", ""),
                            IsInactive=bool(q.get("IsInactive", False)),
                            SelectedPackOptionIndex=int(q.get("SelectedPackOptionIndex", 0)),
                            SelectedSubPackOptionIndex=int(q.get("SelectedSubPackOptionIndex", 0)),
                            PackOptions=pack_options_dc or None,
                        )
                    )

                flags_raw = p.get("Flags", {})
                flags_dc = Flags(
                    NonStock=bool(flags_raw.get("NonStock", False)),
                    IsNCNR=bool(flags_raw.get("IsNCNR", False)),
                    IsSDS=bool(flags_raw.get("IsSDS", False)),
                    IsValueAdd=bool(flags_raw.get("IsValueAdd", False)),
                    IsMatched=bool(flags_raw.get("IsMatched", False)),
                    IsMarketPlace=bool(flags_raw.get("IsMarketPlace", False)),
                    BoNotAllowed=bool(flags_raw.get("BoNotAllowed", False)),
                    DisplayRegularLeadTime=bool(flags_raw.get("DisplayRegularLeadTime", False)),
                    DisplayCheckActiveLeadTime=bool(flags_raw.get("DisplayCheckActiveLeadTime", False)),
                    MultipleCrefsForPart=bool(flags_raw.get("MultipleCrefsForPart", False)),
                    MultiplePartsForCref=bool(flags_raw.get("MultiplePartsForCref", False)),
                    IsChecked=bool(flags_raw.get("IsChecked", False)),
                    IsEditable=bool(flags_raw.get("IsEditable", False)),
                    IsDeniedByCountry=bool(flags_raw.get("IsDeniedByCountry", False)),
                    IsDeniedByCurrency=bool(flags_raw.get("IsDeniedByCurrency", False)),
                    IsDeniedByCustomerId=bool(flags_raw.get("IsDeniedByCustomerId", False)),
                )

                # Substitutes
                subs_raw = p.get("Substitutes") or []
                substitutes_dc = []
                for s in subs_raw:
                    substitutes_dc.append(
                        Substitute(
                            PartId=int(s.get("PartId", 0)),
                            DigiKeyPartNumber=s.get("DigiKeyPartNumber", ""),
                            Manufacturer=s.get("Manufacturer", ""),
                            ManufacturerPartNumber=s.get("ManufacturerPartNumber", ""),
                            Description=s.get("Description", ""),
                            PartDetailUrl=s.get("PartDetailUrl", ""),
                            SubstituteType=s.get("SubstituteType", ""),
                            MinimumOrderQuantity=int(s.get("MinimumOrderQuantity", 0)),
                            QuantityAvailable=str(s.get("QuantityAvailable", "")),
                            TariffStatus=s.get("TariffStatus", ""),
                            MasterPartId=int(s.get("MasterPartId", 0)),
                            UnitPrice=s.get("UnitPrice", ""),
                        )
                    )

                # AlternateParts
                alt_raw = p.get("AlternateParts") or []
                alt_dc = []
                for a in alt_raw:
                    alt_dc.append(
                        AlternatePart(
                            PartId=int(a.get("PartId", 0)),
                            DigiKeyPartNumber=a.get("DigiKeyPartNumber", ""),
                            Manufacturer=a.get("Manufacturer", ""),
                            ManufacturerPartNumber=a.get("ManufacturerPartNumber", ""),
                            Description=a.get("Description", ""),
                            PartDetailUrl=a.get("PartDetailUrl", ""),
                            SubstituteType=a.get("SubstituteType", ""),
                            MinimumOrderQuantity=int(a.get("MinimumOrderQuantity", 0)),
                            QuantityAvailable=str(a.get("QuantityAvailable", "")),
                            TariffStatus=a.get("TariffStatus", ""),
                            MasterPartId=int(a.get("MasterPartId", 0)),
                            UnitPrice=a.get("UnitPrice", ""),
                        )
                    )

                # PartsAvailableForCref
                pac_raw = p.get("PartsAvailableForCref") or []
                pac_dc = []
                for item in pac_raw:
                    pac_dc.append(
                        PartsAvailableForCrefItem(
                            ManufacturerPartnumber=item.get("ManufacturerPartnumber", ""),
                            Manufacturer=item.get("Manufacturer", ""),
                            MinimumOrderQuantity=int(item.get("MinimumOrderQuantity", 0)),
                            Description=item.get("Description", ""),
                            QuantityAvailable=int(item.get("QuantityAvailable", 0)),
                        )
                    )

                parts_dc.append(
                    Part(
                        PartId=int(p.get("PartId", 0)),
                        UniqueId=p.get("UniqueId", ""),
                        CustomerReference=p.get("CustomerReference", ""),
                        ReferenceDesignator=p.get("ReferenceDesignator", ""),
                        Notes=p.get("Notes", ""),
                        MinOrderQty=int(p.get("MinOrderQty", 0)),
                        MaxOrderQty=int(p.get("MaxOrderQty", 0)),
                        OriginalPartNumber=p.get("OriginalPartNumber", ""),
                        RequestedPartNumber=p.get("RequestedPartNumber", ""),
                        DigiKeyPartNumber=p.get("DigiKeyPartNumber", ""),
                        ManufacturerPartNumber=p.get("ManufacturerPartNumber", ""),
                        RequestedManufacturerName=p.get("RequestedManufacturerName", ""),
                        Manufacturer=p.get("Manufacturer", ""),
                        Description=p.get("Description", ""),
                        PartStatus=p.get("PartStatus", ""),
                        PartStatusCode=str(p.get("PartStatusCode", "")),
                        Availability=p.get("Availability"),
                        TariffCode=str(p.get("TariffCode", "")),
                        QuantityAvailable=int(p.get("QuantityAvailable", 0)),
                        SelectedQuantityIndex=int(p.get("SelectedQuantityIndex", 0)),
                        Attrition=int(p.get("Attrition", 0)),
                        Quantities=quantities_dc,
                        VendorLeadWeeks=int(p.get("VendorLeadWeeks", 0)),
                        PartDetailUrl=p.get("PartDetailUrl", ""),
                        PrimaryDatasheetUrl=p.get("PrimaryDatasheetUrl", ""),
                        ImageUrl=p.get("ImageUrl", ""),
                        ThumbnailUrl=p.get("ThumbnailUrl", ""),
                        MarketPlaceSupplierLink=p.get("MarketPlaceSupplierLink", ""),
                        SupplierName=p.get("SupplierName", ""),
                        Substitutes=substitutes_dc or None,
                        AlternateParts=alt_dc,
                        Flags=flags_dc,
                        ReachStatus=p.get("ReachStatus", ""),
                        RohsStatusMessage=p.get("RohsStatusMessage", ""),
                        Eccn=p.get("Eccn", ""),
                        Htsus=p.get("Htsus", ""),
                        CountryOfOrigin=p.get("CountryOfOrigin", ""),
                        EnvironmentalDocs=p.get("EnvironmentalDocs", {}) or {},
                        Category=p.get("Category", ""),
                        PartsAvailableForCref=pac_dc,
                        CrefsAvailableForPart=[str(x) for x in (p.get("CrefsAvailableForPart", []) or [])],
                    )
                )

            result_dc = PartsListResponse(PartsList=parts_dc, TotalParts=int(total_parts))
            return result_dc
        except Exception as e:
            return {
                "error": {
                    "type": "PartsListSchemaBuildError",
                    "code": "SCHEMA_BUILD_FAILED",
                    "message": str(e),
                    "listId": list_id,
                    "originalResponse": response
                }
            }

    @mcp.tool()
    def add_parts_to_list(
        list_id: ListId,
        parts: List[Dict[str, Any]],
        index: int = 0,
        customer_id: CustomerId = "0"
    ) -> Dict[str, Any]:
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
            Dictionary with 'part_ids' key containing array of unique part identifiers
            for the added parts

        Raises:
            ValueError: If user is not authenticated
            requests.HTTPError: If the API request fails (e.g., 400 for invalid input)

        Example:
            result = add_parts_to_list(
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
            part_ids = result["part_ids"]
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
        result = _make_request("POST", url, headers, parts_list, use_user_token=True)
        # Wrap list in dict for FastMCP compatibility (structured_content must be dict)
        if isinstance(result, list):
            return {"part_ids": result}
        return result

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
            part_id: The UniqueId of the part (string) from get_parts_by_list_id().
                    This is the Part.UniqueId field, NOT the Part.PartId field.
                    Example: "abc123def456" (string), not 1942531 (integer)
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
            part_id: The UniqueId of the part (string) from get_parts_by_list_id().
                    This is the Part.UniqueId field, NOT the Part.PartId field.
                    Example: "abc123def456" (string), not 1942531 (integer)
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
    def delete_part_from_list(
        list_id: ListId,
        part_id: PartId,
        customer_id: CustomerId = "0"
    ) -> None:
        """⚠️ DESTRUCTIVE: Permanently delete a part from a list.

        Removes the specified part from the list. This operation is irreversible.

        ⚠️ Requires user authentication via oauth_start_login()

        API Endpoint: DELETE /mylists/v1/lists/{listId}/parts/{partId}

        Args:
            list_id: The unique identifier of the list
            part_id: The UniqueId of the part (string) from get_parts_by_list_id().
                    This is the Part.UniqueId field, NOT the Part.PartId field.
                    Example: "abc123def456" (string), not 1942531 (integer)
            customer_id: DigiKey Customer ID (default: "0")

        Returns:
            None (HTTP 204 No Content on success)

        Raises:
            ValueError: If user is not authenticated
            requests.HTTPError: If the API request fails (e.g., 404 if part not found)

        Note:
            The deletion cannot be undone once confirmed.
        """
        _require_user_auth()

        url = f"{API_BASE}/mylists/v1/lists/{list_id}/parts/{part_id}"
        headers = _get_headers(customer_id, use_user_token=True)

        return _make_request("DELETE", url, headers, use_user_token=True)
