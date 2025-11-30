"""Product Search API MCP Tools"""
from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass
import jmespath
from src.config import API_BASE
from src.api.client import _get_headers, _make_request


# Product Search Response Models - Dataclasses based on DigiKey API JSON schema
@dataclass
class Manufacturer:
    """Manufacturer information."""
    Id: int
    Name: str


@dataclass
class Description:
    """Product description."""
    ProductDescription: str
    DetailedDescription: Optional[str] = None


@dataclass
class ProductStatus:
    """Product status information."""
    Id: int
    Status: str


@dataclass
class PackageType:
    """Package type information."""
    Id: int
    Name: str


@dataclass
class Supplier:
    """Supplier information."""
    Id: int
    Name: str


@dataclass
class PricingTier:
    """Pricing tier information."""
    BreakQuantity: int
    UnitPrice: float
    TotalPrice: float


@dataclass
class ProductVariation:
    """Product variation with packaging and pricing."""
    DigiKeyProductNumber: str
    PackageType: PackageType
    StandardPricing: List[PricingTier]
    MyPricing: List[PricingTier]
    MarketPlace: bool
    QuantityAvailableforPackageType: int
    MinimumOrderQuantity: int
    StandardPackage: int
    Supplier: Optional[Supplier] = None
    TariffActive: Optional[bool] = None
    MaxQuantityForDistribution: Optional[int] = None
    DigiReelFee: Optional[float] = None


@dataclass
class CategoryNode:
    """Category information."""
    CategoryId: int
    ParentId: int
    Name: str
    ProductCount: int
    NewProductCount: int
    ImageUrl: Optional[str] = None


@dataclass
class ParameterValue:
    """Product parameter value."""
    ParameterId: int
    ParameterText: str
    ParameterType: str
    ValueId: str
    ValueText: str


@dataclass
class Product:
    """Complete product information from keyword search."""
    Description: Description
    Manufacturer: Manufacturer
    ManufacturerProductNumber: str
    UnitPrice: float
    ProductUrl: str
    ProductVariations: List[ProductVariation]
    QuantityAvailable: int
    ProductStatus: ProductStatus
    BackOrderNotAllowed: bool
    NormallyStocking: bool
    Discontinued: bool
    EndOfLife: bool
    Ncnr: bool
    DatasheetUrl: Optional[str] = None
    PhotoUrl: Optional[str] = None
    PrimaryVideoUrl: Optional[str] = None
    Parameters: Optional[List[ParameterValue]] = None
    Category: Optional[CategoryNode] = None
    BaseProductNumber: Optional[str] = None
    DateLastBuyChance: Optional[str] = None
    ManufacturerLeadWeeks: Optional[str] = None
    ManufacturerPublicQuantity: Optional[int] = None


@dataclass
class KeywordSearchResponse:
    """Response from keyword search."""
    Products: List[Product]
    ProductsCount: int
    ExactMatches: Optional[List[Product]] = None
    FilterOptions: Optional[Dict[str, Any]] = None
    SearchLocaleUsed: Optional[Dict[str, Any]] = None
    AppliedParametricFiltersDto: Optional[List[Dict[str, Any]]] = None


@dataclass
class ManufacturersResponse:
    """Response from manufacturers search."""
    Manufacturers: List[Manufacturer]
    ManufacturersCount: int


@dataclass
class CategoriesResponse:
    """Response from categories search."""
    Categories: List[CategoryNode]
    CategoriesCount: int


@dataclass
class MediaLink:
    """Media link for a product."""
    MediaType: str
    Title: str
    Url: str
    SmallPhoto: Optional[str] = None
    Thumbnail: Optional[str] = None


@dataclass
class MediaResponse:
    """Response from product media request."""
    MediaLinks: List[MediaLink]
    DigiKeyPartNumber: Optional[str] = None


@dataclass
class ProductPricingResponse:
    """Response from product pricing request."""
    DigiKeyPartNumber: str
    ManufacturerPartNumber: str
    QuantityAvailable: int
    StandardPricing: List[PricingTier]
    RequestedQuantity: int
    CalculatedPrice: float
    ExtendedPrice: float
    ProductUrl: Optional[str] = None
    MinimumOrderQuantity: Optional[int] = None
    StandardPackage: Optional[int] = None
    MyPricing: Optional[List[PricingTier]] = None


@dataclass
class DigiReelPricingResponse:
    """Response from DigiReel pricing request."""
    DigiKeyPartNumber: str
    ManufacturerPartNumber: str
    RequestedQuantity: int
    DigiReelFee: float
    UnitPrice: float
    ExtendedPrice: float
    TotalPrice: float
    QuantityAvailable: int
    MinimumOrderQuantity: Optional[int] = None


