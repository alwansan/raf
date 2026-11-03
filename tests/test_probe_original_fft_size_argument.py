"""Synthetic source-only, privacy and fail-closed tests."""
import json
import unittest
from scripts.probe_original_fft_size_argument import analyze, sha

class OriginalFftSizeArgumentTests(unittest.TestCase):
    def sample(self):
        return '''class WavesRendererFFT {
 private int tileSize = 128;
 void Start() {
  // new Dx11FFT(bad, fake, fake, fake);
  string ignored = "new Dx11FFT(bad, fake, fake, fake)";
  tileSize = Math.Max(tileSize, 64);
  var fft = new Dx11FFT(shader, tileSize, (size > 2048), wide);
 }
}'''

    def test_bounded_provenance_and_private_output(self):
        source = self.sample()
        r = analyze(source, sha(source))
        self.assertEqual(r["constructor_call_count"], 1)
        self.assertEqual(r["constructor_line"], 7)
        self.assertEqual(len(r["size_argument_lexical_writes"]), 2)
        self.assertEqual(r["size_argument_lexical_writes"][0]["integer_literal"], 128)
        self.assertEqual(r["size_argument_lexical_writes"][1]["rhs_kind"], "call_or_cast_expression")
        self.assertFalse(r["source_level_size_value_proven"])
        self.assertFalse(r["runtime_resolution_or_unity_kernel_mapping_verified"])
        for private in ("tileSize", "shader", "Math.Max", "ignored", "wide"):
            self.assertNotIn(private, json.dumps(r))

    def test_member_reference_remains_unproven(self):
        source = "class WavesRendererFFT { void Start() { var fft = new Dx11FFT(cs, this.width, true, false); } }"
        r = analyze(source, sha(source))
        self.assertTrue(r["size_argument_has_member_access"])
        self.assertEqual(r["size_argument_lexical_writes"], [])

    def test_fingerprint_and_constructor_cardinality_fail_closed(self):
        source = self.sample()
        with self.assertRaisesRegex(ValueError, "fingerprint"):
            analyze(source, "0"*64)
        double = source + "\nnew Dx11FFT(cs, width, true, false);"
        with self.assertRaisesRegex(ValueError, "count"):
            analyze(double, sha(double))

    def test_expression_not_guessed_into_size(self):
        source = "class WavesRendererFFT { void Start() { new Dx11FFT(cs, size*2, true, false); } }"
        with self.assertRaisesRegex(ValueError, "simple reference"):
            analyze(source, sha(source))

    def test_comment_and_string_fake_writes_ignored(self):
        source = 'class WavesRendererFFT { void Start() { /* width=1024; */ string s="width=4096;"; new Dx11FFT(cs, width, true, false); } }'
        self.assertEqual(analyze(source, sha(source))["size_argument_lexical_writes"], [])

if __name__ == "__main__":
    unittest.main()
