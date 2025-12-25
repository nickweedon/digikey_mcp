"""Bulk operation executor.

Handles execution of multiple operations in parallel or sequential mode.
"""
import inspect
from typing import Dict, List, Callable, Any
from src.bulk.types import ExecutionMode, OperationResult, BulkOperationResponse
from src.bulk.validators import validate_operation
from src.config import logger


class BulkOperationExecutor:
    """Executes multiple DigiKey API operations in a single call.

    Supports parallel (continue on error) and sequential (stop on first error) modes.
    """

    def __init__(self, customer_id: str = "0"):
        """Initialize executor.

        Args:
            customer_id: Default DigiKey Customer ID for operations
        """
        self.customer_id = customer_id
        self.operation_map = self._build_operation_map()

    def _build_operation_map(self) -> Dict[str, Callable]:
        """Build mapping of operation types to their implementation functions.

        Returns:
            Dictionary mapping operation type strings to callable functions
        """
        # Import implementation functions from tool modules
        from src.tools.mylists_tools import (
            _get_all_lists_impl,
            _create_list_impl,
            _get_list_by_id_impl,
            _update_list_name_impl,
            _delete_list_impl,
            _get_parts_by_list_id_impl,
            _add_parts_to_list_impl,
            _get_part_from_list_impl,
            _update_part_in_list_impl,
            _delete_part_from_list_impl,
        )
        from src.tools.product_tools import (
            _keyword_search_impl,
        )

        operation_map = {
            # MyLists operations (fully supported)
            "get_all_lists": _get_all_lists_impl,
            "create_list": _create_list_impl,
            "get_list_by_id": _get_list_by_id_impl,
            "update_list_name": _update_list_name_impl,
            "delete_list": _delete_list_impl,
            "get_parts_by_list_id": _get_parts_by_list_id_impl,
            "add_parts_to_list": _add_parts_to_list_impl,
            "get_part_from_list": _get_part_from_list_impl,
            "update_part_in_list": _update_part_in_list_impl,
            "delete_part_from_list": _delete_part_from_list_impl,
            # Product operations
            "keyword_search": _keyword_search_impl,
        }

        return operation_map

    def execute(
        self,
        operations: List[Dict[str, Any]],
        mode: ExecutionMode
    ) -> BulkOperationResponse:
        """Execute bulk operations.

        Args:
            operations: List of operation dictionaries with 'type' field
            mode: Execution mode (PARALLEL or SEQUENTIAL)

        Returns:
            BulkOperationResponse with results for each operation
        """
        logger.info(
            f"Executing {len(operations)} operations in {mode.value} mode"
        )

        # Execute based on mode
        if mode == ExecutionMode.PARALLEL:
            results = self._execute_parallel(operations)
        else:
            results = self._execute_sequential(operations)

        # Calculate statistics
        successful = sum(1 for r in results if r.status == "success")
        failed = sum(1 for r in results if r.status == "failed")

        logger.info(
            f"Bulk execution complete: {successful} successful, {failed} failed"
        )

        return BulkOperationResponse(
            total=len(operations),
            successful=successful,
            failed=failed,
            execution_mode=mode.value,
            operations=results
        )

    def _execute_parallel(
        self,
        operations: List[Dict[str, Any]]
    ) -> List[OperationResult]:
        """Execute all operations, continue on errors.

        Args:
            operations: List of operation dictionaries

        Returns:
            List of OperationResult for each operation
        """
        results = []

        for index, op in enumerate(operations):
            result = self._execute_operation(op, index)
            results.append(result)

            if result.status == "failed":
                logger.warning(
                    f"Operation {index} ({result.type}) failed: "
                    f"{result.error.get('message') if result.error else 'Unknown error'}"
                )

        return results

    def _execute_sequential(
        self,
        operations: List[Dict[str, Any]]
    ) -> List[OperationResult]:
        """Stop on first error.

        Args:
            operations: List of operation dictionaries

        Returns:
            List of OperationResult up to and including first failure
        """
        results = []

        for index, op in enumerate(operations):
            result = self._execute_operation(op, index)
            results.append(result)

            # Stop on first error
            if result.status == "failed":
                logger.error(
                    f"Operation {index} ({result.type}) failed in sequential mode, "
                    f"stopping execution: "
                    f"{result.error.get('message') if result.error else 'Unknown error'}"
                )
                break

        return results

    def _execute_operation(
        self,
        op_dict: Dict[str, Any],
        index: int
    ) -> OperationResult:
        """Execute a single operation with error capture.

        Args:
            op_dict: Operation dictionary with 'type' and parameters
            index: Zero-based index of this operation

        Returns:
            OperationResult with success/failure status
        """
        op_type = op_dict.get("type", "unknown")

        try:
            # Validate operation
            validate_operation(op_dict)

            # Get implementation function
            func = self.operation_map.get(op_type)
            if not func:
                raise ValueError(f"Unknown operation type: {op_type}")

            # Extract parameters (remove 'type' field)
            params = {k: v for k, v in op_dict.items() if k != "type"}

            # Inject customer_id if function accepts it and it's not already provided
            sig = inspect.signature(func)
            if "customer_id" in sig.parameters and "customer_id" not in params:
                params["customer_id"] = self.customer_id

            # Execute operation
            logger.debug(f"Executing operation {index}: {op_type}")
            result = func(**params)

            return OperationResult(
                index=index,
                type=op_type,
                status="success",
                result=result,
                error=None
            )

        except Exception as e:
            logger.debug(
                f"Operation {index} ({op_type}) failed: {type(e).__name__}: {str(e)}"
            )
            return OperationResult(
                index=index,
                type=op_type,
                status="failed",
                result=None,
                error={
                    "type": type(e).__name__,
                    "message": str(e)
                }
            )
