"""Synthetic source-only, privacy and fail-closed tests."""
import json
import unittest
from scripts.probe_original_fft_size_argument import analyze, sha, analyze_resolution_owner

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

    def test_one_hop_alias_tracks_literal_without_claiming_runtime_value(self):
        source = "class WavesRendererFFT { int originalDimension = 256; void Start() { int size = originalDimension; new Dx11FFT(cs, size, true, false); } }"
        report = analyze(source, sha(source))
        self.assertEqual(len(report["size_argument_one_hop_aliases"]), 1)
        self.assertEqual(report["size_argument_one_hop_aliases"][0]["lexical_writes"][0]["integer_literal"], 256)
        self.assertFalse(report["size_argument_one_hop_aliases"][0]["type_resolved"])
        self.assertNotIn("originalDimension", str(report))

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

class ResolutionOwnerTests(unittest.TestCase):
    caller = """class WavesRendererFFT {
private readonly WindWaves owner;
private GpuFFT ChooseBestFFTAlgorithm(bool twoChannels) {
int dim = owner.ChosenSize;
return new Dx11FFT(shader, dim, false, twoChannels);
}
}"""
    owner = """class WindWaves {
private int finalDim;
public int ChosenSize => finalDim;
internal void ResolveFinalSettings(WaterQualityLevel quality) {
int candidate = Mathf.Min(data.Requested, quality.Limit, SystemInfo.maxTextureSize);
finalDim = candidate;
}
}"""

    def run_probe(self, caller=None, owner=None):
        caller = self.caller if caller is None else caller
        owner = self.owner if owner is None else owner
        return analyze_resolution_owner(caller, owner, sha(caller), sha(owner))

    def test_property_minimum_chain_without_runtime_claim_or_private_names(self):
        result = self.run_probe()
        self.assertEqual(result['property_return_type'], 'int')
        self.assertEqual(result['settings_minimum_arity'], 3)
        self.assertTrue(result['third_minimum_input_is_device_max_texture_size'])
        self.assertFalse(result['power_of_two_or_lower_bound_proven'])
        self.assertFalse(result['runtime_resolution_or_unity_kernel_mapping_verified'])
        for text in ('ChosenSize', 'finalDim', 'candidate', 'data.Requested', 'quality.Limit'):
            self.assertNotIn(text, json.dumps(result))

    def test_owner_fingerprint_and_getter_type_fail_closed(self):
        with self.assertRaisesRegex(ValueError, 'fingerprint'):
            analyze_resolution_owner(self.caller, self.owner, sha(self.caller), '0'*64)
        for owner in (self.owner.replace('public int ChosenSize', 'public float ChosenSize'),
                      self.owner.replace('=> finalDim;', '=> finalDim * 2;')):
            with self.assertRaises(ValueError): self.run_probe(owner=owner)

    def test_additional_writes_and_different_minimum_fail_closed(self):
        for owner in (self.owner.replace('finalDim = candidate;', 'candidate = 64; finalDim = candidate;'),
                      self.owner.replace('finalDim = candidate;', 'finalDim = candidate; finalDim += 1;'),
                      self.owner.replace('Mathf.Min', 'Mathf.Max'),
                      self.owner.replace('SystemInfo.maxTextureSize', 'data.OtherLimit')):
            with self.assertRaises(ValueError): self.run_probe(owner=owner)
        with self.assertRaises(ValueError):
            self.run_probe(caller=self.caller.replace('return new', 'dim += 1; return new'))

    def test_comments_cannot_supply_fake_property_or_minimum(self):
        with self.assertRaises(ValueError):
            self.run_probe(owner=self.owner.replace('public int ChosenSize => finalDim;', '/* public int ChosenSize => finalDim; */'))
        self.run_probe(owner=self.owner + '\n// finalDim = impostor;')


if __name__ == "__main__":
    unittest.main()
