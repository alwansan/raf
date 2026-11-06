"""Source-free negative controls; no original game shaders or GPU execution."""
import io
import json
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch
from scripts import t1_fft_site2_y_hlsl_pair as mod

SOURCE = {
    "site": 2, "role": "butterfly", "status": "bounded_cfg_may_path_witnesses",
    "value_origin_boundary": "load",
    "coordinate_lane_structure": {
        "typed_bitcasts": ["float32_to_sint32:nonload"], "boundary": "load"},
    "last_writer_evidence_available": True,
    "final_writer_categories_possible": ["float32_constant"],
    "unknown_final_writer_path_possible": False,
    "pointer_escape_seen_on_any_cfg_path": False,
    "uninitialized_final_path_possible": False,
    "abstract_states_at_load": 2,
    "conditional_predicate_producers_seen_on_paths_by_final_writer":
        {"float32_constant": ["OpINotEqual"]},
}

class Site2YRoundtripTests(unittest.TestCase):
    def check(self, orig=None, candidate=None):
        if orig is None:
            orig = SOURCE
        if candidate is None:
            candidate = SOURCE
        with patch.object(mod, "site2y", side_effect=[orig, candidate]) as read:
            result = mod.pair("PRIVATE ORIGINAL RAW", "PRIVATE DERIVED RAW")
            self.assertEqual(read.call_count, 2)
        return result

    def test_same_structure_is_not_numeric_gpu_parity(self):
        x = self.check()
        self.assertTrue(x["structural_signature_all_equal"])
        self.assertFalse(x["structural_identity_proves_numeric_equivalence"])
        self.assertFalse(x["unity_gpu_compiler_or_runtime_tested"])
        self.assertFalse(x["android_water_proven"])

    def test_candidate_phi_branch_stop_classified_separately(self):
        variant = {**SOURCE,
                   "value_origin_boundary": "unresolved_lane",
                   "coordinate_lane_structure": {"typed_bitcasts": [],
                                                 "boundary": "unresolved",
                                                 "stop_opcode": "OpPhi"},
                   "last_writer_evidence_available": False}
        x = self.check(candidate=variant)
        self.assertFalse(x["same_coordinate_source_boundary"])
        self.assertFalse(x["same_coordinate_typed_bitcast_chain"])
        self.assertFalse(x["same_cfg_last_writer_categories"])
        self.assertFalse(x["structural_signature_all_equal"])

    def test_same_boundary_different_bitcast_is_detected(self):
        variant = {**SOURCE, "coordinate_lane_structure":
                   {"typed_bitcasts": ["uint32_to_sint32:nonload"], "boundary": "load"}}
        x = self.check(candidate=variant)
        self.assertTrue(x["same_coordinate_source_boundary"])
        self.assertFalse(x["same_coordinate_typed_bitcast_chain"])

    def test_candidate_reaching_store_changed_is_detected(self):
        variant = {**SOURCE, "final_writer_categories_possible": ["whole_vector"]}
        self.assertFalse(self.check(candidate=variant)["same_cfg_last_writer_categories"])

    def test_untrusted_original_writer_baseline_rejected(self):
        with self.assertRaises(ValueError):
            self.check(orig={**SOURCE, "final_writer_categories_possible": ["float32_load"]})

    def test_untrusted_original_bitcast_baseline_rejected(self):
        with self.assertRaises(ValueError):
            self.check(orig={**SOURCE, "coordinate_lane_structure":
                             {"typed_bitcasts": ["sint32_to_float32:nonload"]}})

    def test_original_pointer_escapes_and_uninitialized_fail_closed(self):
        for key in ("pointer_escape_seen_on_any_cfg_path",
                    "unknown_final_writer_path_possible",
                    "uninitialized_final_path_possible"):
            with self.subTest(key=key), self.assertRaises(ValueError):
                self.check(orig={**SOURCE, key: True})

    def test_incomplete_candidate_does_not_fake_equality(self):
        with patch.object(mod, "site2y", side_effect=[
                SOURCE, ValueError("secret original SSA id=%51")]):
            x = mod.pair("secret_a", "secret_b")
        self.assertFalse(x["translated_site2_y_roles_and_cfg_identifiable"])
        self.assertIsNone(x["roundtrip"])
        self.assertIsNone(x["structural_signature_all_equal"])
        self.assertNotIn("secret", json.dumps(x))

    def test_wrong_site_or_role_cannot_be_summarized(self):
        for modified in ({**SOURCE, "site": 1},
                         {**SOURCE, "role": "source"},
                         {**SOURCE, "site": True}):
            with self.subTest(modified=modified), self.assertRaises(ValueError):
                mod.summary(modified)

    def test_private_identifiers_and_data_never_reported(self):
        x = self.check()
        content = json.dumps(x)
        self.assertNotIn("PRIVATE ORIGINAL RAW", content)
        self.assertNotIn("%", content)
        self.assertFalse(x["private_shader_or_pixel_data_exported"])
        self.assertFalse(x["authored_game_kernel_mapping_proven"])

    def test_cli_failure_redacts_source_and_compiler_diagnostics(self):
        stream = io.StringIO()
        with (patch("sys.argv", ["pair", "--original-data", "/secret/owner"]),
              patch.object(mod, "inspect", side_effect=ValueError("PRIVATE_CODE_%23")),
              redirect_stderr(stream)):
            with self.assertRaises(SystemExit) as exited:
                mod.main()
        self.assertEqual(exited.exception.code, 2)
        self.assertNotIn("PRIVATE", stream.getvalue())
        self.assertNotIn("/secret/owner", stream.getvalue())

    def test_cli_outputs_safe_json_aggregate_only(self):
        x = self.check()
        stream = io.StringIO()
        with (patch("sys.argv", ["pair", "--original-data", "scratch"]),
              patch.object(mod, "inspect", return_value=x),
              redirect_stdout(stream)):
            mod.main()
        marker, row = stream.getvalue().strip().split(" ", 1)
        self.assertEqual(marker, "RAFT_T1_SITE2Y_HLSL_PAIR")
        self.assertFalse(json.loads(row)["source_and_roundtrip_binary_independently_attested"])

if __name__ == "__main__":
    unittest.main()
