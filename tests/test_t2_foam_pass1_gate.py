import unittest
from t2_foam_pass1_gate import evaluate
P = "field_api_Graphics_Blit_"
def fixture():
    d = {}
    for p in (0, 1):
        d[P + f"explicit_sites_pass_literal{p}"] = 1
        for role, cats in (("source", ("Texture", "RenderTexture", "unknown")),
                           ("destination", ("RenderTexture", "null", "unknown"))):
            for c in cats:
                d[P + f"pass{p}_{role}_{c}"] = int(c == ("RenderTexture" if p == 0 else "unknown"))
    return d
class GateTests(unittest.TestCase):
    def test_unknown(self): self.assertEqual(evaluate(fixture()), "UNRESOLVED")
    def test_type_only(self):
        d = fixture()
        for role in ("source", "destination"):
            d[P + f"pass1_{role}_unknown"] = 0
            d[P + f"pass1_{role}_RenderTexture"] = 1
        self.assertEqual(evaluate(d), "TYPE_ONLY")
    def test_bad_partition(self):
        d = fixture(); d[P + "pass1_source_Texture"] = 1
        with self.assertRaises(ValueError): evaluate(d)
    def test_bool_rejected(self):
        d = fixture(); d[P + "pass1_source_unknown"] = True
        with self.assertRaises(ValueError): evaluate(d)
    def test_ambiguous_pass(self):
        d = fixture(); d[P + "explicit_sites_pass_literal1"] = 2
        with self.assertRaises(ValueError): evaluate(d)
    def test_missing(self):
        d = fixture(); del d[P + "pass1_destination_unknown"]
        with self.assertRaises(ValueError): evaluate(d)
if __name__ == "__main__": unittest.main()
