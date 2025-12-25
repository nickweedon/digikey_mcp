"""Operation validators for bulk operations.

Each validator function checks that an operation dict has the required fields
and valid parameter types. Validators raise ValueError with descriptive messages.
"""
from typing import Dict, Any, Callable


# MyLists Validators

def _validate_get_all_lists(op: Dict[str, Any]) -> None:
    """Validate get_all_lists - no required params beyond customer_id."""
    pass


def _validate_create_list(op: Dict[str, Any]) -> None:
    """Validate create_list operation."""
    if "list_name" not in op or not op["list_name"]:
        raise ValueError("create_list requires non-empty 'list_name'")


def _validate_get_list_by_id(op: Dict[str, Any]) -> None:
    """Validate get_list_by_id operation."""
    if "list_id" not in op:
        raise ValueError("get_list_by_id requires 'list_id'")


def _validate_update_list_name(op: Dict[str, Any]) -> None:
    """Validate update_list_name operation."""
    if "list_id" not in op:
        raise ValueError("update_list_name requires 'list_id'")
    if "new_name" not in op or not op["new_name"]:
        raise ValueError("update_list_name requires non-empty 'new_name'")


def _validate_delete_list(op: Dict[str, Any]) -> None:
    """Validate delete_list operation."""
    if "list_id" not in op:
        raise ValueError("delete_list requires 'list_id'")


def _validate_get_parts_by_list_id(op: Dict[str, Any]) -> None:
    """Validate get_parts_by_list_id operation."""
    if "list_id" not in op:
        raise ValueError("get_parts_by_list_id requires 'list_id'")


def _validate_add_parts_to_list(op: Dict[str, Any]) -> None:
    """Validate add_parts_to_list operation."""
    if "list_id" not in op:
        raise ValueError("add_parts_to_list requires 'list_id'")
    if "parts" not in op or not isinstance(op["parts"], list):
        raise ValueError("add_parts_to_list requires 'parts' as a list")
    if len(op["parts"]) == 0:
        raise ValueError("add_parts_to_list requires at least one part")


def _validate_get_part_from_list(op: Dict[str, Any]) -> None:
    """Validate get_part_from_list operation."""
    if "list_id" not in op:
        raise ValueError("get_part_from_list requires 'list_id'")
    if "part_id" not in op:
        raise ValueError("get_part_from_list requires 'part_id'")


def _validate_update_part_in_list(op: Dict[str, Any]) -> None:
    """Validate update_part_in_list operation."""
    if "list_id" not in op:
        raise ValueError("update_part_in_list requires 'list_id'")
    if "part_id" not in op:
        raise ValueError("update_part_in_list requires 'part_id'")
    if "part_data" not in op or not isinstance(op["part_data"], dict):
        raise ValueError("update_part_in_list requires 'part_data' as a dict")


def _validate_delete_part_from_list(op: Dict[str, Any]) -> None:
    """Validate delete_part_from_list operation."""
    if "list_id" not in op:
        raise ValueError("delete_part_from_list requires 'list_id'")
    if "part_id" not in op:
        raise ValueError("delete_part_from_list requires 'part_id'")


# Product Validators

def _validate_keyword_search(op: Dict[str, Any]) -> None:
    """Validate keyword_search operation."""
    if "keywords" not in op or not op["keywords"]:
        raise ValueError("keyword_search requires non-empty 'keywords'")

    # Validate limit if provided
    if "limit" in op:
        limit = op["limit"]
        if not isinstance(limit, int) or limit < 1 or limit > 1000:
            raise ValueError("keyword_search 'limit' must be an integer between 1 and 1000")

    # Validate offset if provided
    if "offset" in op:
        offset = op["offset"]
        if not isinstance(offset, int) or offset < 0:
            raise ValueError("keyword_search 'offset' must be a non-negative integer")


# Validator Registry

VALIDATOR_MAP: Dict[str, Callable[[Dict[str, Any]], None]] = {
    # MyLists operations (fully supported)
    "get_all_lists": _validate_get_all_lists,
    "create_list": _validate_create_list,
    "get_list_by_id": _validate_get_list_by_id,
    "update_list_name": _validate_update_list_name,
    "delete_list": _validate_delete_list,
    "get_parts_by_list_id": _validate_get_parts_by_list_id,
    "add_parts_to_list": _validate_add_parts_to_list,
    "get_part_from_list": _validate_get_part_from_list,
    "update_part_in_list": _validate_update_part_in_list,
    "delete_part_from_list": _validate_delete_part_from_list,
    # Product operations
    "keyword_search": _validate_keyword_search,
}


def validate_operation(op_dict: Dict[str, Any]) -> None:
    """Validate an operation dictionary.

    Args:
        op_dict: Operation dictionary with 'type' field and operation-specific params

    Raises:
        ValueError: If operation is invalid with descriptive message
    """
    op_type = op_dict.get("type")

    if not op_type:
        raise ValueError("Operation missing 'type' field")

    # Get validator for this operation type
    validator = VALIDATOR_MAP.get(op_type)
    if not validator:
        raise ValueError(f"Unknown operation type: {op_type}")

    # Run type-specific validation
    validator(op_dict)
