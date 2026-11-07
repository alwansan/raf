import unittest
from scripts.t2_foam_pass_role_gate import validate

GOOD = {"sites": [{"pass": 0, "source": "RenderTexture", "destination": "RenderTexture"},
                  {"pass": 1, "source": "unknown", "destination": "unknown"}]}

class RoleGateTests(unittest.TestCase):
    def test_expected(self):
        self.assertEqual(validate(GOOD)[0], ("RenderTexture", "RenderTexture"))

    def test_reordered(self):
        self.assertEqual(validate({"sites": list(reversed(GOOD["sites"]))})[1], ("unknown", "unknown"))

    def test_reject_malformed(self):
        cases = [None, {}, {"sites": []}, {"sites": [GOOD["sites"][0]] * 2},
                 {"sites": [{**GOOD["sites"][0], "pass": True}, GOOD["sites"][1]]},
                 {"sites": [{**GOOD["sites"][0], "source": "GPU texture"}, GOOD["sites"][1]]},
                 {"sites": [{**GOOD["sites"][0], "destination": "Texture"}, GOOD["sites"][1]]},
                 {"sites": [{**GOOD["sites"][0], "private_name": "leak"}, GOOD["sites"][1]]}]
        for case in cases:
            with self.subTest(case=case), self.assertRaises(ValueError):
                validate(case)

if __name__ == "__main__":
    unittest.main()
