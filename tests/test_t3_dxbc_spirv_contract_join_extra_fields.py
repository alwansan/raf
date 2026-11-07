"""Synthetic regression for ambiguous reflection coordinate namespaces."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from t3_dxbc_spirv_contract_join import check_contract


class MixedCoordinateNamespaceTests(unittest.TestCase):
    def setUp(self):
        self.dx = [{"stage": "fragment", "family": "texture", "register": 0, "count": 1}]
        self.spv = [{"stage": "fragment", "family": "texture", "set": 0, "binding": 2, "count": 1}]
        self.mapping = [{"stage": "fragment", "family": "texture", "register": 0,
                         "set": 0, "binding": 2, "count": 1}]

    def test_valid_mapping_unchanged(self):
        self.assertEqual(check_contract(self.dx, self.spv, self.mapping), [])

    def test_dx_unexpected_set_without_binding_is_schema_error(self):
        self.dx[0]["set"] = 0
        self.assertEqual(check_contract(self.dx, self.spv, self.mapping), ["invalid_schema"])

    def test_dx_unexpected_binding_is_schema_error(self):
        self.dx[0]["binding"] = 2
        self.assertEqual(check_contract(self.dx, self.spv, self.mapping), ["invalid_schema"])

    def test_spv_unexpected_register_is_schema_error(self):
        self.spv[0]["register"] = 0
        self.assertEqual(check_contract(self.dx, self.spv, self.mapping), ["invalid_schema"])


if __name__ == "__main__":
    unittest.main()
