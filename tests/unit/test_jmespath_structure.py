"""Unit tests for JMESPath query structure consistency.

Tests that verify the structure of responses from default JMESPath queries
matches the structure of responses from custom JMESPath queries that are
designed to produce the same shape.
"""

import pytest
from typing import Any, Dict, Set


def extract_structure_keys(data: Any, prefix: str = "") -> Set[str]:
    """Extract the structure (keys) from a nested dictionary/list recursively.

    Returns a set of keys representing the shape of the data structure.
    For lists, we analyze the first item only.

    Args:
        data: The data structure to analyze
        prefix: Current key path (for recursion)

    Returns:
        Set of key paths like {'key1', 'key1.subkey', 'key1.list[].item'}
    """
    keys = set()

    if isinstance(data, dict):
        for key, value in data.items():
            full_key = f"{prefix}.{key}" if prefix else key
            keys.add(full_key)
            # Recurse into nested structures
            keys.update(extract_structure_keys(value, full_key))
    elif isinstance(data, list) and data:
        # Process first item to get structure
        # Add array indicator to the prefix
        array_prefix = f"{prefix}[]" if prefix else "[]"
        keys.add(array_prefix)
        keys.update(extract_structure_keys(data[0], prefix))

    return keys


class TestKeywordSearchJMESPathStructure:
    """Tests for keyword_search JMESPath query structure consistency."""

    @pytest.mark.unit
    def test_default_jmespath_structure(
        self, client_authenticated_state, patched_api_base, fake_server
    ):
        """Test that default JMESPath query returns expected structure."""
        from src.tools.product_tools import register_product_tools
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_product_tools(mcp)

        tools = mcp._tool_manager._tools
        keyword_search = tools["keyword_search"].fn

        # Call with default JMESPath
        result = keyword_search(keywords="resistor", limit=5)

        # Verify it's a dict
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"

        # Extract structure
        structure = extract_structure_keys(result)

        # Verify top-level keys exist
        assert "ProductsCount" in structure, "Missing ProductsCount in default structure"
        assert "Products" in structure, "Missing Products in default structure"

        # Verify Products is an array
        assert "Products[]" in structure or len([k for k in structure if k.startswith("Products.")]) > 0, \
            "Products should be an array or have nested fields"

        # Verify expected fields in Products array items
        expected_product_fields = [
            "Products.DigiKeyPartNumber",
            "Products.ManufacturerPartNumber",
            "Products.Manufacturer",
            "Products.Description",
            "Products.UnitPrice",
            "Products.QuantityAvailable",
            "Products.MinimumOrderQuantity",
            "Products.ProductStatus",
            "Products.ProductUrl",
            "Products.InStock",
            "Products.Pricing",
        ]

        for field in expected_product_fields:
            assert field in structure, f"Missing expected field '{field}' in default structure"

    @pytest.mark.unit
    def test_custom_jmespath_matches_default_structure(
        self, client_authenticated_state, patched_api_base, fake_server
    ):
        """Test that custom JMESPath can reproduce default structure."""
        from src.tools.product_tools import register_product_tools
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_product_tools(mcp)

        tools = mcp._tool_manager._tools
        keyword_search = tools["keyword_search"].fn

        # Get result with default JMESPath
        default_result = keyword_search(keywords="resistor", limit=5)
        default_structure = extract_structure_keys(default_result)

        # Replicate the default query manually
        custom_query = (
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

        custom_result = keyword_search(keywords="resistor", limit=5, jmespath_query=custom_query)
        custom_structure = extract_structure_keys(custom_result)

        # Structures should match
        assert default_structure == custom_structure, (
            f"Structure mismatch!\n"
            f"Default only: {default_structure - custom_structure}\n"
            f"Custom only: {custom_structure - default_structure}"
        )

    @pytest.mark.unit
    def test_custom_jmespath_preserves_value_types(
        self, client_authenticated_state, patched_api_base, fake_server
    ):
        """Test that custom JMESPath preserves value types matching default."""
        from src.tools.product_tools import register_product_tools
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_product_tools(mcp)

        tools = mcp._tool_manager._tools
        keyword_search = tools["keyword_search"].fn

        # Get default result
        default_result = keyword_search(keywords="resistor", limit=5)

        # Get custom result with same structure
        custom_query = (
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
        custom_result = keyword_search(keywords="resistor", limit=5, jmespath_query=custom_query)

        # Verify types match for top-level fields
        assert type(default_result["ProductsCount"]) == type(custom_result["ProductsCount"]), \
            "ProductsCount type mismatch"
        assert type(default_result["Products"]) == type(custom_result["Products"]), \
            "Products type mismatch"

        # If we have products, verify field types match
        if default_result["Products"] and custom_result["Products"]:
            default_product = default_result["Products"][0]
            custom_product = custom_result["Products"][0]

            # Check a few key field types
            for field in ["ManufacturerPartNumber", "UnitPrice", "QuantityAvailable"]:
                if field in default_product and field in custom_product:
                    default_type = type(default_product[field])
                    custom_type = type(custom_product[field])
                    assert default_type == custom_type, \
                        f"Type mismatch for {field}: default={default_type}, custom={custom_type}"

    @pytest.mark.unit
    def test_custom_jmespath_with_custom_functions_structure(
        self, client_authenticated_state, patched_api_base, fake_server
    ):
        """Test that custom JMESPath with custom functions maintains consistent structure."""
        from src.tools.product_tools import register_product_tools
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_product_tools(mcp)

        tools = mcp._tool_manager._tools
        keyword_search = tools["keyword_search"].fn

        # Query using simpler custom functions that won't fail
        # Test str() and int() which are simpler than regex_replace
        query_with_functions = (
            '{ProductsCount: ProductsCount, Products: Products[].{'
            'PartNumber: ManufacturerPartNumber,'
            'Stock: QuantityAvailable,'
            'StockStr: str(QuantityAvailable),'
            'InStockCount: int(QuantityAvailable)}}'
        )

        result = keyword_search(keywords="resistor", limit=5, jmespath_query=query_with_functions)

        # Verify result is a dict (not a dataclass or error)
        assert isinstance(result, dict), f"Expected dict, got {type(result)}. JMESPath query may have failed."

        # Extract structure
        structure = extract_structure_keys(result)

        # Verify expected structure
        assert "ProductsCount" in structure
        assert "Products" in structure

        expected_fields = [
            "Products.PartNumber",
            "Products.Stock",
            "Products.StockStr",
            "Products.InStockCount",
        ]

        for field in expected_fields:
            assert field in structure, f"Missing field '{field}' in custom function query result"

        # Verify types are appropriate
        if result["Products"]:
            product = result["Products"][0]
            # StockStr should be a string (str() always returns string)
            assert isinstance(product.get("StockStr"), str) or product.get("StockStr") is None
            # InStockCount should be int or None (int() can return None on failure)
            assert isinstance(product.get("InStockCount"), int) or product.get("InStockCount") is None


class TestGetPartsByListIdJMESPathStructure:
    """Tests for get_parts_by_list_id JMESPath query structure consistency."""

    @pytest.mark.unit
    def test_default_jmespath_structure(
        self, authenticated_state, patched_api_base, fake_server
    ):
        """Test that default JMESPath query returns expected structure."""
        from src.tools.mylists_tools import register_mylists_tools
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        tools = mcp._tool_manager._tools
        get_parts = tools["get_parts_by_list_id"].fn

        # Call with default JMESPath
        result = get_parts(list_id="list-001", limit=10)

        # Verify it's a dict
        assert isinstance(result, dict), f"Expected dict, got {type(result)}"

        # Extract structure
        structure = extract_structure_keys(result)

        # Verify top-level keys exist
        assert "TotalParts" in structure, "Missing TotalParts in default structure"
        assert "PartsList" in structure, "Missing PartsList in default structure"

        # Verify expected fields in PartsList array items
        expected_part_fields = [
            "PartsList.UniqueId",
            "PartsList.PartId",
            "PartsList.ManufacturerPartNumber",
            "PartsList.Manufacturer",
            "PartsList.Description",
            "PartsList.Availability",
            "PartsList.PartStatus",
            "PartsList.DigiKeyPartNumber",
            "PartsList.MinOrderQty",
            "PartsList.Notes",
            "PartsList.Htsus",
            "PartsList.CountryOfOrigin",
            "PartsList.OriginalPartNumber",
            "PartsList.ImageUrl",
        ]

        for field in expected_part_fields:
            assert field in structure, f"Missing expected field '{field}' in default structure"

    @pytest.mark.unit
    def test_custom_jmespath_matches_default_structure(
        self, authenticated_state, patched_api_base, fake_server
    ):
        """Test that custom JMESPath can reproduce default structure."""
        from src.tools.mylists_tools import register_mylists_tools
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        tools = mcp._tool_manager._tools
        get_parts = tools["get_parts_by_list_id"].fn

        # Get result with default JMESPath
        default_result = get_parts(list_id="list-001", limit=10)
        default_structure = extract_structure_keys(default_result)

        # Replicate the default query manually
        custom_query = (
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

        custom_result = get_parts(list_id="list-001", limit=10, jmespath_query=custom_query)
        custom_structure = extract_structure_keys(custom_result)

        # Structures should match
        assert default_structure == custom_structure, (
            f"Structure mismatch!\n"
            f"Default only: {default_structure - custom_structure}\n"
            f"Custom only: {custom_structure - default_structure}"
        )

    @pytest.mark.unit
    def test_custom_jmespath_preserves_value_types(
        self, authenticated_state, patched_api_base, fake_server
    ):
        """Test that custom JMESPath preserves value types matching default."""
        from src.tools.mylists_tools import register_mylists_tools
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        tools = mcp._tool_manager._tools
        get_parts = tools["get_parts_by_list_id"].fn

        # Get default result
        default_result = get_parts(list_id="list-001", limit=10)

        # Get custom result with same structure
        custom_query = (
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
        custom_result = get_parts(list_id="list-001", limit=10, jmespath_query=custom_query)

        # Verify types match for top-level fields
        assert type(default_result["TotalParts"]) == type(custom_result["TotalParts"]), \
            "TotalParts type mismatch"
        assert type(default_result["PartsList"]) == type(custom_result["PartsList"]), \
            "PartsList type mismatch"

        # If we have parts, verify field types match
        if default_result["PartsList"] and custom_result["PartsList"]:
            default_part = default_result["PartsList"][0]
            custom_part = custom_result["PartsList"][0]

            # Check a few key field types
            for field in ["UniqueId", "PartId", "ManufacturerPartNumber", "MinOrderQty"]:
                if field in default_part and field in custom_part:
                    default_type = type(default_part[field])
                    custom_type = type(custom_part[field])
                    # Allow None values to have different "types"
                    if default_part[field] is not None and custom_part[field] is not None:
                        assert default_type == custom_type, \
                            f"Type mismatch for {field}: default={default_type}, custom={custom_type}"

    @pytest.mark.unit
    def test_custom_jmespath_with_custom_functions_structure(
        self, authenticated_state, patched_api_base, fake_server
    ):
        """Test that custom JMESPath with custom functions maintains consistent structure."""
        from src.tools.mylists_tools import register_mylists_tools
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        tools = mcp._tool_manager._tools
        get_parts = tools["get_parts_by_list_id"].fn

        # Query using simpler custom functions that won't fail
        # Test str() and int() which are simpler than regex_replace
        query_with_functions = (
            '{TotalParts: TotalParts, PartsList: PartsList[].{'
            'PartNumber: DigiKeyPartNumber,'
            'Manufacturer: Manufacturer,'
            'PartIdInt: int(PartId),'
            'PartIdStr: str(PartId),'
            'MinQty: MinOrderQty}}'
        )

        result = get_parts(list_id="list-001", limit=10, jmespath_query=query_with_functions)

        # Verify result is a dict (not a dataclass or error)
        assert isinstance(result, dict), f"Expected dict, got {type(result)}. JMESPath query may have failed."

        # Extract structure
        structure = extract_structure_keys(result)

        # Verify expected structure
        assert "TotalParts" in structure
        assert "PartsList" in structure

        expected_fields = [
            "PartsList.PartNumber",
            "PartsList.Manufacturer",
            "PartsList.PartIdInt",
            "PartsList.PartIdStr",
            "PartsList.MinQty",
        ]

        for field in expected_fields:
            assert field in structure, f"Missing field '{field}' in custom function query result"

        # Verify types are appropriate
        if result["PartsList"]:
            part = result["PartsList"][0]
            # PartIdStr should be a string (str() always returns string)
            assert isinstance(part.get("PartIdStr"), str)
            # PartIdInt should be int (int() converts the PartId)
            assert isinstance(part.get("PartIdInt"), int) or part.get("PartIdInt") is None

    @pytest.mark.unit
    def test_custom_jmespath_array_flattening_behavior(
        self, authenticated_state, patched_api_base, fake_server
    ):
        """Test JMESPath array flattening behavior for nested arrays.

        This tests that nested array projections (e.g., Quantities[].PackOptions[])
        flatten correctly when used in the default query structure.
        """
        from src.tools.mylists_tools import register_mylists_tools
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        tools = mcp._tool_manager._tools
        get_parts = tools["get_parts_by_list_id"].fn

        # Get result with default JMESPath (which uses nested array projections)
        result = get_parts(list_id="list-001", limit=10)

        # Verify the structure
        assert isinstance(result, dict)
        assert "PartsList" in result

        if result["PartsList"]:
            part = result["PartsList"][0]

            # Fields that use nested array projections should be arrays
            # (Quantities[].FieldName creates an array)
            array_projection_fields = ["RequestedQuantity", "PackQuantity", "PackType", "UnitPrice", "ExtendedPrice"]

            for field in array_projection_fields:
                if field in part:
                    # These should be arrays due to the projection
                    assert isinstance(part[field], list), \
                        f"Field '{field}' should be a list due to array projection, got {type(part[field])}"


class TestJMESPathStructureDocumentation:
    """Tests that verify JMESPath examples in docstrings produce expected structures."""

    @pytest.mark.unit
    def test_keyword_search_docstring_example_structure(
        self, client_authenticated_state, patched_api_base, fake_server
    ):
        """Test that the JMESPath example in keyword_search docstring works correctly."""
        from src.tools.product_tools import register_product_tools
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_product_tools(mcp)

        tools = mcp._tool_manager._tools
        keyword_search = tools["keyword_search"].fn

        # Example from docstring
        query = '{Count: ProductsCount, Parts: Products[].{PN: ManufacturerProductNumber, Price: UnitPrice, Stock: QuantityAvailable}}'
        result = keyword_search(keywords="resistor", limit=5, jmespath_query=query)

        # Verify structure
        assert isinstance(result, dict)
        assert "Count" in result
        assert "Parts" in result
        assert isinstance(result["Parts"], list)

        if result["Parts"]:
            part = result["Parts"][0]
            assert "PN" in part
            assert "Price" in part
            assert "Stock" in part

    @pytest.mark.unit
    def test_get_parts_by_list_id_docstring_example_structure(
        self, authenticated_state, patched_api_base, fake_server
    ):
        """Test that the JMESPath example in get_parts_by_list_id docstring works correctly."""
        from src.tools.mylists_tools import register_mylists_tools
        from fastmcp import FastMCP

        mcp = FastMCP("test")
        register_mylists_tools(mcp)

        tools = mcp._tool_manager._tools
        get_parts = tools["get_parts_by_list_id"].fn

        # Example from docstring
        query = '{TotalParts: TotalParts, PartsList: PartsList[].{Id: PartId, Number: DigiKeyPartNumber, Prices: Quantities[].PackOptions[].{Unit: CalculatedUnitPrice, Ext: ExtendedPrice}}}'
        result = get_parts(list_id="list-001", limit=10, jmespath_query=query)

        # Verify structure
        assert isinstance(result, dict)
        assert "TotalParts" in result
        assert "PartsList" in result
        assert isinstance(result["PartsList"], list)

        if result["PartsList"]:
            part = result["PartsList"][0]
            assert "Id" in part
            assert "Number" in part
            assert "Prices" in part
            # Prices should be a flattened array due to nested projections
            assert isinstance(part["Prices"], list)

            if part["Prices"]:
                price = part["Prices"][0]
                assert "Unit" in price
                assert "Ext" in price
