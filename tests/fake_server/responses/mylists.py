"""Sample MyLists response data for fake DigiKey API server.

These responses are based on the DigiKey MyLists API v1 documentation
and are used for testing purposes.
"""

from typing import Any, Dict, List

# Sample list objects for get_all_lists
SAMPLE_LISTS: List[Dict[str, Any]] = [
    {
        "ListId": "list-001",
        "ListName": "Test Components",
        "CreatedBy": "testuser@example.com",
        "CustomerId": "0",
        "TotalParts": 3,
        "DateCreated": "2024-01-15T10:30:00Z",
        "DateModified": "2024-01-20T14:45:00Z",
        "Tags": ["resistors", "capacitors"],
        "ListSettings": {},
        "Source": "internal"
    },
    {
        "ListId": "list-002",
        "ListName": "Project Alpha BOM",
        "CreatedBy": "testuser@example.com",
        "CustomerId": "0",
        "TotalParts": 10,
        "DateCreated": "2024-02-01T09:00:00Z",
        "DateModified": "2024-02-15T16:30:00Z",
        "Tags": ["project-alpha"],
        "ListSettings": {},
        "Source": "other"
    },
    {
        "ListId": "list-003",
        "ListName": "Empty List",
        "CreatedBy": "testuser@example.com",
        "CustomerId": "0",
        "TotalParts": 0,
        "DateCreated": "2024-03-01T12:00:00Z",
        "DateModified": "2024-03-01T12:00:00Z",
        "Tags": [],
        "ListSettings": {},
        "Source": "internal"
    }
]

