import unittest
from t3_dxbc_signature_contract import summarize_signature


class ContractTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(summarize_signature([])["input"]["records"], 0)

    def test_nonoverlapping_components(self):
        rows = [
            dict(kind="input", register=0, mask=3, system_value=False),
            dict(kind="input", register=0, mask=12, system_value=True),
        ]
        self.assertEqual(summarize_signature(rows)["input"]["components"], 4)

    def test_overlap_rejected(self):
        row = dict(kind="output", register=1, mask=1, system_value=False)
        with self.assertRaises(ValueError):
            summarize_signature([row, row])

    def test_bool_register_rejected(self):
        with self.assertRaises(ValueError):
            summarize_signature([dict(kind="input", register=True, mask=1, system_value=False)])

    def test_unknown_schema_rejected(self):
        with self.assertRaises(ValueError):
            summarize_signature([dict(kind="input", register=0, mask=1, system_value=False, name="private")])

    def test_limit(self):
        with self.assertRaises(ValueError):
            summarize_signature([{}] * 257)


if __name__ == "__main__":
    unittest.main()
