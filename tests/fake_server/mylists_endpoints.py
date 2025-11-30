"""MyLists API endpoints for fake DigiKey API server.

Simulates DigiKey's MyLists API v1 endpoints.
"""

import secrets
from flask import Blueprint, request, jsonify

from .responses.mylists import (
    SAMPLE_LISTS,
    SAMPLE_PARTS,
    get_list_by_id,
    get_parts_response
)
from .oauth_endpoints import is_valid_token, is_expired_token

mylists_bp = Blueprint("mylists", __name__, url_prefix="/mylists/v1")

# In-memory storage for created lists during tests
_created_lists: dict[str, dict] = {}
_created_parts: dict[str, list] = {}  # list_id -> parts


def _check_auth(req) -> tuple[bool, dict | None]:
    """Check authorization header and return (is_valid, error_response)."""
    auth_header = req.headers.get("Authorization")

    if not auth_header:
        return False, (jsonify({
            "error": "unauthorized",
            "error_description": "Authorization header is required"
        }), 401)

    if is_expired_token(auth_header):
        return False, (jsonify({
            "error": "invalid_token",
            "error_description": "The access token has expired"
        }), 401)

    if not is_valid_token(auth_header):
        return False, (jsonify({
            "error": "invalid_token",
            "error_description": "Invalid access token"
        }), 401)

    return True, None


@mylists_bp.route("/lists", methods=["GET"])
def get_all_lists():
    """Get all lists for the authenticated user."""
    is_valid, error = _check_auth(request)
    if not is_valid:
        return error

    # Combine sample lists with any created during test
    all_lists = SAMPLE_LISTS.copy()
    all_lists.extend(_created_lists.values())

    return jsonify(all_lists)


@mylists_bp.route("/lists", methods=["POST"])
def create_list():
    """Create a new list."""
    is_valid, error = _check_auth(request)
    if not is_valid:
        return error

    data = request.get_json()
    if not data or not data.get("ListName"):
        return jsonify({
            "error": "bad_request",
            "error_description": "ListName is required"
        }), 400

    # Generate a new list ID
    list_id = f"list-{secrets.token_hex(8)}"

    new_list = {
        "ListId": list_id,
        "ListName": data["ListName"],
        "CreatedBy": "testuser@example.com",
        "CustomerId": request.headers.get("X-DIGIKEY-Customer-Id", "0"),
        "TotalParts": 0,
        "DateCreated": "2024-01-01T00:00:00Z",
        "DateModified": "2024-01-01T00:00:00Z",
        "Tags": data.get("Tags", []),
        "ListSettings": {},
        "Source": data.get("Source", "other")
    }

    _created_lists[list_id] = new_list
    _created_parts[list_id] = []

    # Return just the list ID as a string (API behavior)
    return jsonify(list_id), 201


@mylists_bp.route("/lists/<list_id>", methods=["GET"])
def get_list(list_id: str):
    """Get a specific list by ID."""
    is_valid, error = _check_auth(request)
    if not is_valid:
        return error

    # Check created lists first, then sample lists
    lst = _created_lists.get(list_id) or get_list_by_id(list_id)

    if not lst:
        return jsonify({
            "error": "not_found",
            "error_description": f"List '{list_id}' not found"
        }), 404

    result = lst.copy()

    # Include parts if requested
    if request.args.get("includePartsList", "").lower() == "true":
        parts_response = get_parts_response(list_id)
        result["PartsList"] = parts_response["PartsList"]

    return jsonify(result)


@mylists_bp.route("/lists/<list_id>", methods=["DELETE"])
def delete_list(list_id: str):
    """Delete a list."""
    is_valid, error = _check_auth(request)
    if not is_valid:
        return error

    # Check if list exists
    lst = _created_lists.get(list_id) or get_list_by_id(list_id)
    if not lst:
        return jsonify({
            "error": "not_found",
            "error_description": f"List '{list_id}' not found"
        }), 404

    # Remove from created lists if it was created during test
    if list_id in _created_lists:
        del _created_lists[list_id]
    if list_id in _created_parts:
        del _created_parts[list_id]

    return "", 204


