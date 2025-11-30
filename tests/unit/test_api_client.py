"""Unit tests for API client error handling.

Tests that the API client returns structured error responses
for 400, 403, 404 errors instead of raising exceptions.
"""

import json
import pytest
from unittest.mock import Mock, patch


class TestStructuredErrorHandling:
    """Tests for structured error handling in _make_request."""

    @pytest.mark.unit
    def test_404_error_returns_structured_error(self):
        """Test that 404 errors return structured error dict instead of raising."""
        from src.api.client import _make_request

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.url = "https://api.digikey.com/mylists/v1/lists/invalid/parts/123"
        mock_response.text = json.dumps({
            "type": None,
            "title": "MyLists Data Error",
            "status": 404,
            "detail": "The requested part does not exist on the list id provided",
        })
        mock_response.json.return_value = json.loads(mock_response.text)

        with patch('requests.get', return_value=mock_response):
            result = _make_request("GET", mock_response.url, {}, use_user_token=True)

        assert "error" in result, "Expected structured error response"
        assert result["error"]["type"] == "ResourceNotFound"
        assert result["error"]["code"] == "HTTP_404"
        assert result["error"]["status"] == 404
        assert "not exist" in result["error"]["message"]
        assert result["error"]["url"] == mock_response.url

    @pytest.mark.unit
    def test_400_error_returns_structured_error(self):
        """Test that 400 errors return structured error dict."""
        from src.api.client import _make_request

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.url = "https://api.digikey.com/mylists/v1/lists/invalid"
        mock_response.text = json.dumps({"detail": "Invalid request format"})
        mock_response.json.return_value = json.loads(mock_response.text)

        with patch('requests.get', return_value=mock_response):
            result = _make_request("GET", mock_response.url, {}, use_user_token=False)

        assert "error" in result, "Expected structured error response"
        assert result["error"]["type"] == "BadRequest"
        assert result["error"]["code"] == "HTTP_400"
        assert result["error"]["status"] == 400
        assert "Invalid request format" in result["error"]["message"]

    @pytest.mark.unit
    def test_403_error_returns_structured_error(self):
        """Test that 403 errors return structured error dict."""
        from src.api.client import _make_request

        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.url = "https://api.digikey.com/mylists/v1/lists/forbidden"
        mock_response.text = json.dumps({"detail": "Access denied to this resource"})
        mock_response.json.return_value = json.loads(mock_response.text)

        with patch('requests.get', return_value=mock_response):
            result = _make_request("GET", mock_response.url, {}, use_user_token=False)

        assert "error" in result, "Expected structured error response"
        assert result["error"]["type"] == "Forbidden"
        assert result["error"]["code"] == "HTTP_403"
        assert result["error"]["status"] == 403
        assert "Access denied" in result["error"]["message"]

    @pytest.mark.unit
    def test_500_error_raises_exception(self):
        """Test that 500 errors raise HTTPError (not structured)."""
        from src.api.client import _make_request
        from requests.exceptions import HTTPError

        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.url = "https://api.digikey.com/products/v4/search/keyword"
        mock_response.text = "Internal server error"
        mock_response.raise_for_status.side_effect = HTTPError("500 Server Error")

        with patch('requests.post', return_value=mock_response):
            with pytest.raises(HTTPError):
                _make_request("POST", mock_response.url, {}, {"Keywords": "test"}, use_user_token=False)

    @pytest.mark.unit
    def test_successful_response_returns_data(self):
        """Test that successful responses return the JSON data."""
        from src.api.client import _make_request

        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.url = "https://api.digikey.com/mylists/v1/lists"
        mock_response.content = b'{"status": "ok", "data": [{"id": 1}]}'
        mock_response.json.return_value = {"status": "ok", "data": [{"id": 1}]}

        with patch('requests.get', return_value=mock_response):
            result = _make_request("GET", mock_response.url, {}, use_user_token=False)

        assert "error" not in result, "Successful response should not have error"
        assert result["status"] == "ok"
        assert result["data"] == [{"id": 1}]

    @pytest.mark.unit
    def test_204_no_content_returns_success_dict(self):
        """Test that 204 No Content returns success dict."""
        from src.api.client import _make_request

        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.url = "https://api.digikey.com/mylists/v1/lists/abc123"
        mock_response.content = b""

        with patch('requests.delete', return_value=mock_response):
            result = _make_request("DELETE", mock_response.url, {}, use_user_token=True)

        assert result["status"] == "success"
        assert "message" in result

    @pytest.mark.unit
    def test_404_error_with_non_json_response(self):
        """Test that 404 errors with non-JSON response bodies are handled."""
        from src.api.client import _make_request

        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.url = "https://api.digikey.com/mylists/v1/lists/notfound"
        mock_response.text = "Not Found"
        mock_response.json.side_effect = json.JSONDecodeError("", "", 0)

        with patch('requests.get', return_value=mock_response):
            result = _make_request("GET", mock_response.url, {}, use_user_token=False)

        assert "error" in result
        assert result["error"]["type"] == "ResourceNotFound"
        assert result["error"]["status"] == 404
        # Message should fall back to response text
        assert result["error"]["message"] == "Not Found"

    @pytest.mark.unit
    def test_error_includes_details_from_api(self):
        """Test that error response includes original API error details."""
        from src.api.client import _make_request

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.url = "https://api.digikey.com/mylists/v1/lists"
        api_error = {
            "detail": "Validation failed",
            "errors": {"ListName": ["Name is required"]},
            "correlationId": "abc123"
        }
        mock_response.text = json.dumps(api_error)
        mock_response.json.return_value = api_error

        with patch('requests.post', return_value=mock_response):
            result = _make_request("POST", mock_response.url, {}, {"ListName": ""}, use_user_token=True)

        assert "error" in result
        assert result["error"]["details"] == api_error
        assert result["error"]["details"]["errors"]["ListName"] == ["Name is required"]
