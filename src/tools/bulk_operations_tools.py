"""Bulk Operations MCP Tool

Allows executing multiple DigiKey MyLists operations in a single call.
Supports parallel (continue on error) and sequential (stop on first error) execution modes.
"""
from typing import List, Dict, Any, Literal
from src.bulk.executor import BulkOperationExecutor
from src.bulk.types import ExecutionMode
from src.config import logger


def register_bulk_operations_tools(mcp):
    """Register bulk operations MCP tool."""

    @mcp.tool()
    def bulk_operations(
        operations: List[Dict[str, Any]],
        execution_mode: Literal["parallel", "sequential"] = "parallel",
        customer_id: str = "0"
    ) -> Dict[str, Any]:
        """Execute multiple DigiKey operations in a single call.

        Supports MyLists operations (10 total) and Product operations (1 total)
        for efficient batch processing. Operations can be executed in parallel
        (continue on errors) or sequential (stop on first error) mode.

        **Supported MyLists Operations:**
        - get_all_lists: Retrieve all lists
        - create_list: Create a new list
        - get_list_by_id: Get list details
        - update_list_name: Rename a list
        - delete_list: Delete a list (destructive)
        - get_parts_by_list_id: Get parts from a list
        - add_parts_to_list: Add parts to a list
        - get_part_from_list: Get a specific part
        - update_part_in_list: Update part metadata
        - delete_part_from_list: Delete a part (destructive)

        **Supported Product Operations:**
        - keyword_search: Search products by keyword with optional filters

        **Execution Modes:**
        - parallel: Execute all operations, continue on errors, report all results
        - sequential: Stop on first error, return results up to failure point

        Args:
            operations: List of operation dictionaries. Each must have:
                       - type: Operation type string (e.g., "create_list", "add_parts_to_list")
                       - Additional parameters specific to the operation type
            execution_mode: How to handle errors - "parallel" or "sequential" (default: "parallel")
            customer_id: DigiKey Customer ID (default: "0")

        Returns:
            Dictionary with structure:
            {
                "total": int,              # Total operations requested
                "successful": int,         # Number that succeeded
                "failed": int,             # Number that failed
                "execution_mode": str,     # Mode used
                "operations": [            # Results for each operation
                    {
                        "index": int,          # 0-based index
                        "type": str,           # Operation type
                        "status": "success"|"failed",
                        "result": {...}|None,  # Operation result if successful
                        "error": {...}|None    # Error details if failed
                    }
                ]
            }

        Example - Sequential workflow (create list, add parts):
            operations = [
                {
                    "type": "create_list",
                    "list_name": "Voltage Regulator BOM"
                },
                {
                    "type": "add_parts_to_list",
                    "list_id": "<use result from operation 0>",
                    "parts": [
                        {"requested_part_number": "LM7805CT-ND"},
                        {"requested_part_number": "C1206C104K5RACTU"}
                    ]
                }
            ]
            result = bulk_operations(operations, execution_mode="sequential")

        Example - Parallel operations (update multiple parts):
            operations = [
                {
                    "type": "update_part_in_list",
                    "list_id": "abc123",
                    "part_id": "part1",
                    "part_data": {"notes": "Updated note 1"}
                },
                {
                    "type": "update_part_in_list",
                    "list_id": "abc123",
                    "part_id": "part2",
                    "part_data": {"notes": "Updated note 2"}
                },
                {
                    "type": "update_part_in_list",
                    "list_id": "abc123",
                    "part_id": "part3",
                    "part_data": {"notes": "Updated note 3"}
                }
            ]
            result = bulk_operations(operations, execution_mode="parallel")

        Example - Product searches (parallel):
            operations = [
                {
                    "type": "keyword_search",
                    "keywords": "arduino uno",
                    "limit": 10
                },
                {
                    "type": "keyword_search",
                    "keywords": "raspberry pi 4",
                    "limit": 10,
                    "search_options": "InStock"
                },
                {
                    "type": "keyword_search",
                    "keywords": "resistor 10k",
                    "limit": 20,
                    "manufacturer_id": "1234"
                }
            ]
            result = bulk_operations(operations, execution_mode="parallel")

        Note:
            - All MyLists operations require user authentication via oauth_start_login()
            - Product operations (keyword_search) do NOT require authentication
            - Sequential mode is useful for dependent operations
            - Parallel mode is useful for independent batch updates
        """
        logger.info(
            f"Bulk operations: {len(operations)} operations in {execution_mode} mode"
        )

        # Create executor
        executor = BulkOperationExecutor(customer_id)

        # Convert execution_mode string to enum
        mode = ExecutionMode(execution_mode)

        # Execute operations
        response = executor.execute(operations, mode)

        # Return as dictionary
        return response.to_dict()
