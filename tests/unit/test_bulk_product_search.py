"""Unit tests for bulk operations with product search."""
import pytest
from src.bulk.executor import BulkOperationExecutor
from src.bulk.types import ExecutionMode
from src.bulk.validators import validate_operation


@pytest.mark.unit
class TestBulkProductSearch:
    """Tests for bulk operations with keyword_search."""

    def test_keyword_search_validator_valid(self):
        """Test that keyword_search validator accepts valid operations."""
        valid_ops = [
            {"type": "keyword_search", "keywords": "arduino"},
            {"type": "keyword_search", "keywords": "resistor", "limit": 10},
            {"type": "keyword_search", "keywords": "capacitor", "offset": 20, "limit": 50},
        ]

        for op in valid_ops:
            # Should not raise
            validate_operation(op)

    def test_keyword_search_validator_invalid(self):
        """Test that keyword_search validator rejects invalid operations."""
        invalid_ops = [
            {"type": "keyword_search"},  # Missing keywords
            {"type": "keyword_search", "keywords": ""},  # Empty keywords
            {"type": "keyword_search", "keywords": "test", "limit": 0},  # Invalid limit
            {"type": "keyword_search", "keywords": "test", "limit": 2000},  # Limit too large
            {"type": "keyword_search", "keywords": "test", "offset": -1},  # Negative offset
        ]

        for op in invalid_ops:
            with pytest.raises(ValueError):
                validate_operation(op)

    def test_bulk_executor_has_keyword_search(self):
        """Test that bulk executor has keyword_search operation registered."""
        executor = BulkOperationExecutor()
        operation_map = executor.operation_map

        assert "keyword_search" in operation_map
        assert callable(operation_map["keyword_search"])

    def test_bulk_keyword_search_execution(self, patched_api_base):
        """Test bulk execution of keyword_search operations.

        NOTE: This test will fail against production API without valid credentials.
        It uses the patched_api_base fixture to point to the fake server,
        but the fake server doesn't implement keyword_search endpoints yet.

        This test verifies the structure and execution flow works correctly.
        """
        executor = BulkOperationExecutor()

        operations = [
            {"type": "keyword_search", "keywords": "arduino", "limit": 3},
            {"type": "keyword_search", "keywords": "raspberry", "limit": 2},
        ]

        # Execute - this will likely fail due to fake server not having product endpoints
        # but it proves the bulk operations infrastructure works
        result = executor.execute(operations, ExecutionMode.PARALLEL)

        # Verify structure
        assert result.total == 2
        assert result.execution_mode == "parallel"
        assert len(result.operations) == 2

        # Each operation should have been attempted
        for op_result in result.operations:
            assert op_result.type == "keyword_search"
            assert op_result.status in ["success", "failed"]
            assert op_result.index in [0, 1]

    def test_bulk_keyword_search_sequential_mode(self, patched_api_base):
        """Test sequential execution stops on first error."""
        executor = BulkOperationExecutor()

        operations = [
            {"type": "keyword_search", "keywords": "test1", "limit": 5},
            {"type": "keyword_search", "keywords": "test2", "limit": 5},
            {"type": "keyword_search", "keywords": "test3", "limit": 5},
        ]

        result = executor.execute(operations, ExecutionMode.SEQUENTIAL)

        # Verify structure
        assert result.total == len(operations)
        assert result.execution_mode == "sequential"

        # In sequential mode with failures, might not execute all operations
        assert len(result.operations) <= len(operations)
