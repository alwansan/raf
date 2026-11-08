"""Source-free adversaries for authenticated original FFT numeric-selector cases."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from scripts.t1_fft_original_kernel6_candidates import (
    compatible_source_numeric_cases, audit_sources, _read_pinned,
)


def pins(text):
    return hashlib.sha256(text.encode()).hexdigest()


def source_fixture():
    derived = '''class Dx11FFT : GpuFFT {
 public Dx11FFT(ComputeShader cs, int size, bool precise, bool wide) : base(size,precise,wide,true) {
  kernel = inheritedCount - 5 << 1;
  if (wide) { kernel += 10; }
 }
 public void Run() {
   cs.SetTexture(kernel, "Source", src);
   cs.SetTexture(kernel, "Butterfly", tex);
   cs.SetTexture(kernel, "Target", tmp);
   cs.Dispatch(kernel, 1, 4, 1);
   cs.SetTexture(kernel + 1, "Source", tmp);
   cs.SetTexture(kernel + 1, "Butterfly", tex);
   cs.SetTexture(kernel + 1, "Target", outTex);
   cs.Dispatch(kernel + 1, 1, 4, 1);
 }
}'''
    base = '''class GpuFFT {
 protected int inheritedCount;
 protected GpuFFT(int dimension, bool a, bool b, bool c) {
  inheritedCount = (int)(Mathf.Log(dimension) / Mathf.Log(2f));
 }
}'''
    return derived, base


class OriginalFFTIndexSixEvidenceTests(unittest.TestCase):
    def proof(self, d=None, b=None, *, index=6):
        original_d, original_b = source_fixture()
        if d is None:
            d = original_d
        if b is None:
            b = original_b
        return audit_sources(d, b, pins(d), pins(b), observed_index=index)

    def test_source_numeric_six_is_size256_bank0_first_pass_case_only(self):
        r = self.proof()
        self.assertEqual(r["compatible_source_numeric_cases"], [{
            "assumed_power_of_two_size": 256, "assumed_bank_flag": 0,
            "source_pass_offset": 0, "source_numeric_argument": 6,
        }])
        self.assertEqual(r["source_dispatch_calls"], 2)
        self.assertEqual(r["source_settexture_calls"], 6)
        self.assertEqual(r["source_two_pass_affine_offsets"], [0, 1])
        self.assertTrue(r["inherited_seed_dataflow_verified"])
        self.assertFalse(r["Unity_FindKernel_runtime_id_mapped"])
        self.assertFalse(r["original_serialized_compiled_slot_index_mapped_to_runtime_id"])
        self.assertFalse(r["actual_original_resolution_or_bank_at_error_observed"])
        self.assertNotIn("inheritedCount", json.dumps(r))
        self.assertNotIn("outTex", json.dumps(r))

    def test_index_six_does_not_imply_named_kernel_or_compiled_slot(self):
        r = self.proof()
        self.assertTrue(r["source_integer_exponent_case_only"])
        self.assertFalse(r["same_ComputeShader_asset_at_owner_error_verified"])
        self.assertFalse(r["actual_Unity_Mathf_log_float_result_on_device_observed"])
        self.assertFalse(r["FFT_water_rendering_fixed"])

    def test_all_20_numeric_slots_invert_without_collision(self):
        seen = set()
        for index in range(20):
            rows = compatible_source_numeric_cases(index)
            self.assertEqual(len(rows), 1)
            row = rows[0]
            identity = (row["assumed_power_of_two_size"],
                        row["assumed_bank_flag"], row["source_pass_offset"])
            self.assertNotIn(identity, seen)
            seen.add(identity)
        self.assertEqual(len(seen), 20)

    def test_bank1_at_index16_is_not_index6(self):
        x = self.proof(index=16)["compatible_source_numeric_cases"][0]
        self.assertEqual((x["assumed_power_of_two_size"], x["assumed_bank_flag"],
                          x["source_pass_offset"]), (256, 1, 0))

    def test_odd_indices_are_second_pass_not_primary(self):
        cases = compatible_source_numeric_cases(7)
        self.assertEqual(cases[0]["assumed_power_of_two_size"], 256)
        self.assertEqual(cases[0]["source_pass_offset"], 1)

    def test_wrong_source_hash_always_rejected(self):
        d, b = source_fixture()
        with self.assertRaisesRegex(ValueError, "SHA mismatch"):
            audit_sources(d, b, "0" * 64, pins(b))
        with self.assertRaisesRegex(ValueError, "SHA mismatch"):
            audit_sources(d, b, pins(d), "0" * 64)

    def test_changed_bank_stride_fails_even_when_rehashed(self):
        d, b = source_fixture()
        with self.assertRaises(ValueError):
            self.proof(d=d.replace("kernel += 10;", "kernel += 8;"))

    def test_changed_inherited_source_seed_fails_even_when_rehashed(self):
        d, b = source_fixture()
        with self.assertRaises(ValueError):
            self.proof(b=b.replace("Log(2f)", "Log(4f)"))

    def test_extra_dispatch_literal_six_is_not_accepted_as_original(self):
        d, _ = source_fixture()
        with self.assertRaisesRegex(ValueError, "two Dispatch"):
            self.proof(d=d.replace("   cs.Dispatch(kernel + 1, 1, 4, 1);",
                                   "   cs.Dispatch(6, 1, 4, 1);\n   cs.Dispatch(kernel + 1, 1, 4, 1);"))

    def test_drift_second_dispatch_offset_rejected(self):
        d, _ = source_fixture()
        with self.assertRaises(ValueError):
            self.proof(d=d.replace("cs.Dispatch(kernel + 1", "cs.Dispatch(kernel + 2"))

    def test_drift_texture_affine_group_rejected(self):
        d, _ = source_fixture()
        with self.assertRaises(ValueError):
            self.proof(d=d.replace('cs.SetTexture(kernel + 1, "Target"',
                                   'cs.SetTexture(kernel + 2, "Target"'))

    def test_drift_texture_count_rejected(self):
        d, _ = source_fixture()
        with self.assertRaisesRegex(ValueError, "six SetTexture"):
            self.proof(d=d.replace('   cs.SetTexture(kernel, "Butterfly", tex);\n', ''))

    def test_mixed_compute_receiver_not_source_same_shader(self):
        d, _ = source_fixture()
        with self.assertRaisesRegex(ValueError, "receiver"):
            self.proof(d=d.replace('cs.SetTexture(kernel + 1, "Butterfly"',
                                   'another.SetTexture(kernel + 1, "Butterfly"'))

    def test_bool_and_out_of_domain_indices_fail(self):
        for bad in (True, -1, 20, 1.0, "6", None):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    compatible_source_numeric_cases(bad)

    def test_private_original_source_read_exact_sha_and_symlink_rejection(self):
        d, b = source_fixture()
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "Dx11FFT.cs").write_text(d, encoding="utf-8")
            self.assertEqual(_read_pinned(root, "Dx11FFT", pins(d)), d)
            with self.assertRaises(ValueError):
                _read_pinned(root, "Dx11FFT", pins(d + "tampered"))
            alias = root / "other"
            alias.mkdir()
            (alias / "Dx11FFT.cs").symlink_to(root / "Dx11FFT.cs")
            with self.assertRaisesRegex(ValueError, "missing/ambiguous"):
                _read_pinned(root, "Dx11FFT", pins(d))


if __name__ == "__main__":
    unittest.main()