@dataclass
class SubstitutionsResponse:
    """Response from product substitutions search."""
    Products: List[Product]
    ProductsCount: int
    RequestedProductNumber: Optional[str] = None


@dataclass
class ProductDetailsResponse:
    """Response from product details request."""
    DigiKeyPartNumber: str
    ManufacturerPartNumber: str
    Manufacturer: Manufacturer
    Description: Description
    ProductUrl: str
    UnitPrice: float
    QuantityAvailable: int
    ProductStatus: ProductStatus
    StandardPricing: List[PricingTier]
    BackOrderNotAllowed: bool
    NormallyStocking: bool
    Discontinued: bool
    EndOfLife: bool
    Ncnr: bool
    DatasheetUrl: Optional[str] = None
    PhotoUrl: Optional[str] = None
    MinimumOrderQuantity: Optional[int] = None
    StandardPackage: Optional[int] = None
    Category: Optional[CategoryNode] = None
    Parameters: Optional[List[ParameterValue]] = None
    ReachStatus: Optional[str] = None
    RohsStatus: Optional[str] = None
    LeadStatus: Optional[str] = None
    HtsusCode: Optional[str] = None
    TariffDescription: Optional[str] = None
    Eccn: Optional[str] = None


def register_product_tools(mcp):
    """Register Product Search API MCP tools."""

    @mcp.tool()
    def keyword_search(
        keywords: str,
        limit: int = 5,
        manufacturer_id: str = None,
        category_id: str = None,
        search_options: str = None,
        sort_field: str = None,
        sort_order: str = "Ascending",
        jmespath_query: Optional[str] = None
    ) -> Union[KeywordSearchResponse, Dict[str, Any]]:
        """Search DigiKey products by keyword.

        Retrieves product information based on keyword search with optional filtering.
        Supports pagination, manufacturer/category filtering, and custom result shaping
        via JMESPath queries.

        Optional JMESPath filtering can be applied to pre-shape the response. When
        `jmespath_query` is provided, the function returns a filtered JSON (dict)
        according to the JMESPath expression. If not provided, a sensible default
        query is used that selects commonly needed fields.

        Args:
            keywords: Search terms or part numbers
            limit: Maximum number of results (default: 5)
            manufacturer_id: Filter by specific manufacturer ID
            category_id: Filter by specific category ID
            search_options: Comma-delimited filters like LeadFree,RoHSCompliant,InStock
            sort_field: Field to sort by. Options: None, Packaging, ProductStatus,
                       DigiKeyProductNumber, ManufacturerProductNumber, Manufacturer,
                       MinimumQuantity, QuantityAvailable, Price, Supplier,
                       PriceManufacturerStandardPackage
            sort_order: Sort direction - Ascending or Descending (default: Ascending)
            jmespath_query: Optional JMESPath expression to pre-filter and shape the
                           response. If omitted, a default query returns only commonly
                           used fields.

        Returns:
            Dict with product data filtered by JMESPath query. Response schema:
            {
              "ProductsCount": int,
              "Products": [{
                "ManufacturerProductNumber": str,
                "UnitPrice": float,
                "QuantityAvailable": int,
                "ProductUrl": str,
                "DatasheetUrl": str|null,
                "PhotoUrl": str|null,
                "BackOrderNotAllowed": bool,
                "NormallyStocking": bool,
                "Discontinued": bool,
                "EndOfLife": bool,
                "Ncnr": bool,
                "Description": {
                  "ProductDescription": str,
                  "DetailedDescription": str|null
                },
                "Manufacturer": {
                  "Id": int,
                  "Name": str
                },
                "ProductStatus": {
                  "Id": int,
                  "Status": str
                },
                "ProductVariations": [{
                  "DigiKeyProductNumber": str,
                  "MinimumOrderQuantity": int,
                  "StandardPackage": int,
                  "QuantityAvailableforPackageType": int,
                  "MarketPlace": bool,
                  "DigiReelFee": float|null,
                  "PackageType": {"Id": int, "Name": str},
                  "StandardPricing": [{"BreakQuantity": int, "UnitPrice": float, "TotalPrice": float}],
                  "MyPricing": [{"BreakQuantity": int, "UnitPrice": float, "TotalPrice": float}]
                }],
                "Category": {"CategoryId": int, "Name": str, "ParentId": int}|null,
                "Parameters": [{"ParameterId": int, "ParameterText": str, "ValueText": str}]|null
              }]
            }

        Example:
            # Default filtered fields
            result = keyword_search("arduino", limit=5)

            # Custom JMESPath to extract specific fields
            q = '{Count: ProductsCount, Parts: Products[].{PN: ManufacturerProductNumber, Price: UnitPrice, Stock: QuantityAvailable}}'
            result = keyword_search("arduino", limit=5, jmespath_query=q)

            # Get only in-stock products with pricing
            q = '{Products: Products[?QuantityAvailable > `0`].{PN: ManufacturerProductNumber, Price: UnitPrice}}'
            result = keyword_search("capacitor", limit=10, jmespath_query=q)
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

        response = _make_request("POST", url, headers, body, use_user_token=False)

        # Default JMESPath query that extracts commonly used fields
        default_query = (
            '{ProductsCount: ProductsCount, Products: Products[].{'
            'DigiKeyPartNumber: ProductVariations[0].DigiKeyProductNumber,'
            'ManufacturerPartNumber: ManufacturerProductNumber,'
            'Manufacturer: Manufacturer.Name,'
            'Description: Description.ProductDescription,'
            'UnitPrice: UnitPrice,'
            'QuantityAvailable: QuantityAvailable,'
            'MinimumOrderQuantity: ProductVariations[0].MinimumOrderQuantity,'
            'ProductStatus: ProductStatus.Status,'
            'ProductUrl: ProductUrl,'
            'DatasheetUrl: DatasheetUrl,'
            'PhotoUrl: PhotoUrl,'
            'InStock: (QuantityAvailable > `0`),'
            'Pricing: ProductVariations[0].StandardPricing}}'
        )

        # Apply JMESPath query if provided or use default
        query_to_use = jmespath_query or default_query
        try:
            filtered = jmespath.search(query_to_use, response)
            if filtered is not None:
                return filtered
        except Exception:
            # Fall back to schema build with error metadata
            pass

        # Build dataclass response according to schema, preserving extra fields
        try:
            raw_products = response.get("Products", [])
            products_count = response.get("ProductsCount", 0)

            products_dc: List[Product] = []
            for p in raw_products:
                # Build Description
                desc_raw = p.get("Description", {})
                description = Description(
                    ProductDescription=desc_raw.get("ProductDescription", ""),
                    DetailedDescription=desc_raw.get("DetailedDescription")
                )

                # Build Manufacturer
                mfr_raw = p.get("Manufacturer", {})
                manufacturer = Manufacturer(
                    Id=int(mfr_raw.get("Id", 0)),
                    Name=mfr_raw.get("Name", "")
                )

                # Build ProductStatus
                status_raw = p.get("ProductStatus", {})
                product_status = ProductStatus(
                    Id=int(status_raw.get("Id", 0)),
                    Status=status_raw.get("Status", "")
                )

                # Build ProductVariations
                variations_raw = p.get("ProductVariations", [])
                variations_dc = []
                for v in variations_raw:
                    # Build PackageType
                    pkg_raw = v.get("PackageType", {})
                    package_type = PackageType(
                        Id=int(pkg_raw.get("Id", 0)),
                        Name=pkg_raw.get("Name", "")
                    )

                    # Build Supplier (optional)
                    supplier = None
                    supplier_raw = v.get("Supplier")
                    if supplier_raw:
                        supplier = Supplier(
                            Id=int(supplier_raw.get("Id", 0)),
                            Name=supplier_raw.get("Name", "")
                        )

                    # Build StandardPricing
                    std_pricing_raw = v.get("StandardPricing", [])
                    std_pricing_dc = []
                    for tier in std_pricing_raw:
                        std_pricing_dc.append(
                            PricingTier(
                                BreakQuantity=int(tier.get("BreakQuantity", 0)),
                                UnitPrice=float(tier.get("UnitPrice", 0.0)),
                                TotalPrice=float(tier.get("TotalPrice", 0.0))
                            )
                        )

                    # Build MyPricing
                    my_pricing_raw = v.get("MyPricing", [])
                    my_pricing_dc = []
                    for tier in my_pricing_raw:
                        my_pricing_dc.append(
                            PricingTier(
                                BreakQuantity=int(tier.get("BreakQuantity", 0)),
                                UnitPrice=float(tier.get("UnitPrice", 0.0)),
                                TotalPrice=float(tier.get("TotalPrice", 0.0))
                            )
                        )

                    variations_dc.append(
                        ProductVariation(
                            DigiKeyProductNumber=v.get("DigiKeyProductNumber", ""),
                            PackageType=package_type,
                            StandardPricing=std_pricing_dc,
                            MyPricing=my_pricing_dc,
                            MarketPlace=bool(v.get("MarketPlace", False)),
                            QuantityAvailableforPackageType=int(v.get("QuantityAvailableforPackageType", 0)),
                            MinimumOrderQuantity=int(v.get("MinimumOrderQuantity", 0)),
                            StandardPackage=int(v.get("StandardPackage", 0)),
                            Supplier=supplier,
                            TariffActive=v.get("TariffActive"),
                            MaxQuantityForDistribution=v.get("MaxQuantityForDistribution"),
                            DigiReelFee=v.get("DigiReelFee")
                        )
                    )

                # Build Parameters (optional)
                params_raw = p.get("Parameters")
                parameters = None
                if params_raw:
                    parameters = []
                    for param in params_raw:
                        parameters.append(
                            ParameterValue(
                                ParameterId=int(param.get("ParameterId", 0)),
                                ParameterText=param.get("ParameterText", ""),
                                ParameterType=param.get("ParameterType", ""),
                                ValueId=str(param.get("ValueId", "")),
                                ValueText=param.get("ValueText", "")
                            )
                        )

                # Build Category (optional)
                category = None
                cat_raw = p.get("Category")
                if cat_raw:
                    category = CategoryNode(
                        CategoryId=int(cat_raw.get("CategoryId", 0)),
                        ParentId=int(cat_raw.get("ParentId", 0)),
                        Name=cat_raw.get("Name", ""),
                        ProductCount=int(cat_raw.get("ProductCount", 0)),
                        NewProductCount=int(cat_raw.get("NewProductCount", 0)),
                        ImageUrl=cat_raw.get("ImageUrl")
                    )

                products_dc.append(
                    Product(
                        Description=description,
                        Manufacturer=manufacturer,
                        ManufacturerProductNumber=p.get("ManufacturerProductNumber", ""),
                        UnitPrice=float(p.get("UnitPrice", 0.0)),
                        ProductUrl=p.get("ProductUrl", ""),
                        ProductVariations=variations_dc,
                        QuantityAvailable=int(p.get("QuantityAvailable", 0)),
                        ProductStatus=product_status,
                        BackOrderNotAllowed=bool(p.get("BackOrderNotAllowed", False)),
                        NormallyStocking=bool(p.get("NormallyStocking", False)),
                        Discontinued=bool(p.get("Discontinued", False)),
                        EndOfLife=bool(p.get("EndOfLife", False)),
                        Ncnr=bool(p.get("Ncnr", False)),
                        DatasheetUrl=p.get("DatasheetUrl"),
                        PhotoUrl=p.get("PhotoUrl"),
                        PrimaryVideoUrl=p.get("PrimaryVideoUrl"),
                        Parameters=parameters,
                        Category=category,
                        BaseProductNumber=p.get("BaseProductNumber"),
                        DateLastBuyChance=p.get("DateLastBuyChance"),
                        ManufacturerLeadWeeks=p.get("ManufacturerLeadWeeks"),
                        ManufacturerPublicQuantity=p.get("ManufacturerPublicQuantity")
                    )
                )

            result_dc = KeywordSearchResponse(
                Products=products_dc,
                ProductsCount=products_count,
                ExactMatches=None,  # TODO: Parse if needed
                FilterOptions=response.get("FilterOptions"),
                SearchLocaleUsed=response.get("SearchLocaleUsed"),
                AppliedParametricFiltersDto=response.get("AppliedParametricFiltersDto")
            )
            return result_dc

        except Exception as e:
            return {
                "error": {
                    "type": "KeywordSearchSchemaBuildError",
                    "code": "SCHEMA_BUILD_FAILED",
                    "message": str(e),
                    "keywords": keywords,
                    "originalResponse": response
                }
            }

    @mcp.tool()
    def product_details(
        product_number: str,
        manufacturer_id: str = None,
        customer_id: str = "0"
    ) -> Union[ProductDetailsResponse, Dict[str, Any]]:
        """Get detailed information for a specific product.

        Args:
            product_number: DigiKey or manufacturer part number
            manufacturer_id: Optional manufacturer ID for disambiguation
            customer_id: Customer ID for pricing (default: "0")

        Returns:
            ProductDetailsResponse with complete product details including pricing,
            availability, specifications, and compliance information.
        """
        url = f"{API_BASE}/products/v4/search/{product_number}/productdetails"
        headers = _get_headers(customer_id)

        params = {}
        if manufacturer_id:
            params["manufacturerId"] = manufacturer_id

        if params:
            url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

        return _make_request("GET", url, headers, use_user_token=False)

    @mcp.tool()
    def search_manufacturers() -> Union[ManufacturersResponse, Dict[str, Any]]:
        """Search and retrieve all product manufacturers.

        Returns:
            ManufacturersResponse containing list of all manufacturers with their
            IDs and names, plus total count.
        """
        url = f"{API_BASE}/products/v4/search/manufacturers"
        headers = _get_headers()
        return _make_request("GET", url, headers, use_user_token=False)

    @mcp.tool()
    def search_categories() -> Union[CategoriesResponse, Dict[str, Any]]:
        """Search and retrieve all product categories.

        Returns:
            CategoriesResponse containing hierarchical category tree with IDs,
            names, product counts, and child categories.
        """
        url = f"{API_BASE}/products/v4/search/categories"
        headers = _get_headers()
        return _make_request("GET", url, headers, use_user_token=False)

    @mcp.tool()
    def get_category_by_id(category_id: str) -> Union[CategoryNode, Dict[str, Any]]:
        """Get specific category details by ID.

        Args:
            category_id: The category ID to retrieve

        Returns:
            CategoryNode with category details including ID, name, parent,
            product counts, and child categories.
        """
        url = f"{API_BASE}/products/v4/search/categories/{category_id}"
        headers = _get_headers()
        return _make_request("GET", url, headers, use_user_token=False)

    @mcp.tool()
    def search_product_substitutions(
        product_number: str,
        limit: int = 10,
        search_options: str = None,
        exclude_marketplace: bool = False
    ) -> Union[SubstitutionsResponse, Dict[str, Any]]:
        """Search for product substitutions for a given product.

        Args:
            product_number: The product to get substitutions for
            limit: Number of substitutions (default: 10)
            search_options: Filters like LeadFree,RoHSCompliant,InStock
            exclude_marketplace: Exclude marketplace products (default: False)

        Returns:
            SubstitutionsResponse with list of substitute products that can
            replace the specified product.
        """
        url = f"{API_BASE}/products/v4/search/{product_number}/substitutions"
        headers = _get_headers()

        params = {"limit": limit, "excludeMarketPlaceProducts": exclude_marketplace}
        if search_options:
            params["searchOptionList"] = search_options

        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])
        return _make_request("GET", url, headers, use_user_token=False)

    @mcp.tool()
    def get_product_media(product_number: str) -> Union[MediaResponse, Dict[str, Any]]:
        """Get media (images, documents, videos) for a product.

        Args:
            product_number: The product to get media for

        Returns:
            MediaResponse containing list of media links including product photos,
            datasheets, and other documentation.
        """
        url = f"{API_BASE}/products/v4/search/{product_number}/media"
        headers = _get_headers()
        return _make_request("GET", url, headers, use_user_token=False)

    @mcp.tool()
    def get_product_pricing(
        product_number: str,
        customer_id: str = "0",
        requested_quantity: int = 1
    ) -> Union[ProductPricingResponse, Dict[str, Any]]:
        """Get detailed pricing information for a product.

        Args:
            product_number: The product to get pricing for
            customer_id: Customer ID for pricing (default: "0")
            requested_quantity: Quantity for pricing calculation (default: 1)

        Returns:
            ProductPricingResponse with standard pricing tiers, calculated price
            for requested quantity, and availability information.
        """
        url = f"{API_BASE}/products/v4/search/{product_number}/productpricing"
        headers = _get_headers(customer_id)

        params = {"requestedQuantity": requested_quantity}
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

        return _make_request("GET", url, headers, use_user_token=False)

    @mcp.tool()
    def get_digi_reel_pricing(
        product_number: str,
        requested_quantity: int,
        customer_id: str = "0"
    ) -> Union[DigiReelPricingResponse, Dict[str, Any]]:
        """Get DigiReel pricing for a product.

        Args:
            product_number: DigiKey product number (must be DigiReel compatible)
            requested_quantity: Quantity for DigiReel pricing
            customer_id: Customer ID for pricing (default: "0")

        Returns:
            DigiReelPricingResponse with DigiReel-specific pricing including
            the DigiReel service fee and total price calculation.
        """
        url = f"{API_BASE}/products/v4/search/{product_number}/digireelpricing"
        headers = _get_headers(customer_id)

        params = {"requestedQuantity": requested_quantity}
        url += "?" + "&".join([f"{k}={v}" for k, v in params.items()])

        return _make_request("GET", url, headers, use_user_token=False)