# Sample parts for a list
SAMPLE_PARTS: List[Dict[str, Any]] = [
    {
        "PartId": 1942531,
        "UniqueId": "unique-part-001",
        "CustomerReference": "R1",
        "ReferenceDesignator": "R1",
        "Notes": "Main resistor",
        "MinOrderQty": 1,
        "MaxOrderQty": 0,
        "OriginalPartNumber": "RMCF0805JT10K0",
        "RequestedPartNumber": "RMCF0805JT10K0CT-ND",
        "DigiKeyPartNumber": "RMCF0805JT10K0CT-ND",
        "ManufacturerPartNumber": "RMCF0805JT10K0",
        "RequestedManufacturerName": "",
        "Manufacturer": "Stackpole Electronics Inc",
        "Description": "RES 10K OHM 5% 1/8W 0805",
        "PartStatus": "Active",
        "PartStatusCode": "0",
        "Availability": "In Stock",
        "TariffCode": "",
        "QuantityAvailable": 4500000,
        "SelectedQuantityIndex": 0,
        "Attrition": 0,
        "Quantities": [
            {
                "QuantityRequested": 10,
                "CalculatedQuantity": 10,
                "TargetPrice": None,
                "SelectedPackType": "Cut Tape",
                "SelectedSubPackType": "",
                "IsInactive": False,
                "SelectedPackOptionIndex": 0,
                "SelectedSubPackOptionIndex": 0,
                "PackOptions": [
                    {
                        "PartId": 1942531,
                        "DigiKeyPartNumber": "RMCF0805JT10K0CT-ND",
                        "ManufacturerPartNumber": "RMCF0805JT10K0",
                        "Quantity": 10,
                        "PackType": "Cut Tape",
                        "QuantityAvailable": 4500000,
                        "MinimumOrderQuantity": 1,
                        "CalculatedUnitPrice": 0.10,
                        "ExtendedPrice": 1.00,
                        "BreakPrice": 0.10,
                        "BreakQuantity": 1,
                        "IsUpsell": False,
                        "ValueAdditionalFee": 0.0,
                        "SubPackOptions": [],
                        "FormattedUnitPrice": "$0.10",
                        "FormattedExtendedPrice": "$1.00"
                    }
                ]
            }
        ],
        "VendorLeadWeeks": 0,
        "PartDetailUrl": "https://www.digikey.com/en/products/detail/stackpole-electronics-inc/RMCF0805JT10K0/1942531",
        "PrimaryDatasheetUrl": "https://www.seielect.com/catalog/sei-rmcf_rmcp.pdf",
        "ImageUrl": "https://mm.digikey.com/Volume0/opasdata/d220001/medias/images/1702/MFG_RMCF%20SERIES.jpg",
        "ThumbnailUrl": "https://mm.digikey.com/Volume0/opasdata/d220001/medias/images/1702/tmb_MFG_RMCF%20SERIES.jpg",
        "MarketPlaceSupplierLink": "",
        "SupplierName": "",
        "Substitutes": None,
        "AlternateParts": [],
        "Flags": {
            "NonStock": False,
            "IsNCNR": False,
            "IsSDS": False,
            "IsValueAdd": False,
            "IsMatched": True,
            "IsMarketPlace": False,
            "BoNotAllowed": False,
            "DisplayRegularLeadTime": True,
            "DisplayCheckActiveLeadTime": False,
            "MultipleCrefsForPart": False,
            "MultiplePartsForCref": False,
            "IsChecked": False,
            "IsEditable": True,
            "IsDeniedByCountry": False,
            "IsDeniedByCurrency": False,
            "IsDeniedByCustomerId": False
        },
        "ReachStatus": "REACH Unaffected",
        "RohsStatusMessage": "RoHS Compliant",
        "Eccn": "EAR99",
        "Htsus": "8533.21.0030",
        "CountryOfOrigin": "CN",
        "EnvironmentalDocs": {},
        "Category": "Chip Resistor - Surface Mount",
        "PartsAvailableForCref": [],
        "CrefsAvailableForPart": []
    },
    {
        "PartId": 399841,
        "UniqueId": "unique-part-002",
        "CustomerReference": "C1",
        "ReferenceDesignator": "C1",
        "Notes": "Decoupling capacitor",
        "MinOrderQty": 1,
        "MaxOrderQty": 0,
        "OriginalPartNumber": "CL10B104KB8NNNC",
        "RequestedPartNumber": "1276-1006-1-ND",
        "DigiKeyPartNumber": "1276-1006-1-ND",
        "ManufacturerPartNumber": "CL10B104KB8NNNC",
        "RequestedManufacturerName": "",
        "Manufacturer": "Samsung Electro-Mechanics",
        "Description": "CAP CER 0.1UF 50V X7R 0603",
        "PartStatus": "Active",
        "PartStatusCode": "0",
        "Availability": "In Stock",
        "TariffCode": "",
        "QuantityAvailable": 12000000,
        "SelectedQuantityIndex": 0,
        "Attrition": 0,
        "Quantities": [
            {
                "QuantityRequested": 100,
                "CalculatedQuantity": 100,
                "TargetPrice": None,
                "SelectedPackType": "Cut Tape",
                "SelectedSubPackType": "",
                "IsInactive": False,
                "SelectedPackOptionIndex": 0,
                "SelectedSubPackOptionIndex": 0,
                "PackOptions": [
                    {
                        "PartId": 399841,
                        "DigiKeyPartNumber": "1276-1006-1-ND",
                        "ManufacturerPartNumber": "CL10B104KB8NNNC",
                        "Quantity": 100,
                        "PackType": "Cut Tape",
                        "QuantityAvailable": 12000000,
                        "MinimumOrderQuantity": 1,
                        "CalculatedUnitPrice": 0.024,
                        "ExtendedPrice": 2.40,
                        "BreakPrice": 0.024,
                        "BreakQuantity": 1,
                        "IsUpsell": False,
                        "ValueAdditionalFee": 0.0,
                        "SubPackOptions": [],
                        "FormattedUnitPrice": "$0.024",
                        "FormattedExtendedPrice": "$2.40"
                    }
                ]
            }
        ],
        "VendorLeadWeeks": 0,
        "PartDetailUrl": "https://www.digikey.com/en/products/detail/samsung-electro-mechanics/CL10B104KB8NNNC/399841",
        "PrimaryDatasheetUrl": "https://mm.digikey.com/Volume0/opasdata/d220001/medias/docus/35/CL10B104KB8NNNC.pdf",
        "ImageUrl": "https://mm.digikey.com/Volume0/opasdata/d220001/medias/images/2346/MFG_CL.jpg",
        "ThumbnailUrl": "https://mm.digikey.com/Volume0/opasdata/d220001/medias/images/2346/tmb_MFG_CL.jpg",
        "MarketPlaceSupplierLink": "",
        "SupplierName": "",
        "Substitutes": None,
        "AlternateParts": [],
        "Flags": {
            "NonStock": False,
            "IsNCNR": False,
            "IsSDS": False,
            "IsValueAdd": False,
            "IsMatched": True,
            "IsMarketPlace": False,
            "BoNotAllowed": False,
            "DisplayRegularLeadTime": True,
            "DisplayCheckActiveLeadTime": False,
            "MultipleCrefsForPart": False,
            "MultiplePartsForCref": False,
            "IsChecked": False,
            "IsEditable": True,
            "IsDeniedByCountry": False,
            "IsDeniedByCurrency": False,
            "IsDeniedByCustomerId": False
        },
        "ReachStatus": "REACH Unaffected",
        "RohsStatusMessage": "RoHS Compliant",
        "Eccn": "EAR99",
        "Htsus": "8532.24.0020",
        "CountryOfOrigin": "KR",
        "EnvironmentalDocs": {},
        "Category": "Ceramic Capacitors",
        "PartsAvailableForCref": [],
        "CrefsAvailableForPart": []
    }
]


def get_list_by_id(list_id: str) -> Dict[str, Any] | None:
    """Get a list by its ID."""
    for lst in SAMPLE_LISTS:
        if lst["ListId"] == list_id:
            return lst.copy()
    return None


def get_parts_response(list_id: str) -> Dict[str, Any]:
    """Get parts response for a list."""
    # Only list-001 has parts in our fake data
    if list_id == "list-001":
        return {
            "TotalParts": len(SAMPLE_PARTS),
            "PartsList": SAMPLE_PARTS.copy()
        }
    return {
        "TotalParts": 0,
        "PartsList": []
    }
