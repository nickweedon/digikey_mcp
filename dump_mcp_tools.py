#!/usr/bin/env python3
"""Dump MCP tools/list output in a readable format.

This script lists all tools registered with the DigiKey MCP server
and formats the output for readability.
"""

import asyncio
import json
import sys
from typing import Any


def format_value(value: Any, indent: int = 4) -> str:
    """Format a value for display, pretty-printing dicts/lists as JSON."""
    if isinstance(value, (dict, list)):
        return json.dumps(value, indent=indent, default=str)
    elif isinstance(value, set):
        return json.dumps(list(value), indent=indent)
    elif value is None:
        return "null"
    elif callable(value):
        # For function references, show the qualified name
        return f"<function {value.__qualname__}>"
    else:
        return repr(value)


def dump_tool(tool, index: int) -> str:
    """Format a single tool for display."""
    lines = []
    lines.append("=" * 80)
    lines.append(f"TOOL #{index + 1}: {tool.name}")
    lines.append("=" * 80)
    lines.append("")

    # Name
    lines.append(f"name: {tool.name}")
    lines.append("")

    # Title (if different from name)
    if hasattr(tool, 'title') and tool.title:
        lines.append(f"title: {tool.title}")
        lines.append("")

    # Description - preserve formatting
    lines.append("description: |")
    for line in tool.description.split("\n"):
        lines.append(f"    {line}")
    lines.append("")

    # Icons
    if hasattr(tool, 'icons') and tool.icons:
        lines.append(f"icons: {format_value(tool.icons)}")
        lines.append("")

    # Tags
    lines.append(f"tags: {format_value(tool.tags)}")
    lines.append("")

    # Meta
    if hasattr(tool, 'meta') and tool.meta:
        lines.append("meta: |")
        meta_json = json.dumps(tool.meta, indent=4, default=str)
        for line in meta_json.split("\n"):
            lines.append(f"    {line}")
        lines.append("")

    # Enabled
    lines.append(f"enabled: {tool.enabled}")
    lines.append("")

    # Parameters (Input Schema)
    lines.append("parameters (inputSchema): |")
    params_json = json.dumps(tool.parameters, indent=4, default=str)
    for line in params_json.split("\n"):
        lines.append(f"    {line}")
    lines.append("")

    # Output Schema
    if hasattr(tool, 'output_schema') and tool.output_schema:
        lines.append("output_schema: |")
        output_json = json.dumps(tool.output_schema, indent=4, default=str)
        for line in output_json.split("\n"):
            lines.append(f"    {line}")
        lines.append("")
    else:
        lines.append("output_schema: null")
        lines.append("")

    # Annotations
    lines.append(f"annotations: {format_value(tool.annotations)}")
    lines.append("")

    # Serializer
    lines.append(f"serializer: {format_value(tool.serializer)}")
    lines.append("")

    # Function reference
    lines.append(f"fn: {format_value(tool.fn)}")
    lines.append("")

    return "\n".join(lines)


async def get_tools():
    """Fetch tools from the MCP server."""
    from digikey_mcp_server import mcp
    return await mcp.get_tools()


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Dump MCP tools/list output in a readable format"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file (default: stdout)",
        default=None
    )
    parser.add_argument(
        "-t", "--tool",
        help="Filter to a specific tool by name",
        default=None
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of formatted text"
    )

    args = parser.parse_args()

    # Suppress logging output
    import logging
    logging.getLogger().setLevel(logging.CRITICAL)

    # Fetch tools (returns dict keyed by tool name)
    tools_dict = asyncio.run(get_tools())
    tools = list(tools_dict.values())

    # Filter if requested
    if args.tool:
        if args.tool in tools_dict:
            tools = [tools_dict[args.tool]]
        else:
            print(f"Error: Tool '{args.tool}' not found", file=sys.stderr)
            print(f"Available tools: {', '.join(sorted(tools_dict.keys()))}", file=sys.stderr)
            sys.exit(1)

    # Format output
    if args.json:
        output_data = []
        for tool in tools:
            tool_dict = {
                "name": tool.name,
                "title": getattr(tool, 'title', None),
                "description": tool.description,
                "icons": getattr(tool, 'icons', None),
                "tags": list(tool.tags) if tool.tags else [],
                "meta": getattr(tool, 'meta', None),
                "enabled": tool.enabled,
                "parameters": tool.parameters,
                "output_schema": getattr(tool, 'output_schema', None),
                "annotations": tool.annotations,
                "serializer": str(tool.serializer) if tool.serializer else None,
                "fn": tool.fn.__qualname__ if tool.fn else None
            }
            output_data.append(tool_dict)
        output = json.dumps(output_data, indent=2, default=str)
    else:
        output_lines = []
        output_lines.append("# MCP Tools List")
        output_lines.append(f"# Total tools: {len(tools)}")
        output_lines.append("")

        for i, tool in enumerate(tools):
            output_lines.append(dump_tool(tool, i))

        output = "\n".join(output_lines)

    # Write output
    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Output written to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
