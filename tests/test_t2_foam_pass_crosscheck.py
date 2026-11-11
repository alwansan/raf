"""Source-free tests for independent Foam role/aggregate reconciliation."""
import unittest
from unittest.mock import patch
from scripts.t2_foam_pass_crosscheck import reconcile
from scripts.t2_foam_pass_role_gate import unique_keys

P = "field_api_Graphics_Blit_"
S = ("Texture", "RenderTexture", "unknown")
D = ("RenderTexture", "null", "unknown")


def aggregate(s0, s1, d0, d1):
    r = {P + "explicit_sites_pass_" + k: int(k in ("literal0", "literal1"))
         for k in ("literal0", "literal1", "other_literal", "unknown", "mixed")}
    for role, variants, first, second in (("source", S, s0, s1),
                                           ("destination", D, d0, d1)):
        for value in variants:
            r[P + "explicit_" + role + "_" + value] = int(first == value) + int(second == value)
            r[P + "pass0_" + role + "_" + value] = int(first == value)
            r[P + "pass1_" + role + "_" + value] = int(second == value)
    return r


def sites(s0, s1, d0, d1):
    return {"sites": [
        {"pass": 0, "source": s0, "destination": d0},
        {"pass": 1, "source": s1, "destination": d1},
    ]}


class CrossEvidenceTests(unittest.TestCase):
    def test_all_81_matching_partitions(self):
        # Original full schema validation is tested separately; this tests the join.
        with patch("scripts.t2_foam_pass_crosscheck.validate_original") as original:
            for s0 in S:
                for s1 in S:
                    for d0 in D:
                        for d1 in D:
                            with self.subTest(s0=s0, s1=s1, d0=d0, d1=d1):
                                result = reconcile(aggregate(s0,s1,d0,d1), sites(s0,s1,d0,d1))
                                self.assertTrue(result["independent_summaries_agree"])
                                self.assertEqual(result["pass1"], {"source": s1, "destination": d1})
            self.assertEqual(original.call_count, 81)

    def test_matching_roles_do_not_prove_runtime_texture_identity(self):
        with patch("scripts.t2_foam_pass_crosscheck.validate_original"):
            for source in S:
                for destination in D:
                    result = reconcile(aggregate(source, source, destination, destination),
                                       sites(source, source, destination, destination))
                    self.assertEqual(result["crosspass_rendertexture_instance_identity"], "UNKNOWN")
                    self.assertTrue(result["classification_only"])

    def test_each_pass_each_role_disagreement_rejected(self):
        with patch("scripts.t2_foam_pass_crosscheck.validate_original"):
            base = aggregate("Texture", "unknown", "RenderTexture", "null")
            for p, role, replacement in ((0,"source","unknown"), (1,"source","Texture"),
                                         (0,"destination","null"), (1,"destination","unknown")):
                bad = sites("Texture","unknown","RenderTexture","null")
                bad["sites"][p][role] = replacement
                with self.subTest(pass_id=p, role=role), self.assertRaisesRegex(ValueError,"disagreement"):
                    reconcile(base, bad)

    def test_original_validator_is_mandatory(self):
        with patch("scripts.t2_foam_pass_crosscheck.validate_original", side_effect=ValueError("bad_original")):
            with self.assertRaisesRegex(ValueError, "bad_original"):
                reconcile(aggregate("Texture","unknown","RenderTexture","null"),
                          sites("Texture","unknown","RenderTexture","null"))

    def test_reject_duplicate_keys(self):
        with self.assertRaisesRegex(ValueError,"duplicate_json_key"):
            unique_keys([("pass", 0), ("pass", 1)])


if __name__ == "__main__":
    unittest.main()
