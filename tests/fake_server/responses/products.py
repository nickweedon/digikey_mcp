"""Sample Product API response data for fake DigiKey API server.

These responses are based on the DigiKey Product Search API v4 documentation
and are used for testing purposes.
"""

from typing import Any, Dict, List

# Sample product for keyword search
SAMPLE_PRODUCTS: List[Dict[str, Any]] = [
    {
        "Description": {
            "ProductDescription": "RES SMD 10K OHM 5% 1/8W 0805",
            "DetailedDescription": "10 kOhms +/-5% 0.125W, 1/8W Chip Resistor 0805 (2012 Metric) Automotive AEC-Q200 Thick Film"
        },
        "Manufacturer": {
            "Id": 447,
            "Name": "Stackpole Electronics Inc"
        },
        "ManufacturerProductNumber": "RMCF0805JT10K0",
        "UnitPrice": 0.10,
        "ProductUrl": "https://www.digikey.com/en/products/detail/stackpole-electronics-inc/RMCF0805JT10K0/1942531",
        "DatasheetUrl": "https://www.seielect.com/catalog/sei-rmcf_rmcp.pdf",
        "PhotoUrl": "https://mm.digikey.com/Volume0/opasdata/d220001/medias/images/1702/MFG_RMCF%20SERIES.jpg",
        "PrimaryVideoUrl": None,
        "ProductVariations": [
            {
                "DigiKeyProductNumber": "RMCF0805JT10K0CT-ND",
                "PackageType": {
                    "Id": 1,
                    "Name": "Cut Tape"
                },
                "StandardPricing": [
                    {"BreakQuantity": 1, "UnitPrice": 0.10, "TotalPrice": 0.10},
                    {"BreakQuantity": 10, "UnitPrice": 0.039, "TotalPrice": 0.39},
                    {"BreakQuantity": 100, "UnitPrice": 0.022, "TotalPrice": 2.20}
                ],
                "MyPricing": [],
                "MarketPlace": False,
                "QuantityAvailableforPackageType": 4500000,
                "MinimumOrderQuantity": 1,
                "StandardPackage": 5000,
                "Supplier": None,
                "TariffActive": False,
                "MaxQuantityForDistribution": None,
                "DigiReelFee": 7.00
            },
            {
                "DigiKeyProductNumber": "RMCF0805JT10K0TR-ND",
                "PackageType": {
                    "Id": 2,
                    "Name": "Tape & Reel"
                },
                "StandardPricing": [
                    {"BreakQuantity": 5000, "UnitPrice": 0.0088, "TotalPrice": 44.00}
                ],
                "MyPricing": [],
                "MarketPlace": False,
                "QuantityAvailableforPackageType": 4500000,
                "MinimumOrderQuantity": 5000,
                "StandardPackage": 5000,
                "Supplier": None,
                "TariffActive": False,
                "MaxQuantityForDistribution": None,
                "DigiReelFee": None
            }
        ],
        "QuantityAvailable": 4500000,
        "ProductStatus": {
            "Id": 0,
            "Status": "Active"
        },
        "BackOrderNotAllowed": False,
        "NormallyStocking": True,
        "Discontinued": False,
        "EndOfLife": False,
        "Ncnr": False,
        "Parameters": [
            {"ParameterId": 1, "ParameterText": "Resistance", "ParameterType": "Text", "ValueId": "10000", "ValueText": "10 kOhms"},
            {"ParameterId": 2, "ParameterText": "Tolerance", "ParameterType": "Text", "ValueId": "5", "ValueText": "+/-5%"},
            {"ParameterId": 3, "ParameterText": "Power (Watts)", "ParameterType": "Text", "ValueId": "0.125", "ValueText": "0.125W, 1/8W"},
            {"ParameterId": 4, "ParameterText": "Package / Case", "ParameterType": "Text", "ValueId": "0805", "ValueText": "0805 (2012 Metric)"}
        ],
        "Category": {
            "CategoryId": 52,
            "ParentId": 51,
            "Name": "Chip Resistor - Surface Mount",
            "ProductCount": 125000,
            "NewProductCount": 500,
            "ImageUrl": None
        },
        "BaseProductNumber": "RMCF0805JT",
        "DateLastBuyChance": None,
        "ManufacturerLeadWeeks": None,
        "ManufacturerPublicQuantity": None
    },
    {
        "Description": {
            "ProductDescription": "CAP CER 0.1UF 50V X7R 0603",
            "DetailedDescription": "0.1 uF +/-10% 50V Ceramic Capacitor X7R 0603 (1608 Metric)"
        },
        "Manufacturer": {
            "Id": 556,
            "Name": "Samsung Electro-Mechanics"
        },
        "ManufacturerProductNumber": "CL10B104KB8NNNC",
        "UnitPrice": 0.024,
        "ProductUrl": "https://www.digikey.com/en/products/detail/samsung-electro-mechanics/CL10B104KB8NNNC/399841",
        "DatasheetUrl": "https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/35/CL10B104KB8NNNC.pdf",
        "PhotoUrl": "https://mm.digikey.com/Volume0/opasdata/d220001/medias/images/2346/MFG_CL.jpg",
        "PrimaryVideoUrl": None,
        "ProductVariations": [
            {
                "DigiKeyProductNumber": "1276-1006-1-ND",
                "PackageType": {
                    "Id": 1,
                    "Name": "Cut Tape"
                },
                "StandardPricing": [
                    {"BreakQuantity": 1, "UnitPrice": 0.024, "TotalPrice": 0.024},
                    {"BreakQuantity": 10, "UnitPrice": 0.018, "TotalPrice": 0.18},
                    {"BreakQuantity": 100, "UnitPrice": 0.011, "TotalPrice": 1.10}
                ],
                "MyPricing": [],
                "MarketPlace": False,
                "QuantityAvailableforPackageType": 12000000,
                "MinimumOrderQuantity": 1,
                "StandardPackage": 4000,
                "Supplier": None,
                "TariffActive": False,
                "MaxQuantityForDistribution": None,
                "DigiReelFee": 7.00
            }
        ],
        "QuantityAvailable": 12000000,
        "ProductStatus": {
            "Id": 0,
            "Status": "Active"
        },
        "BackOrderNotAllowed": False,
        "NormallyStocking": True,
        "Discontinued": False,
        "EndOfLife": False,
        "Ncnr": False,
        "Parameters": [
            {"ParameterId": 10, "ParameterText": "Capacitance", "ParameterType": "Text", "ValueId": "100nF", "ValueText": "100nF"},
            {"ParameterId": 11, "ParameterText": "Voltage - Rated", "ParameterType": "Text", "ValueId": "50V", "ValueText": "50V"},
            {"ParameterId": 12, "ParameterText": "Temperature Coefficient", "ParameterType": "Text", "ValueId": "X7R", "ValueText": "X7R"}
        ],
        "Category": {
            "CategoryId": 58,
            "ParentId": 57,
            "Name": "Ceramic Capacitors",
            "ProductCount": 250000,
            "NewProductCount": 1200,
            "ImageUrl": None
        },
        "BaseProductNumber": "CL10B104",
        "DateLastBuyChance": None,
        "ManufacturerLeadWeeks": None,
        "ManufacturerPublicQuantity": None
    }
]