@mylists_bp.route("/lists/<list_id>/listName/<new_name>", methods=["PUT"])
def update_list_name(list_id: str, new_name: str):
    """Update a list's name."""
    is_valid, error = _check_auth(request)
    if not is_valid:
        return error

    # Check if list exists
    if list_id in _created_lists:
        _created_lists[list_id]["ListName"] = new_name
        return "", 204

    lst = get_list_by_id(list_id)
    if not lst:
        return jsonify({
            "error": "not_found",
            "error_description": f"List '{list_id}' not found"
        }), 404

    # For sample lists, we can't actually modify them, but return success
    return "", 204


@mylists_bp.route("/lists/<list_id>/parts", methods=["GET"])
def get_parts(list_id: str):
    """Get parts from a list."""
    is_valid, error = _check_auth(request)
    if not is_valid:
        return error

    # Check if list exists
    lst = _created_lists.get(list_id) or get_list_by_id(list_id)
    if not lst:
        return jsonify({
            "error": "not_found",
            "error_description": f"List '{list_id}' not found"
        }), 404

    # Get pagination parameters
    start_index = int(request.args.get("startIndex", 0))
    limit = int(request.args.get("limit", 200))

    # Get parts for this list
    if list_id in _created_parts:
        all_parts = _created_parts[list_id]
    else:
        parts_response = get_parts_response(list_id)
        all_parts = parts_response["PartsList"]

    # Apply pagination
    paginated_parts = all_parts[start_index:start_index + limit]

    return jsonify({
        "TotalParts": len(all_parts),
        "PartsList": paginated_parts
    })


@mylists_bp.route("/lists/<list_id>/parts", methods=["POST"])
def add_parts(list_id: str):
    """Add parts to a list."""
    is_valid, error = _check_auth(request)
    if not is_valid:
        return error

    # Check if list exists
    lst = _created_lists.get(list_id) or get_list_by_id(list_id)
    if not lst:
        return jsonify({
            "error": "not_found",
            "error_description": f"List '{list_id}' not found"
        }), 404

    parts_data = request.get_json()
    if not parts_data or not isinstance(parts_data, list):
        return jsonify({
            "error": "bad_request",
            "error_description": "Request body must be an array of parts"
        }), 400

    # Initialize parts list for this list if needed
    if list_id not in _created_parts:
        _created_parts[list_id] = []

    # Generate unique IDs for added parts
    added_ids = []
    for part in parts_data:
        unique_id = f"part-{secrets.token_hex(8)}"
        added_ids.append(unique_id)

        # Create a minimal part entry
        new_part = {
            "UniqueId": unique_id,
            "PartId": 0,
            "RequestedPartNumber": part.get("RequestedPartNumber", ""),
            "CustomerReference": part.get("CustomerReference", ""),
            "ReferenceDesignator": part.get("ReferenceDesignator", ""),
            "Notes": part.get("Notes", "")
        }
        _created_parts[list_id].append(new_part)

    # Update total parts count
    if list_id in _created_lists:
        _created_lists[list_id]["TotalParts"] = len(_created_parts[list_id])

    return jsonify(added_ids), 201


@mylists_bp.route("/lists/<list_id>/parts/<part_id>", methods=["GET"])
def get_part(list_id: str, part_id: str):
    """Get a specific part from a list."""
    is_valid, error = _check_auth(request)
    if not is_valid:
        return error

    # Check sample parts
    for part in SAMPLE_PARTS:
        if part["UniqueId"] == part_id:
            return jsonify(part)

    # Check created parts
    if list_id in _created_parts:
        for part in _created_parts[list_id]:
            if part["UniqueId"] == part_id:
                return jsonify(part)

    return jsonify({
        "error": "not_found",
        "error_description": f"Part '{part_id}' not found in list '{list_id}'"
    }), 404


@mylists_bp.route("/lists/<list_id>/parts/<part_id>", methods=["DELETE"])
def delete_part(list_id: str, part_id: str):
    """Delete a part from a list."""
    is_valid, error = _check_auth(request)
    if not is_valid:
        return error

    # Check if part exists
    found = False

    if list_id in _created_parts:
        for i, part in enumerate(_created_parts[list_id]):
            if part["UniqueId"] == part_id:
                del _created_parts[list_id][i]
                found = True
                break

    if not found:
        for part in SAMPLE_PARTS:
            if part["UniqueId"] == part_id:
                found = True
                break

    if not found:
        return jsonify({
            "error": "not_found",
            "error_description": f"Part '{part_id}' not found"
        }), 404

    return "", 204


def reset_state():
    """Reset the in-memory state for testing."""
    global _created_lists, _created_parts
    _created_lists = {}
    _created_parts = {}
