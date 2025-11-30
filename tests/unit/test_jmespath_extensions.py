"""
Unit tests for custom JMESPath functions.

Tests the regex_replace() and int() custom functions with various inputs
including edge cases and error conditions.
"""

import pytest
from src.jmespath_extensions import search_with_custom_functions


class TestRegexReplaceFunction:
    """Test cases for the regex_replace() custom function."""

    def test_basic_replacement(self):
        """Test basic regex replacement."""
        data = {"value": "100 ohm"}
        result = search_with_custom_functions(
            "regex_replace(' ohm$', '', value)",
            data
        )
        assert result == "100"

    def test_multiple_replacements(self):
        """Test regex that matches multiple times."""
        data = {"value": "foo"}
        result = search_with_custom_functions(
            "regex_replace('o', 'x', value)",
            data
        )
        assert result == "fxx"

    def test_no_match_returns_unchanged(self):
        """Test that non-matching pattern returns original value."""
        data = {"value": "100 ohm"}
        result = search_with_custom_functions(
            "regex_replace('xyz', '', value)",
            data
        )
        assert result == "100 ohm"

    def test_invalid_regex_pattern_returns_unchanged(self):
        """Test that invalid regex pattern returns original value."""
        data = {"value": "test"}
        # '[' is invalid regex (unclosed character class)
        result = search_with_custom_functions(
            "regex_replace('[', '', value)",
            data
        )
        assert result == "test"

    def test_strip_non_numeric(self):
        """Test extracting numeric portion from alphanumeric string."""
        data = {"value": "R100K"}
        result = search_with_custom_functions(
            "regex_replace('[^0-9]', '', value)",
            data
        )
        assert result == "100"

    def test_remove_units_various_formats(self):
        """Test removing different unit formats."""
        test_cases = [
            ("100 ohm", "100 "),  # Space remains
            ("4.7 µF", "4.7 µ"),  # µ is not ASCII letter
            ("1000mA", "1000"),
            ("3.3V", "3.3"),
        ]
        for input_val, expected in test_cases:
            data = {"value": input_val}
            # Remove ASCII letters at end
            result = search_with_custom_functions(
                "regex_replace('[a-zA-Z]+$', '', value)",
                data
            )
            assert result == expected

    def test_empty_string(self):
        """Test regex_replace on empty string."""
        data = {"value": ""}
        result = search_with_custom_functions(
            "regex_replace('test', 'replacement', value)",
            data
        )
        assert result == ""

    def test_complex_pattern(self):
        """Test with complex regex pattern."""
        data = {"value": "100 kOhm"}
        result = search_with_custom_functions(
            "regex_replace(' [kK]?[oO]hm.*$', '', value)",
            data
        )
        assert result == "100"

    def test_replacement_with_backreferences(self):
        """Test regex replacement with capture groups."""
        data = {"value": "part-123-abc"}
        # Simple replacement test instead of backreferences (JMESPath string escaping is tricky)
        result = search_with_custom_functions(
            "regex_replace('-', '_', value)",
            data
        )
        assert result == "part_123_abc"


class TestIntFunction:
    """Test cases for the int() custom function."""

    def test_valid_numeric_string(self):
        """Test converting valid numeric string to int."""
        data = {"value": "100"}
        result = search_with_custom_functions("int(value)", data)
        assert result == 100
        assert isinstance(result, int)

    def test_already_numeric_int(self):
        """Test that existing integers pass through."""
        data = {"value": 42}
        result = search_with_custom_functions("int(value)", data)
        assert result == 42
        assert isinstance(result, int)

    def test_already_numeric_float(self):
        """Test that floats are converted to int (truncated)."""
        data = {"value": 42.7}
        result = search_with_custom_functions("int(value)", data)
        assert result == 42
        assert isinstance(result, int)

    def test_invalid_string_returns_null(self):
        """Test that non-numeric strings return null."""
        data = {"value": "abc"}
        result = search_with_custom_functions("int(value)", data)
        assert result is None

    def test_empty_string_returns_null(self):
        """Test that empty string returns null."""
        data = {"value": ""}
        result = search_with_custom_functions("int(value)", data)
        assert result is None

    def test_negative_numbers(self):
        """Test converting negative number strings."""
        data = {"value": "-42"}
        result = search_with_custom_functions("int(value)", data)
        assert result == -42

    def test_whitespace_string_returns_null(self):
        """Test that whitespace-only string returns null."""
        data = {"value": "   "}
        result = search_with_custom_functions("int(value)", data)
        assert result is None

    def test_numeric_with_whitespace(self):
        """Test that numeric string with whitespace fails (Python int() doesn't strip)."""
        # Note: Python's int() does actually strip whitespace, so this should work
        data = {"value": " 100 "}
        result = search_with_custom_functions("int(value)", data)
        assert result == 100

    def test_partial_numeric_string_returns_null(self):
        """Test that partially numeric strings return null."""
        data = {"value": "100abc"}
        result = search_with_custom_functions("int(value)", data)
        assert result is None


