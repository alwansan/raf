"""Synthetic original FFT cache format lineage checks; no proprietary code."""
import hashlib
import unittest
from scripts.probe_original_fft_cache_dataflow import source_contract


def fixture(fourth="seedFormat", forwarded=True):
    assign = "var seedFormat = inputFormat;" if forwarded else "var unused=seedFormat;"
    return """class RenderTexturesCache {
       RenderTextureFormat inputFormat;
       void Construct() {
           """ + assign + """
           var t=new RenderTexture(32,32,0,""" + fourth + """,RenderTextureReadWrite.Linear);
           t.enableRandomWrite = randomWrite;
           t.Create();
       }
    }"""


def analyze(text):
    return source_contract(text, hashlib.sha256(text.encode()).hexdigest())


class CacheLineageTests(unittest.TestCase):
    def test_one_hop_format_forwarding(self):
        r = analyze(fixture())
        self.assertEqual(r["format_reference_to_typed_declaration_lexical_hops"], 1)
        self.assertEqual(r["fifth_argument_public_readwrite_modes"], ["Linear"])
        self.assertEqual(r["random_write_value_category"], "reference")
        self.assertFalse(r["original_gpu_resource_format_verified"])
        self.assertNotIn("inputFormat", str(r))
        self.assertNotIn("seedFormat", str(r))

    def test_direct_typed_format_forwarding(self):
        r = analyze(fixture(fourth="inputFormat"))
        self.assertEqual(r["format_reference_to_typed_declaration_lexical_hops"], 0)

    def test_unresolved_format_is_not_claimed(self):
        r = analyze(fixture(forwarded=False))
        self.assertIsNone(r["format_reference_to_typed_declaration_lexical_hops"])

    def test_wrong_hash_and_wrong_arity_fail(self):
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            source_contract(fixture(), "0" * 64)
        with self.assertRaisesRegex(ValueError, "signature"):
            analyze(fixture().replace("32,32,0,", "32,0,"))

    def test_comments_do_not_spoof_format_owner(self):
        data = fixture(forwarded=False).replace("void Construct()", "// seedFormat = inputFormat;\nvoid Construct()")
        self.assertIsNone(analyze(data)["format_reference_to_typed_declaration_lexical_hops"])


if __name__ == "__main__":
    unittest.main()
