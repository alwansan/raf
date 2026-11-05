"""Synthetic-only tests; never imply original FFT or Unity device proof."""
import hashlib
import unittest
from scripts.t1_fft_dispatch_evidence import audit


class DispatchEvidenceTests(unittest.TestCase):
    def check(self, text):
        raw = text.encode()
        return audit(raw, hashlib.sha256(raw).hexdigest())

    def test_real_syntax_is_only_structural(self):
        result = self.check('var k = shader.FindKernel("K"); shader.SetTexture(k, "A", t); shader.Dispatch(k, 1, 1, 1);')
        self.assertTrue(result["findkernel_and_dispatch_syntax_present"])
        self.assertTrue(result["call_families_present"]["SetTexture"])
        self.assertFalse(result["original_program_to_kernel_mapping_proven"])
        self.assertFalse(result["resource_binding_dataflow_proven"])
        self.assertFalse(result["android_device_proven"])

    def test_comments_and_strings_do_not_count(self):
        result = self.check('// FindKernel(x)\n/* Dispatch(x) */ var x = "SetTexture(a)";')
        self.assertFalse(result["findkernel_and_dispatch_syntax_present"])
        self.assertFalse(result["call_families_present"]["SetTexture"])

    def test_interpolated_and_verbatim_literals_are_not_calls(self):
        source = '''var a = $"FindKernel(1)"; var b = $@"Dispatch(1)";
var c = @$"SetTexture(1)"; var d = 'x';
shader.Dispatch(k, 1, 1, 1);'''
        result = self.check(source)
        self.assertFalse(result["findkernel_and_dispatch_syntax_present"])
        self.assertFalse(result["call_families_present"]["FindKernel"])
        self.assertFalse(result["call_families_present"]["SetTexture"])
        self.assertTrue(result["call_families_present"]["Dispatch"])

    def test_csharp_raw_and_interpolated_raw_literals_are_not_calls(self):
        source = '''var x = """shader.FindKernel("K"); shader.Dispatch(k, 1, 1, 1);""";
var y = $"""shader.SetTexture(k, "A", t);""";
shader.Dispatch(k, 1, 1, 1);'''
        result = self.check(source)
        self.assertFalse(result["call_families_present"]["FindKernel"])
        self.assertFalse(result["call_families_present"]["SetTexture"])
        self.assertTrue(result["call_families_present"]["Dispatch"])
        self.assertFalse(result["findkernel_and_dispatch_syntax_present"])

    def test_four_quote_raw_delimiter_does_not_close_on_inner_triple(self):
        source = '''var text = """"shader.FindKernel("K"); """ shader.SetTexture(k, "A", t); """";
shader.Dispatch(k, 1, 1, 1);'''
        result = self.check(source)
        self.assertFalse(result["call_families_present"]["FindKernel"])
        self.assertFalse(result["call_families_present"]["SetTexture"])
        self.assertTrue(result["call_families_present"]["Dispatch"])
        self.assertFalse(result["findkernel_and_dispatch_syntax_present"])

    def test_missing_dispatch_cannot_pass(self):
        self.assertFalse(self.check("shader.FindKernel(x);")["findkernel_and_dispatch_syntax_present"])

    def test_wrong_sha_and_empty_rejected(self):
        raw = b"shader.Dispatch(1,1,1);"
        with self.assertRaises(ValueError):
            audit(raw, "0" * 64)
        with self.assertRaises(ValueError):
            audit(b"", hashlib.sha256(b"").hexdigest())
        with self.assertRaises(ValueError):
            audit(raw, "INVALID")

    def test_private_identifiers_not_in_output(self):
        result = self.check('shader.FindKernel("SECRET_PRIVATE_NAME");')
        self.assertNotIn("SECRET_PRIVATE_NAME", str(result))


if __name__ == "__main__":
    unittest.main()
