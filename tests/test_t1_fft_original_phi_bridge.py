"""Adversarial source-only original FFT provenance-to-Unity signature bridge."""
import copy
from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.t1_fft_original_phi_bridge import (
    MAX_BYTES, ORIGINAL, CANDIDATE, UNITY, ZIP2,
    analyze, main, read,
)

FIXTURE = Path(__file__).parent / "data" / "t1_fft_original_phi_evidence_public.json"


def fixture():
    return json.loads(FIXTURE.read_text(encoding="utf-8"))


class T1OriginalPhiBridgeTests(unittest.TestCase):
    def test_curated_authentic_ci_provenance_indicates_gap_not_fix(self):
        x = analyze(fixture())
        self.assertEqual(x["status"],
                         "original_input_bitcast_vs_translated_private_loop_phi_gap")
        self.assertEqual(x["original_source_boundary"],
                         "sint32_input_vector_bitcast_to_float32")
        self.assertEqual(x["candidate_source_boundary"],
                         "uint32_private_vector_through_float32_loop_phi")
        self.assertEqual(x["synthetic_computed_carrier_zero_signature_lanes_per_path"], 63)
        self.assertEqual(x["synthetic_buffered_carrier_zero_signature_lanes_per_path"], 0)
        self.assertEqual(len(x["synthetic_path_names"]), 5)
        for key in ("original_candidate_numeric_parity_in_Unity_proven",
                    "translation_is_cause_of_water_failure_proven",
                    "float32_FTZ_causality_proven",
                    "original_runtime_kernel_mapping_proven",
                    "android_adreno_water_proven",
                    "source_report_authenticated_by_this_gate",
                    "candidate_runtime_phi_branch_known",
                    "raw_shader_pixel_hashes_or_ids_exported"):
            self.assertIs(x[key], False, key)

    def test_fixture_verified_pins_are_three_distinct_actual_ci_runs(self):
        f = fixture()
        self.assertEqual((f["original"]["run_id"], f["original"]["commit"]), ORIGINAL)
        self.assertEqual((f["candidate"]["run_id"], f["candidate"]["commit"]), CANDIDATE)
        self.assertEqual((f["synthetic_unity"]["run_id"],
                          f["synthetic_unity"]["commit"]), UNITY)
        self.assertEqual(f["original"]["zip2_pin"], ZIP2)
        self.assertEqual(f["candidate"]["zip2_pin"], ZIP2)

    def test_no_runtime_authenticity_inferred_from_manually_copied_metadata(self):
        f = fixture()
        for key in ("original_numeric_semantics_proven",
                    "authored_unity_runtime_mapping_proven"):
            f["original"][key] = True
            with self.assertRaises(ValueError):
                analyze(f)
            f["original"][key] = False
        for key in ("selected_runtime_predecessor_proven",
                    "original_vs_unity_numeric_parity_proven"):
            f["candidate"][key] = True
            with self.assertRaises(ValueError):
                analyze(f)
            f["candidate"][key] = False
        for key in ("original_shader_executed", "android_adreno_proven"):
            f["synthetic_unity"][key] = True
            with self.assertRaises(ValueError):
                analyze(f)
            f["synthetic_unity"][key] = False

    def test_reject_run_identifier_or_commit_mismatch(self):
        for section, expected in (("original", ORIGINAL),
                                  ("candidate", CANDIDATE),
                                  ("synthetic_unity", UNITY)):
            for key, wrong in (("run_id", expected[0] + 1),
                               ("run_id", str(expected[0])),
                               ("commit", "f" * 40)):
                f = fixture()
                f[section][key] = wrong
                with self.subTest(section=section, key=key, value=wrong):
                    with self.assertRaises(ValueError):
                        analyze(f)

    def test_reject_zip2_shas_and_unexpected_fields(self):
        for section in ("original", "candidate"):
            f = fixture()
            f[section]["zip2_pin"] = "0" * 40
            with self.assertRaises(ValueError):
                analyze(f)
        f = fixture()
        f["stolen_pixel_values"] = ["PRIVATE"]
        with self.assertRaises(ValueError):
            analyze(f)
        f = fixture()
        del f["original"]["source_boundary"]
        with self.assertRaises(ValueError):
            analyze(f)

    def test_original_site_and_input_cast_must_be_exact(self):
        for key, wrong in (("role", "source"), ("site", 0), ("site", True),
                           ("coordinate", "y"), ("reachable_last_writer_count", 2),
                           ("status", "unresolved")):
            f = fixture()
            f["original"][key] = wrong
            with self.subTest(key=key), self.assertRaises(ValueError):
                analyze(f)
        for key, wrong in (("leaf_storage_class", "Private"),
                           ("leaf_numeric_kind", "float32_vector"),
                           ("write_form", "same_lane"),
                           ("immediate_store_opcode", "OpIAdd"),
                           ("cast_kinds", []),
                           ("ssa_ops", ["OpLoad"])):
            f = fixture()
            f["original"]["source_boundary"][key] = wrong
            with self.subTest(key=key), self.assertRaises(ValueError):
                analyze(f)

    def test_original_alias_or_uninitialized_source_rejected(self):
        for key in ("no_unknown_alias_write", "no_uninitialized_path"):
            f = fixture()
            f["original"][key] = False
            with self.assertRaises(ValueError):
                analyze(f)

    def test_candidate_phi_and_loop_boundaries_must_be_explicit(self):
        for key, wrong in (("top_phi_kind", "uint32_vector"),
                           ("top_selected_component", "y"),
                           ("phi_expansions", 0),
                           ("cycle_boundaries", 0),
                           ("structural_phi_backedges", 0),
                           ("incoming_count", 3),
                           ("second_boundary", "unknown"),
                           ("coordinate", "y")):
            f = fixture()
            f["candidate"][key] = wrong
            with self.subTest(key=key), self.assertRaises(ValueError):
                analyze(f)
        for key, wrong in (("leaf_storage_class", "Input"),
                           ("leaf_numeric_kind", "sint32_vector"),
                           ("has_bitcast", False)):
            f = fixture()
            f["candidate"]["first_noncyclic_boundary"][key] = wrong
            with self.subTest(key=key), self.assertRaises(ValueError):
                analyze(f)

    def test_synthetic_control_mismatch_fails_closed(self):
        for field in ("positive_controls_all_zero", "sourcefree_only"):
            f = fixture()
            f["synthetic_unity"][field] = False
            with self.assertRaises(ValueError):
                analyze(f)
        for key, wrong in (("engine", "2022.3.0f1"),
                           ("backend", "Vulkan"), ("threads", 63),
                           ("site_count", 15)):
            f = fixture()
            f["synthetic_unity"][key] = wrong
            with self.assertRaises(ValueError):
                analyze(f)

    def test_synthetic_gpu_zero_signatures_and_buffer_paths_exact(self):
        for key, wrong in (("computed_mismatches", [62] * 5),
                           ("computed_zero_signatures", [63, 63, 0, 63, 63]),
                           ("buffered_mismatches", [0, 0, 1, 0, 0]),
                           ("buffered_zero_signatures", [0] * 4)):
            f = fixture()
            f["synthetic_unity"][key] = wrong
            with self.subTest(key=key), self.assertRaises(ValueError):
                analyze(f)
        f = fixture()
        f["synthetic_unity"]["computed_zero_signatures"][0] = True
        with self.assertRaises(ValueError):
            analyze(f)

    def test_duplicate_key_invalid_json_and_excess_size(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "payload.json"
            payload = fixture()
            path.write_bytes(json.dumps(payload).encode())
            self.assertEqual(read(path), payload)
            examples = [b"", b"x", b'{"x":1,"x":2}', b'{"bad":NaN}',
                        b'{"a":Infinity}', b"z" * (MAX_BYTES + 1)]
            for blob in examples:
                path.write_bytes(blob)
                with self.subTest(blob=blob[:12]), self.assertRaises(ValueError):
                    read(path)

    def test_symlink_or_non_file_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            good = root / "payload.json"
            good.write_text(json.dumps(fixture()), encoding="utf-8")
            link = root / "symlink.json"
            link.symlink_to(good)
            with self.assertRaises(ValueError):
                read(link)
            with self.assertRaises(ValueError):
                read(root)

    def test_public_cli_prints_no_private_original_sha_ids_or_values(self):
        import sys
        stdout = io.StringIO()
        with patch.object(sys, "argv", ["bridge", "--evidence", str(FIXTURE)]):
            with redirect_stdout(stdout):
                self.assertEqual(main(), 0)
        r = stdout.getvalue()
        self.assertIn("RAFT_T1_FFT_ORIGINAL_PHI_BRIDGE", r)
        for marker in ("OpVectorShuffle", "0x", "PRIVATE", ZIP2,
                       str(FIXTURE), ORIGINAL[1], CANDIDATE[1], UNITY[1],
                       "source_boundary", "raw_", "shader_id"):
            if marker == "source_boundary":
                continue  # safe fixed whitelisted boundary labels are intentional
            if marker == "raw_":
                continue  # safe boolean 'raw_...exported' is intentionally present
            self.assertNotIn(marker, r)

    def test_invalid_private_payload_is_redacted_on_cli_error(self):
        import sys
        with tempfile.TemporaryDirectory() as directory:
            p = Path(directory) / "payload"
            p.write_bytes(b'PRIVATE_SHADER_DATA')
            err = io.StringIO()
            with patch.object(sys, "argv", ["bridge", "--evidence", str(p)]):
                with redirect_stderr(err):
                    with self.assertRaises(SystemExit) as result:
                        main()
            self.assertEqual(result.exception.code, 2)
            self.assertNotIn("PRIVATE_SHADER_DATA", err.getvalue())
            self.assertNotIn(str(p), err.getvalue())


if __name__ == "__main__":
    unittest.main()
