#!/usr/bin/env python3
"""Test structured error handling."""

import json
from unittest.mock import Mock, patch
from src.api.client import _make_request

print("=" * 60)
print("Testing Structured Error Handling")
print("=" * 60)

# Test 1: Simulate a 404 error
print("\n1. Testing 404 Error Handling:")
mock_response = Mock()
mock_response.status_code = 404
mock_response.url = "https://api.digikey.com/mylists/v1/lists/9HI0IPL3D6/parts/1942531"
mock_response.text = '{"type":null,"title":"MyLists Data Error","status":404,"detail":"The requested part does not exist on the list id provided","instance":null,"correlationId":null,"errors":{}}'
mock_response.json.return_value = json.loads(mock_response.text)

with patch('requests.get', return_value=mock_response):
    result = _make_request("GET", mock_response.url, {}, use_user_token=True)

    if "error" in result:
        print("✓ 404 error returned as structured error (not exception)")
        print(f"  Error type: {result['error']['type']}")
        print(f"  Error code: {result['error']['code']}")
        print(f"  Status: {result['error']['status']}")
        print(f"  Message: {result['error']['message']}")
        print(f"  URL: {result['error']['url']}")
    else:
        print("✗ Error not structured properly")
        print(f"  Result: {result}")

# Test 2: Simulate a 400 error
print("\n2. Testing 400 Error Handling:")
mock_response = Mock()
mock_response.status_code = 400
mock_response.url = "https://api.digikey.com/mylists/v1/lists/invalid"
mock_response.text = '{"detail":"Invalid request format"}'
mock_response.json.return_value = json.loads(mock_response.text)

with patch('requests.get', return_value=mock_response):
    result = _make_request("GET", mock_response.url, {}, use_user_token=False)

    if "error" in result:
        print("✓ 400 error returned as structured error")
        print(f"  Error type: {result['error']['type']}")
        print(f"  Message: {result['error']['message']}")
    else:
        print("✗ Error not structured properly")

# Test 3: Simulate a 403 error
print("\n3. Testing 403 Error Handling:")
mock_response = Mock()
mock_response.status_code = 403
mock_response.url = "https://api.digikey.com/mylists/v1/lists/forbidden"
mock_response.text = '{"detail":"Access denied to this resource"}'
mock_response.json.return_value = json.loads(mock_response.text)

with patch('requests.get', return_value=mock_response):
    result = _make_request("GET", mock_response.url, {}, use_user_token=False)

    if "error" in result:
        print("✓ 403 error returned as structured error")
        print(f"  Error type: {result['error']['type']}")
        print(f"  Message: {result['error']['message']}")
    else:
        print("✗ Error not structured properly")

# Test 4: Test successful response still works
print("\n4. Testing Successful Response:")
mock_response = Mock()
mock_response.status_code = 200
mock_response.url = "https://api.digikey.com/mylists/v1/lists"
mock_response.json.return_value = {"status": "ok", "data": []}

with patch('requests.get', return_value=mock_response):
    result = _make_request("GET", mock_response.url, {}, use_user_token=False)

    if "error" not in result and "status" in result:
        print("✓ Successful response works correctly")
        print(f"  Result: {result}")
    else:
        print("✗ Successful response broken")

print("\n" + "=" * 60)
print("✓ All error handling tests completed!")
print("=" * 60)