# Sample manufacturer list
SAMPLE_MANUFACTURERS: List[Dict[str, Any]] = [
    {"Id": 447, "Name": "Stackpole Electronics Inc"},
    {"Id": 556, "Name": "Samsung Electro-Mechanics"},
    {"Id": 141, "Name": "Texas Instruments"},
    {"Id": 311, "Name": "Microchip Technology"},
    {"Id": 873, "Name": "Murata Electronics"},
]

# Sample category tree
SAMPLE_CATEGORIES: List[Dict[str, Any]] = [
    {
        "CategoryId": 51,
        "ParentId": 0,
        "Name": "Resistors",
        "ProductCount": 500000,
        "NewProductCount": 2000,
        "ImageUrl": "https://mm.digikey.com/category/resistors.jpg",
        "ChildCategories": [
            {
                "CategoryId": 52,
                "ParentId": 51,
                "Name": "Chip Resistor - Surface Mount",
                "ProductCount": 125000,
                "NewProductCount": 500,
                "ImageUrl": None,
                "ChildCategories": []
            }
        ]
    },
    {
        "CategoryId": 57,
        "ParentId": 0,
        "Name": "Capacitors",
        "ProductCount": 750000,
        "NewProductCount": 3000,
        "ImageUrl": "https://mm.digikey.com/category/capacitors.jpg",
        "ChildCategories": [
            {
                "CategoryId": 58,
                "ParentId": 57,
                "Name": "Ceramic Capacitors",
                "ProductCount": 250000,
                "NewProductCount": 1200,
                "ImageUrl": None,
                "ChildCategories": []
            }
        ]
    }
]

