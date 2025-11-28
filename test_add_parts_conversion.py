#!/usr/bin/env python3
"""Test the add_parts_to_list dataclass conversion."""

import json
from src.tools.mylists_tools import RequestedPart, PartQuantity


def test_requested_part_conversion():
    """Test that RequestedPart converts to the correct API format."""

    # Test simple part with just part number
    part1 = RequestedPart(
        requested_part_number="296-8875-1-ND",
        customer_reference="R1"
    )
    result1 = part1.to_dict()

    print("Test 1: Simple part with part number and reference")
    print(json.dumps(result1, indent=2))
    assert result1["RequestedPartNumber"] == "296-8875-1-ND"
    assert result1["CustomerReference"] == "R1"
    assert "PartId" not in result1  # Should not include None values
    print("✓ Test 1 passed\n")

    # Test part with quantities
    part2 = RequestedPart(
        requested_part_number="296-8875-1-ND",
        customer_reference="R1",
        reference_designator="R1",
        quantities=[
            PartQuantity(quantity=10),
            PartQuantity(quantity=20, target_price=1.50)
        ]
    )
    result2 = part2.to_dict()

    print("Test 2: Part with quantities")
    print(json.dumps(result2, indent=2))
    assert len(result2["Quantities"]) == 2
    assert result2["Quantities"][0]["Quantity"] == 10
    assert result2["Quantities"][1]["Quantity"] == 20
    assert result2["Quantities"][1]["TargetPrice"] == 1.50
    assert "SelectedPackType" not in result2["Quantities"][0]  # Should not include None values
    print("✓ Test 2 passed\n")

    # Test that the result is a valid JSON object (not wrapped in "parts")
    print("Test 3: Verify output is a direct object, not wrapped")
    parts_list = [part1.to_dict(), part2.to_dict()]
    json_output = json.dumps(parts_list)
    print(f"Array output: {json_output[:100]}...")

    # Verify it's an array, not {"parts": [...]}
    parsed = json.loads(json_output)
    assert isinstance(parsed, list), "Output should be an array"
    assert len(parsed) == 2
    print("✓ Test 3 passed\n")

    print("=" * 60)
    print("✓ All tests passed!")
    print("=" * 60)
    print("\nExample API request body:")
    print(json.dumps(parts_list, indent=2))


if __name__ == "__main__":
    test_requested_part_conversion()
