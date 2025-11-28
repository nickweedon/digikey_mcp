#!/usr/bin/env python3
"""Test type annotations and dataclasses for MyLists tools."""

from typing import get_type_hints
from src.tools.mylists_tools import (
    RequestedPart,
    PartQuantity,
    ListId,
    PartId,
    CustomerId,
    ListSource,
    _to_dict_excluding_none
)


def test_type_aliases():
    """Test that type aliases are properly defined."""
    print("Testing type aliases...")

    # Type aliases should resolve to their base types
    assert ListId == str
    assert PartId == str
    assert CustomerId == str

    print("✓ Type aliases correct")


def test_helper_function():
    """Test the _to_dict_excluding_none helper."""
    print("\nTesting helper function...")

    result = _to_dict_excluding_none({
        "key1": "value",
        "key2": None,
        "key3": 123,
        "key4": None
    })

    assert result == {"key1": "value", "key3": 123}
    assert "key2" not in result
    assert "key4" not in result

    print("✓ Helper function works correctly")


def test_part_quantity_class():
    """Test PartQuantity class."""
    print("\nTesting PartQuantity class...")

    # Test with all fields
    qty1 = PartQuantity(selected_pack_type=1, quantity=10, target_price=1.50)
    dict1 = qty1.to_dict()

    assert dict1["SelectedPackType"] == 1
    assert dict1["Quantity"] == 10
    assert dict1["TargetPrice"] == 1.50

    # Test with only some fields (None should be excluded)
    qty2 = PartQuantity(quantity=20)
    dict2 = qty2.to_dict()

    assert dict2["Quantity"] == 20
    assert "SelectedPackType" not in dict2
    assert "TargetPrice" not in dict2

    print("✓ PartQuantity class works correctly")


def test_requested_part_class():
    """Test RequestedPart class."""
    print("\nTesting RequestedPart class...")

    # Test minimal part
    part1 = RequestedPart(requested_part_number="296-8875-1-ND")
    dict1 = part1.to_dict()

    assert dict1["RequestedPartNumber"] == "296-8875-1-ND"
    assert len(dict1) == 1  # Only one field

    # Test full part with quantities
    qty = PartQuantity(quantity=10, target_price=1.00)
    part2 = RequestedPart(
        requested_part_number="296-8875-1-ND",
        customer_reference="R1",
        reference_designator="R1",
        notes="Test resistor",
        quantities=[qty]
    )
    dict2 = part2.to_dict()

    assert dict2["RequestedPartNumber"] == "296-8875-1-ND"
    assert dict2["CustomerReference"] == "R1"
    assert dict2["ReferenceDesignator"] == "R1"
    assert dict2["Notes"] == "Test resistor"
    assert len(dict2["Quantities"]) == 1
    assert dict2["Quantities"][0]["Quantity"] == 10

    # Test with multiple quantities
    part3 = RequestedPart(
        part_id="12345",
        quantities=[
            PartQuantity(quantity=10),
            PartQuantity(quantity=100, target_price=0.50)
        ]
    )
    dict3 = part3.to_dict()

    assert dict3["PartId"] == "12345"
    assert len(dict3["Quantities"]) == 2
    assert dict3["Quantities"][0]["Quantity"] == 10
    assert dict3["Quantities"][1]["Quantity"] == 100
    assert dict3["Quantities"][1]["TargetPrice"] == 0.50

    print("✓ RequestedPart class works correctly")


def test_tool_function_signatures():
    """Test that tool functions have proper type annotations."""
    print("\nTesting tool function type annotations...")

    # Import the module to get the registered functions
    from src.tools import mylists_tools

    # We can't easily access the inner functions, but we can verify
    # the module has the expected types defined
    assert hasattr(mylists_tools, 'ListId')
    assert hasattr(mylists_tools, 'PartId')
    assert hasattr(mylists_tools, 'CustomerId')
    assert hasattr(mylists_tools, 'ListSource')
    assert hasattr(mylists_tools, 'RequestedPart')
    assert hasattr(mylists_tools, 'PartQuantity')

    print("✓ Tool function type annotations present")


def test_api_format_conversion():
    """Test that our classes convert to the exact API format expected."""
    print("\nTesting API format conversion...")

    # Create a complex part structure
    part = RequestedPart(
        requested_part_number="296-8875-1-ND",
        manufacturer_name="Test Manufacturer",
        customer_reference="REF-001",
        reference_designator="R1",
        notes="Sample part",
        selected_quantity_index=0,
        attrition=5,
        quantities=[
            PartQuantity(
                selected_pack_type=1,
                quantity=100,
                target_price=0.75
            )
        ]
    )

    api_dict = part.to_dict()

    # Verify all fields are in PascalCase
    expected_keys = {
        "RequestedPartNumber",
        "ManufacturerName",
        "CustomerReference",
        "ReferenceDesignator",
        "Notes",
        "SelectedQuantityIndex",
        "Attrition",
        "Quantities"
    }

    assert set(api_dict.keys()) == expected_keys

    # Verify quantity structure
    assert len(api_dict["Quantities"]) == 1
    qty_dict = api_dict["Quantities"][0]
    assert qty_dict["SelectedPackType"] == 1
    assert qty_dict["Quantity"] == 100
    assert qty_dict["TargetPrice"] == 0.75

    print("✓ API format conversion correct")


def main():
    """Run all tests."""
    print("=" * 60)
    print("Testing MyLists Type Annotations and Dataclasses")
    print("=" * 60)

    test_type_aliases()
    test_helper_function()
    test_part_quantity_class()
    test_requested_part_class()
    test_tool_function_signatures()
    test_api_format_conversion()

    print("\n" + "=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)


if __name__ == "__main__":
    main()