# Sample product details response
SAMPLE_PRODUCT_DETAILS: Dict[str, Any] = {
    "DigiKeyPartNumber": "RMCF0805JT10K0CT-ND",
    "ManufacturerPartNumber": "RMCF0805JT10K0",
    "Manufacturer": {
        "Id": 447,
        "Name": "Stackpole Electronics Inc"
    },
    "Description": {
        "ProductDescription": "RES SMD 10K OHM 5% 1/8W 0805",
        "DetailedDescription": "10 kOhms +/-5% 0.125W, 1/8W Chip Resistor 0805 (2012 Metric) Automotive AEC-Q200 Thick Film"
    },
    "ProductUrl": "https://www.digikey.com/en/products/detail/stackpole-electronics-inc/RMCF0805JT10K0/1942531",
    "DatasheetUrl": "https://www.seielect.com/catalog/sei-rmcf_rmcp.pdf",
    "PhotoUrl": "https://mm.digikey.com/Volume0/opasdata/d220001/medias/images/1702/MFG_RMCF%20SERIES.jpg",
    "UnitPrice": 0.10,
    "QuantityAvailable": 4500000,
    "MinimumOrderQuantity": 1,
    "StandardPackage": 5000,
    "ProductStatus": {
        "Id": 0,
        "Status": "Active"
    },
    "Category": {
        "CategoryId": 52,
        "ParentId": 51,
        "Name": "Chip Resistor - Surface Mount",
        "ProductCount": 125000,
        "NewProductCount": 500,
        "ImageUrl": None
    },
    "Parameters": [
        {"ParameterId": 1, "ParameterText": "Resistance", "ParameterType": "Text", "ValueId": "10000", "ValueText": "10 kOhms"},
        {"ParameterId": 2, "ParameterText": "Tolerance", "ParameterType": "Text", "ValueId": "5", "ValueText": "+/-5%"},
        {"ParameterId": 3, "ParameterText": "Power (Watts)", "ParameterType": "Text", "ValueId": "0.125", "ValueText": "0.125W, 1/8W"},
        {"ParameterId": 4, "ParameterText": "Package / Case", "ParameterType": "Text", "ValueId": "0805", "ValueText": "0805 (2012 Metric)"}
    ],
    "StandardPricing": [
        {"BreakQuantity": 1, "UnitPrice": 0.10, "TotalPrice": 0.10},
        {"BreakQuantity": 10, "UnitPrice": 0.039, "TotalPrice": 0.39},
        {"BreakQuantity": 100, "UnitPrice": 0.022, "TotalPrice": 2.20}
    ],
    "BackOrderNotAllowed": False,
    "NormallyStocking": True,
    "Discontinued": False,
    "EndOfLife": False,
    "Ncnr": False,
    "ReachStatus": "REACH Unaffected",
    "RohsStatus": "RoHS Compliant",
    "LeadStatus": "Lead Free",
    "HtsusCode": "8533.21.0030",
    "TariffDescription": "",
    "Eccn": "EAR99"
}

# Sample substitutions response
SAMPLE_SUBSTITUTIONS: Dict[str, Any] = {
    "Products": [
        {
            "Description": {
                "ProductDescription": "RES SMD 10K OHM 1% 1/8W 0805",
                "DetailedDescription": "10 kOhms +/-1% 0.125W Chip Resistor 0805"
            },
            "Manufacturer": {
                "Id": 447,
                "Name": "Stackpole Electronics Inc"
            },
            "ManufacturerProductNumber": "RMCF0805FT10K0",
            "UnitPrice": 0.12,
            "ProductUrl": "https://www.digikey.com/products/detail/RMCF0805FT10K0",
            "ProductVariations": [
                {
                    "DigiKeyProductNumber": "RMCF0805FT10K0CT-ND",
                    "PackageType": {"Id": 1, "Name": "Cut Tape"},
                    "StandardPricing": [{"BreakQuantity": 1, "UnitPrice": 0.12, "TotalPrice": 0.12}],
                    "MyPricing": [],
                    "MarketPlace": False,
                    "QuantityAvailableforPackageType": 2000000,
                    "MinimumOrderQuantity": 1,
                    "StandardPackage": 5000
                }
            ],
            "QuantityAvailable": 2000000,
            "ProductStatus": {"Id": 0, "Status": "Active"},
            "BackOrderNotAllowed": False,
            "NormallyStocking": True,
            "Discontinued": False,
            "EndOfLife": False,
            "Ncnr": False
        }
    ],
    "ProductsCount": 1
}