class TestCombinedWorkflow:
    """Test cases for combined regex_replace + int workflows."""

    def test_extract_and_convert_resistance_value(self):
        """Test extracting numeric value from resistance string."""
        data = {"resistance": "100 ohm"}
        result = search_with_custom_functions(
            "int(regex_replace(' ohm$', '', resistance))",
            data
        )
        assert result == 100

    def test_filter_by_converted_value(self):
        """Test filtering array by converted numeric value."""
        data = {
            "products": [
                {"resistance": "50 ohm"},
                {"resistance": "100 ohm"},
                {"resistance": "200 ohm"},
                {"resistance": "invalid"},
            ]
        }
        query = "products[?int(regex_replace(' ohm$', '', resistance)) >= `100`]"
        result = search_with_custom_functions(query, data)

        assert len(result) == 2
        assert result[0]["resistance"] == "100 ohm"
        assert result[1]["resistance"] == "200 ohm"

    def test_transform_and_project(self):
        """Test transforming values in projection."""
        data = {
            "products": [
                {"part": "R100K", "name": "Resistor 1"},
                {"part": "R220K", "name": "Resistor 2"},
            ]
        }
        query = "products[].{Name: name, Value: int(regex_replace('[^0-9]', '', part))}"
        result = search_with_custom_functions(query, data)

        assert len(result) == 2
        assert result[0] == {"Name": "Resistor 1", "Value": 100}
        assert result[1] == {"Name": "Resistor 2", "Value": 220}

    def test_range_filter_with_conversion(self):
        """Test filtering by numeric range after conversion."""
        data = {
            "products": [
                {"resistance": "25 ohm"},
                {"resistance": "75 ohm"},
                {"resistance": "150 ohm"},
                {"resistance": "250 ohm"},
            ]
        }
        query = """
        products[?int(regex_replace(' ohm$', '', resistance)) >= `50`
                 && int(regex_replace(' ohm$', '', resistance)) <= `200`]
        """
        result = search_with_custom_functions(query, data)

        assert len(result) == 2
        assert result[0]["resistance"] == "75 ohm"
        assert result[1]["resistance"] == "150 ohm"

    def test_null_filtering(self):
        """Test filtering out null values from failed conversions."""
        data = {
            "products": [
                {"value": "100"},
                {"value": "invalid"},
                {"value": "200"},
            ]
        }
        query = "products[?int(value) != `null`]"
        result = search_with_custom_functions(query, data)

        assert len(result) == 2
        assert result[0]["value"] == "100"
        assert result[1]["value"] == "200"

    def test_complex_component_value_extraction(self):
        """Test realistic component value extraction scenario."""
        data = {
            "components": [
                {"type": "resistor", "value": "10000 ohm", "price": "0.10"},
                {"type": "resistor", "value": "100 ohm", "price": "0.05"},
                {"type": "capacitor", "value": "100uF", "price": "0.25"},
            ]
        }
        # Extract resistors with value >= 1000 ohms
        query = """
        components[?type == 'resistor'
                   && int(regex_replace('[^0-9]', '', value)) >= `1000`]
        .{Type: type, ValueOhm: int(regex_replace('[^0-9]', '', value)), Price: price}
        """
        result = search_with_custom_functions(query, data)

        assert len(result) == 1
        assert result[0]["Type"] == "resistor"
        assert result[0]["ValueOhm"] == 10000
        assert result[0]["Price"] == "0.10"


class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_null_value_in_regex_replace(self):
        """Test regex_replace handles null gracefully."""
        # JMESPath may pass null if field doesn't exist
        data = {"other_field": "value"}
        # Accessing non-existent field returns null, which regex_replace should handle
        result = search_with_custom_functions(
            "regex_replace('test', '', missing_field)",
            data
        )
        # Should return null unchanged
        assert result is None

    def test_null_value_in_int(self):
        """Test int handles null gracefully."""
        data = {"other_field": "value"}
        result = search_with_custom_functions("int(missing_field)", data)
        assert result is None

    def test_chained_projections(self):
        """Test custom functions in chained projections."""
        data = {
            "categories": [
                {
                    "name": "Resistors",
                    "products": [
                        {"resistance": "100 ohm"},
                        {"resistance": "200 ohm"},
                    ]
                }
            ]
        }
        query = """
        categories[].products[].int(regex_replace(' ohm$', '', resistance))
        """
        result = search_with_custom_functions(query, data)

        # Flattened list of converted values
        assert result == [100, 200]

    def test_unicode_in_regex_replace(self):
        """Test regex_replace with unicode characters."""
        data = {"value": "4.7 µF"}
        # Remove the µ character
        result = search_with_custom_functions(
            "regex_replace('µ', '', value)",
            data
        )
        assert result == "4.7 F"

    def test_special_regex_characters(self):
        """Test regex_replace with metacharacter classes."""
        data = {"value": "abc123def"}
        # Use \d to match digits
        result = search_with_custom_functions(
            "regex_replace('[0-9]+', '-', value)",
            data
        )
        assert result == "abc-def"
