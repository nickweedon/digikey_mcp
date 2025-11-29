import unittest

from src.tools import mylists_tools as mt
import src.tools.mylists_tools as tools_mod


class CapturingMCP:
    def __init__(self):
        self.tools = {}
    def tool(self):
        def deco(func):
            self.tools[func.__name__] = func
            return func
        return deco


class TestMyListsTypes(unittest.TestCase):
    def setUp(self):
        def fake_make_request(method, url, headers, body=None, use_user_token=False):
            return {
                "TotalParts": 1,
                "PartsList": [{
                    "PartId": 123,
                    "UniqueId": "u-1",
                    "CustomerReference": "R1",
                    "ReferenceDesignator": "R1",
                    "Notes": "note",
                    "MinOrderQty": 1,
                    "MaxOrderQty": 99,
                    "OriginalPartNumber": "OPN",
                    "RequestedPartNumber": "RPN",
                    "DigiKeyPartNumber": "DKPN",
                    "ManufacturerPartNumber": "MPN",
                    "RequestedManufacturerName": "ReqMfg",
                    "Manufacturer": "Mfg",
                    "Description": "desc",
                    "PartStatus": "Active",
                    "PartStatusCode": "Active",
                    "Availability": None,
                    "TariffCode": "NoTariff",
                    "QuantityAvailable": 42,
                    "SelectedQuantityIndex": 0,
                    "Attrition": 0,
                    "Quantities": [{
                        "QuantityRequested": 10,
                        "CalculatedQuantity": 10,
                        "TargetPrice": 0,
                        "SelectedPackType": "Reel",
                        "SelectedSubPackType": "Sub",
                        "IsInactive": False,
                        "SelectedPackOptionIndex": 0,
                        "SelectedSubPackOptionIndex": 0,
                        "PackOptions": [{
                            "PartId": 1,
                            "DigiKeyPartNumber": "DKPN",
                            "ManufacturerPartNumber": "MPN",
                            "Quantity": 10,
                            "PackType": "Reel",
                            "QuantityAvailable": 5,
                            "MinimumOrderQuantity": 1,
                            "CalculatedUnitPrice": 0.5,
                            "ExtendedPrice": 5.0,
                            "BreakPrice": 0.5,
                            "BreakQuantity": 10,
                            "IsUpsell": False,
                            "ValueAdditionalFee": 0.0,
                            "SubPackOptions": [None],
                            "FormattedUnitPrice": "$0.50",
                            "FormattedExtendedPrice": "$5.00"
                        }]
                    }],
                    "VendorLeadWeeks": 4,
                    "PartDetailUrl": "https://example.com/part",
                    "PrimaryDatasheetUrl": "https://example.com/ds",
                    "ImageUrl": "https://example.com/img",
                    "ThumbnailUrl": "https://example.com/thumb",
                    "MarketPlaceSupplierLink": "link",
                    "SupplierName": "Supplier",
                    "AlternateParts": [],
                    "Flags": {
                        "NonStock": False,
                        "IsNCNR": False,
                        "IsSDS": False,
                        "IsValueAdd": False,
                        "IsMatched": False,
                        "IsMarketPlace": False,
                        "BoNotAllowed": False,
                        "DisplayRegularLeadTime": False,
                        "DisplayCheckActiveLeadTime": False,
                        "MultipleCrefsForPart": False,
                        "MultiplePartsForCref": False,
                        "IsChecked": False,
                        "IsEditable": True,
                        "IsDeniedByCountry": False,
                        "IsDeniedByCurrency": False,
                        "IsDeniedByCustomerId": False
                    },
                    "ReachStatus": "",
                    "RohsStatusMessage": "",
                    "Eccn": "",
                    "Htsus": "",
                    "CountryOfOrigin": "",
                    "EnvironmentalDocs": {},
                    "Category": "",
                    "PartsAvailableForCref": [],
                    "CrefsAvailableForPart": [],
                    "Substitutes": [{
                        "PartId": 2,
                        "DigiKeyPartNumber": "ALT",
                        "Manufacturer": "M",
                        "ManufacturerPartNumber": "MMPN",
                        "Description": "alt",
                        "PartDetailUrl": "u",
                        "SubstituteType": "type",
                        "MinimumOrderQuantity": 1,
                        "QuantityAvailable": "0",
                        "TariffStatus": "NoTariff",
                        "MasterPartId": 0,
                        "UnitPrice": "$1.00"
                    }]
                }]
            }
        tools_mod._make_request = fake_make_request
        tools_mod._require_user_auth = lambda: None
        self.capture = CapturingMCP()
        mt.register_mylists_tools(self.capture)

    def test_builder_returns_dataclass(self):
        func = self.capture.tools['get_parts_by_list_id']
        # Force dataclass path by temporarily making jmespath.search fail
        original_search = tools_mod.jmespath.search
        def failing_search(expr, data):
            raise RuntimeError("force fallback")
        tools_mod.jmespath.search = failing_search
        out = func(list_id="abc", limit=10)
        # Restore jmespath
        tools_mod.jmespath.search = original_search
        # Dataclass type name
        assert type(out).__name__ == 'PartsListResponse'
        assert out.TotalParts == 1
        assert len(out.PartsList) == 1
        part = out.PartsList[0]
        # Check key fields
        assert part.PartId == 123
        assert part.PartStatusCode == 'Active'
        # Substitutes preserved
        assert isinstance(part.Substitutes, list)
        assert part.Substitutes[0].DigiKeyPartNumber == 'ALT'
        # PackOptions preserved and typed
        qty = part.Quantities[0]
        assert isinstance(qty.PackOptions, list)
        assert qty.PackOptions[0].FormattedUnitPrice == '$0.50'

    def test_jmespath_default_and_custom(self):
        func = self.capture.tools['get_parts_by_list_id']
        # Default filtering (no query provided)
        default_out = func(list_id="abc", limit=10)
        # When jmespath_query is omitted, function returns filtered dict, not dataclass
        assert isinstance(default_out, dict)
        assert 'TotalParts' in default_out and 'Parts' in default_out
        assert isinstance(default_out['Parts'], list)
        part = default_out['Parts'][0]
        # Check presence of key fields from the default query
        assert 'ManufacturerPartNumber' in part
        assert 'Manufacturer' in part
        assert 'DigiKeyPartNumber' in part
        assert 'PackType' in part

        # Custom query to pick specific pricing fields
        q = '{TotalParts: TotalParts, Parts: PartsList[].{Id: PartId, Number: DigiKeyPartNumber, Prices: Quantities[].PackOptions[].{Unit: CalculatedUnitPrice, Ext: ExtendedPrice}}}'
        custom_out = func(list_id="abc", limit=10, jmespath_query=q)
        assert isinstance(custom_out, dict)
        assert 'TotalParts' in custom_out and 'Parts' in custom_out
        prices = custom_out['Parts'][0]['Prices']
        # Prices is a list of dicts for each PackOption
        assert isinstance(prices, list)
        assert isinstance(prices[0], dict)
        assert 'Unit' in prices[0] and 'Ext' in prices[0]


if __name__ == '__main__':
    import unittest
    unittest.main()
