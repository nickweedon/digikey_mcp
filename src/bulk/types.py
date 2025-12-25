"""Type definitions for bulk operations."""
from enum import Enum
from dataclasses import dataclass
from typing import Any, Optional, Dict, List


class ExecutionMode(str, Enum):
    """Execution mode for bulk operations."""
    PARALLEL = "parallel"
    SEQUENTIAL = "sequential"


@dataclass
class OperationResult:
    """Result of a single operation in a bulk execution.

    Attributes:
        index: Zero-based index of the operation
        type: Operation type string (e.g., "create_list", "keyword_search")
        status: "success" or "failed"
        result: Operation result data if successful, None if failed
        error: Error details if failed, None if successful
    """
    index: int
    type: str
    status: str  # "success" | "failed"
    result: Optional[Any] = None
    error: Optional[Dict[str, Any]] = None


@dataclass
class BulkOperationResponse:
    """Response from a bulk operation execution.

    Attributes:
        total: Total number of operations requested
        successful: Number of operations that succeeded
        failed: Number of operations that failed
        execution_mode: Mode used ("parallel" or "sequential")
        operations: List of individual operation results
    """
    total: int
    successful: int
    failed: int
    execution_mode: str
    operations: List[OperationResult]

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for MCP response."""
        return {
            "total": self.total,
            "successful": self.successful,
            "failed": self.failed,
            "execution_mode": self.execution_mode,
            "operations": [
                {
                    "index": op.index,
                    "type": op.type,
                    "status": op.status,
                    "result": op.result,
                    "error": op.error
                }
                for op in self.operations
            ]
        }
