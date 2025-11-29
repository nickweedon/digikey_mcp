#!/usr/bin/env python3
"""Test JMESPath functionality for keyword_search."""

import json
import jmespath

# Load the sample arduino search result
with open('arduino_search_result.json', 'r') as f:
    response = json.load(f)

print("=" * 60)
print("Testing JMESPath Query Implementation")
print("=" * 60)

# Test 1: Default query
print("\n1. Testing DEFAULT QUERY:")
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

try:
    result = jmespath.search(default_query, response)
    print(f"✓ Default query succeeded!")
    print(f"  Products returned: {len(result['Products'])}")
    print(f"  Total count: {result['ProductsCount']}")
    if result['Products']:
        first = result['Products'][0]
        print(f"\n  First product:")
        print(f"    DigiKey PN: {first.get('DigiKeyPartNumber')}")
        print(f"    Mfr PN: {first.get('ManufacturerPartNumber')}")
        print(f"    Manufacturer: {first.get('Manufacturer')}")
        print(f"    Price: ${first.get('UnitPrice')}")
        print(f"    In Stock: {first.get('InStock')}")
        print(f"    Qty Available: {first.get('QuantityAvailable')}")
except Exception as e:
    print(f"✗ Default query failed: {e}")
    import traceback
    traceback.print_exc()

# Test 2: Custom query - extract only part numbers and prices
print("\n2. Testing CUSTOM QUERY (part numbers and prices only):")
custom_query = '{Count: ProductsCount, Parts: Products[].{PN: ManufacturerProductNumber, Price: UnitPrice, Stock: QuantityAvailable}}'

try:
    result = jmespath.search(custom_query, response)
    print(f"✓ Custom query succeeded!")
    print(f"  Total count: {result['Count']}")
    print(f"  Parts: {len(result['Parts'])}")
    for i, part in enumerate(result['Parts'][:3], 1):
        print(f"    {i}. PN: {part['PN']}, Price: ${part['Price']}, Stock: {part['Stock']}")
except Exception as e:
    print(f"✗ Custom query failed: {e}")

# Test 3: Filtered query - only in-stock items
print("\n3. Testing FILTERED QUERY (in-stock only):")
filtered_query = '{Products: Products[?QuantityAvailable > `0`].{PN: ManufacturerProductNumber, Stock: QuantityAvailable}}'

try:
    result = jmespath.search(filtered_query, response)
    print(f"✓ Filtered query succeeded!")
    print(f"  In-stock products: {len(result['Products'])}")
    for i, part in enumerate(result['Products'][:3], 1):
        print(f"    {i}. PN: {part['PN']}, Stock: {part['Stock']}")
except Exception as e:
    print(f"✗ Filtered query failed: {e}")

print("\n" + "=" * 60)
print("✓ All JMESPath tests completed successfully!")
print("=" * 60)