# Sample media response
SAMPLE_MEDIA: Dict[str, Any] = {
    "MediaLinks": [
        {
            "MediaType": "Product Photo",
            "Title": "Product Image",
            "SmallPhoto": "https://mm.digikey.com/small/RMCF0805JT10K0.jpg",
            "Thumbnail": "https://mm.digikey.com/thumb/RMCF0805JT10K0.jpg",
            "Url": "https://mm.digikey.com/full/RMCF0805JT10K0.jpg"
        },
        {
            "MediaType": "Datasheet",
            "Title": "Datasheet",
            "SmallPhoto": None,
            "Thumbnail": None,
            "Url": "https://www.seielect.com/catalog/sei-rmcf_rmcp.pdf"
        }
    ]
}

# Sample pricing response
SAMPLE_PRICING: Dict[str, Any] = {
    "DigiKeyPartNumber": "RMCF0805JT10K0CT-ND",
    "ManufacturerPartNumber": "RMCF0805JT10K0",
    "QuantityAvailable": 4500000,
    "StandardPricing": [
        {"BreakQuantity": 1, "UnitPrice": 0.10, "TotalPrice": 0.10},
        {"BreakQuantity": 10, "UnitPrice": 0.039, "TotalPrice": 0.39},
        {"BreakQuantity": 100, "UnitPrice": 0.022, "TotalPrice": 2.20},
        {"BreakQuantity": 500, "UnitPrice": 0.016, "TotalPrice": 8.00},
        {"BreakQuantity": 1000, "UnitPrice": 0.012, "TotalPrice": 12.00}
    ],
    "MyPricing": [],
    "ProductUrl": "https://www.digikey.com/products/detail/RMCF0805JT10K0CT-ND",
    "MinimumOrderQuantity": 1,
    "StandardPackage": 5000,
    "RequestedQuantity": 1,
    "CalculatedPrice": 0.10,
    "ExtendedPrice": 0.10
}

# Sample DigiReel pricing response
SAMPLE_DIGIREEL_PRICING: Dict[str, Any] = {
    "DigiKeyPartNumber": "RMCF0805JT10K0CT-ND",
    "ManufacturerPartNumber": "RMCF0805JT10K0",
    "RequestedQuantity": 100,
    "DigiReelFee": 7.00,
    "UnitPrice": 0.022,
    "ExtendedPrice": 2.20,
    "TotalPrice": 9.20,  # Extended + DigiReel fee
    "QuantityAvailable": 4500000,
    "MinimumOrderQuantity": 1
}


def get_keyword_search_response(keywords: str, limit: int = 5) -> Dict[str, Any]:
    """Generate a keyword search response."""
    # Filter products that match keywords (simple substring match)
    keywords_lower = keywords.lower()
    matching = []

    for product in SAMPLE_PRODUCTS:
        desc = product["Description"]["ProductDescription"].lower()
        mpn = product["ManufacturerProductNumber"].lower()
        mfr = product["Manufacturer"]["Name"].lower()

        if keywords_lower in desc or keywords_lower in mpn or keywords_lower in mfr:
            matching.append(product)

    # If no match, return all products (for testing)
    if not matching:
        matching = SAMPLE_PRODUCTS.copy()

    # Apply limit
    results = matching[:limit]

    return {
        "Products": results,
        "ProductsCount": len(results),
        "ExactMatches": [],
        "FilterOptions": {
            "Manufacturers": [
                {"Id": 447, "Name": "Stackpole Electronics Inc", "ProductCount": 1},
                {"Id": 556, "Name": "Samsung Electro-Mechanics", "ProductCount": 1}
            ],
            "Categories": [
                {"CategoryId": 52, "Name": "Chip Resistor - Surface Mount", "ProductCount": 1},
                {"CategoryId": 58, "Name": "Ceramic Capacitors", "ProductCount": 1}
            ]
        },
        "SearchLocaleUsed": {
            "Site": "US",
            "Language": "en",
            "Currency": "USD"
        },
        "AppliedParametricFiltersDto": []
    }


def get_category_by_id(category_id: int) -> Dict[str, Any] | None:
    """Get a category by its ID."""
    def search_categories(cats, target_id):
        for cat in cats:
            if cat["CategoryId"] == target_id:
                return cat.copy()
            if "ChildCategories" in cat:
                result = search_categories(cat["ChildCategories"], target_id)
                if result:
                    return result
        return None

    return search_categories(SAMPLE_CATEGORIES, category_id)


def get_product_by_number(product_number: str) -> Dict[str, Any] | None:
    """Get a product by DigiKey part number or manufacturer part number."""
    for product in SAMPLE_PRODUCTS:
        if product["ManufacturerProductNumber"].upper() == product_number.upper():
            return product.copy()
        for variation in product.get("ProductVariations", []):
            if variation["DigiKeyProductNumber"].upper() == product_number.upper():
                return product.copy()
    return None
