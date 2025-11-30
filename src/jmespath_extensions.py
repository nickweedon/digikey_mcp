"""
Custom JMESPath functions for enhanced query capabilities.

This module provides custom JMESPath functions to enable:
- regex_replace(): Text transformation via regex find-and-replace
- int(): String to integer conversion with safe null handling

These functions enable LLMs to construct queries that transform and filter
component values like "100 ohm" → 100 for numeric range comparisons.
"""

import re
import jmespath
from jmespath import functions
from typing import Any, Optional, Union


class CustomFunctions(functions.Functions):
    """Custom JMESPath functions for DigiKey MCP server."""

    @functions.signature(
        {'types': ['string']},
        {'types': ['string']},
        {'types': ['string', 'null']}
    )
    def _func_regex_replace(
        self,
        pattern: str,
        replacement: str,
        value: Optional[str]
    ) -> Optional[str]:
        """
        Perform regex find-and-replace on a string (like sed s/pattern/replacement/).

        Args:
            pattern: Regular expression pattern to match
            replacement: String to replace matches with
            value: Input string to transform

        Returns:
            String with replacements applied, or original value if regex is invalid

        Examples:
            regex_replace(' ohm$', '', '100 ohm') → '100'
            regex_replace('[^0-9]', '', 'R100K') → '100'
            regex_replace('o', 'x', 'foo') → 'fxx'
        """
        if value is None:
            return None
        try:
            return re.sub(pattern, replacement, value)
        except (re.error, TypeError):
            # Invalid regex pattern or null value - return original unchanged
            return value

    @functions.signature({'types': ['string', 'number', 'null']})
    def _func_int(self, value: Union[str, int, float, None]) -> Optional[int]:
        """
        Convert a value to an integer.

        Args:
            value: String or numeric value to convert

        Returns:
            Integer value, or None (JSON null) if conversion fails

        Examples:
            int('100') → 100
            int(42.7) → 42
            int('invalid') → null
            int('') → null

        Note:
            Returning null on failure allows safe filtering:
            Products[?int(Field) != null]
        """
        if value is None:
            return None
        try:
            if isinstance(value, (int, float)):
                return int(value)
            return int(value)
        except (ValueError, TypeError):
            return None


# Create a shared options object with custom functions registered
_custom_options = jmespath.Options(custom_functions=CustomFunctions())


def search_with_custom_functions(expression: str, data: Any) -> Any:
    """
    Execute a JMESPath query with custom functions enabled.

    This is a drop-in replacement for jmespath.search() that includes
    custom regex_replace() and int() functions.

    Args:
        expression: JMESPath query expression
        data: Data to query

    Returns:
        Query result

    Examples:
        >>> data = {"value": "100 ohm"}
        >>> search_with_custom_functions("int(regex_replace(' ohm$', '', value))", data)
        100

        >>> data = {"products": [{"resistance": "50 ohm"}, {"resistance": "150 ohm"}]}
        >>> query = "products[?int(regex_replace(' ohm$', '', resistance)) >= 100]"
        >>> search_with_custom_functions(query, data)
        [{"resistance": "150 ohm"}]
    """
    return jmespath.search(expression, data, options=_custom_options)
