"""Product Search API endpoints for fake DigiKey API server.

Simulates DigiKey's Product Search API v4 endpoints.
"""

from flask import Blueprint, request, jsonify

from .responses.products import (
    SAMPLE_PRODUCTS,
    SAMPLE_MANUFACTURERS,
    SAMPLE_CATEGORIES,
    SAMPLE_PRODUCT_DETAILS,
    SAMPLE_SUBSTITUTIONS,
    SAMPLE_MEDIA,
    SAMPLE_PRICING,
    SAMPLE_DIGIREEL_PRICING,
    get_keyword_search_response,
    get_category_by_id,
    get_product_by_number,
)

products_bp = Blueprint("products", __name__, url_prefix="/products/v4")


@products_bp.route("/search/keyword", methods=["POST"])
def keyword_search():
    """Keyword search for products."""
    data = request.get_json() or {}

    keywords = data.get("Keywords", "")
    limit = data.get("Limit", 5)

    if not keywords:
        return jsonify({
            "error": "bad_request",
            "error_description": "Keywords parameter is required"
        }), 400

    response = get_keyword_search_response(keywords, limit)
    return jsonify(response)


@products_bp.route("/search/<product_number>/productdetails", methods=["GET"])
def product_details(product_number: str):
    """Get product details by part number."""
    product = get_product_by_number(product_number)

    if not product:
        # Return sample details if product not found but use the requested part number
        details = SAMPLE_PRODUCT_DETAILS.copy()
        details["RequestedPartNumber"] = product_number
        return jsonify(details)

    # Build a details response from the product
    details = {
        "DigiKeyPartNumber": product["ProductVariations"][0]["DigiKeyProductNumber"] if product.get("ProductVariations") else "",
        "ManufacturerPartNumber": product["ManufacturerProductNumber"],
        "Manufacturer": product["Manufacturer"],
        "Description": product["Description"],
        "ProductUrl": product["ProductUrl"],
        "DatasheetUrl": product.get("DatasheetUrl"),
        "PhotoUrl": product.get("PhotoUrl"),
        "UnitPrice": product["UnitPrice"],
        "QuantityAvailable": product["QuantityAvailable"],
        "MinimumOrderQuantity": product["ProductVariations"][0]["MinimumOrderQuantity"] if product.get("ProductVariations") else 1,
        "StandardPackage": product["ProductVariations"][0]["StandardPackage"] if product.get("ProductVariations") else 1,
        "ProductStatus": product["ProductStatus"],
        "Category": product.get("Category"),
        "Parameters": product.get("Parameters", []),
        "StandardPricing": product["ProductVariations"][0]["StandardPricing"] if product.get("ProductVariations") else [],
        "BackOrderNotAllowed": product["BackOrderNotAllowed"],
        "NormallyStocking": product["NormallyStocking"],
        "Discontinued": product["Discontinued"],
        "EndOfLife": product["EndOfLife"],
        "Ncnr": product["Ncnr"],
        "ReachStatus": "REACH Unaffected",
        "RohsStatus": "RoHS Compliant",
        "LeadStatus": "Lead Free",
        "HtsusCode": "8533.21.0030",
        "TariffDescription": "",
        "Eccn": "EAR99"
    }

    return jsonify(details)


@products_bp.route("/search/manufacturers", methods=["GET"])
def get_manufacturers():
    """Get all manufacturers."""
    return jsonify({
        "Manufacturers": SAMPLE_MANUFACTURERS,
        "ManufacturersCount": len(SAMPLE_MANUFACTURERS)
    })


@products_bp.route("/search/categories", methods=["GET"])
def get_categories():
    """Get all categories."""
    return jsonify({
        "Categories": SAMPLE_CATEGORIES,
        "CategoriesCount": len(SAMPLE_CATEGORIES)
    })


@products_bp.route("/search/categories/<category_id>", methods=["GET"])
def get_category(category_id: str):
    """Get a specific category by ID."""
    try:
        cat_id = int(category_id)
    except ValueError:
        return jsonify({
            "error": "bad_request",
            "error_description": "Invalid category ID"
        }), 400

    category = get_category_by_id(cat_id)

    if not category:
        return jsonify({
            "error": "not_found",
            "error_description": f"Category '{category_id}' not found"
        }), 404

    return jsonify(category)


@products_bp.route("/search/<product_number>/substitutions", methods=["GET"])
def get_substitutions(product_number: str):
    """Get product substitutions."""
    limit = request.args.get("limit", 10, type=int)

    # Return sample substitutions (modified to match requested product)
    response = SAMPLE_SUBSTITUTIONS.copy()
    response["RequestedProductNumber"] = product_number

    # Limit the products if requested
    if limit < len(response["Products"]):
        response["Products"] = response["Products"][:limit]
        response["ProductsCount"] = limit

    return jsonify(response)


@products_bp.route("/search/<product_number>/media", methods=["GET"])
def get_media(product_number: str):
    """Get product media."""
    response = SAMPLE_MEDIA.copy()
    response["DigiKeyPartNumber"] = product_number
    return jsonify(response)


@products_bp.route("/search/<product_number>/productpricing", methods=["GET"])
def get_pricing(product_number: str):
    """Get product pricing."""
    requested_quantity = request.args.get("requestedQuantity", 1, type=int)

    response = SAMPLE_PRICING.copy()
    response["DigiKeyPartNumber"] = product_number
    response["RequestedQuantity"] = requested_quantity

    # Calculate price based on quantity breaks
    unit_price = response["StandardPricing"][0]["UnitPrice"]
    for tier in response["StandardPricing"]:
        if requested_quantity >= tier["BreakQuantity"]:
            unit_price = tier["UnitPrice"]

    response["CalculatedPrice"] = unit_price
    response["ExtendedPrice"] = round(unit_price * requested_quantity, 2)

    return jsonify(response)


@products_bp.route("/search/<product_number>/digireelpricing", methods=["GET"])
def get_digireel_pricing(product_number: str):
    """Get DigiReel pricing."""
    requested_quantity = request.args.get("requestedQuantity", 1, type=int)

    response = SAMPLE_DIGIREEL_PRICING.copy()
    response["DigiKeyPartNumber"] = product_number
    response["RequestedQuantity"] = requested_quantity

    # Calculate price
    unit_price = response["UnitPrice"]
    extended_price = round(unit_price * requested_quantity, 2)
    total_price = extended_price + response["DigiReelFee"]

    response["ExtendedPrice"] = extended_price
    response["TotalPrice"] = total_price

    return jsonify(response)
