"""Adversarial source-only tests for historical GitHub Actions FFT log provenance."""
import copy
from contextlib import redirect_stdout, redirect_stderr
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts.t1_fft_historical_ci_log_verify import (
    PINS, _load, _marker, verify, main, MAX_LOG, MAX_META,
)

EVIDENCE = Path(__file__).parent / "data/t1_fft_original_phi_evidence_public.json"
STAMP = "2026-11-06T19:30:01.000001Z"


def sample():
    evidence = json.loads(EVIDENCE.read_text())
    original = evidence["original"]
    candidate = evidence["candidate"]
    unity = evidence["synthetic_unity"]
    s = original["source_boundary"]
    markers = {
        "original": {
            "role": "butterfly", "site": 1, "coordinate": "x",
            "status": original["status"],
            "reachable_last_writer_count": 1,
            "possible_unknown_alias_write": False,
            "possible_uninitialized_path": False,
            "original_numeric_semantics_proven": False,
            "complete_proof": False,
            "possible_last_writer_component_sources": [{
                "immediate_store_value_opcode": s["immediate_store_opcode"],
                "ssa_ops": s["ssa_ops"], "cast_kinds": s["cast_kinds"],
                "leaf_storage_class": s["leaf_storage_class"],
                "leaf_numeric_kind": s["leaf_numeric_kind"],
                "status": s["status"], "write_form": s["write_form"],
            }],
        },
        "candidate": {
            "role": "butterfly", "site": 1, "coordinate": "x",
            "status": candidate["status"], "top_phi_kind": "float32_vector",
            "top_selected_component": "x",
            "phi_expansions": 1, "cycle_boundaries": 1,
            "structural_phi_backedges": 1,
            "selected_runtime_predecessor_proven": False,
            "actual_original_vs_unity_numeric_parity_proven": False,
            "chain": {
                "incoming_count": 2, "status": "phi_merge",
                "value_kind": "float32_vector", "selected_component": "x",
                "incoming": [{
                    "predecessor_in_structural_cfg_cycle": False,
                    "source": {
                        "opcode": "OpCompositeInsert",
                        "source": {"opcode": "OpBitcast", "source": {
                            "detail": {
                                "leaf_storage_class": "Private",
                                "leaf_numeric_kind": "uint32_vector",
                                "status": "memory_load_boundary",
                            }
                        }},
                    },
                }, {
                    "predecessor_in_structural_cfg_cycle": True,
                    "source": {"opcode": "OpCompositeInsert", "source": {
                        "status": "loop_carried_or_cyclic_phi",
                    }},
                }],
            },
        },
        "synthetic_unity": {
            "positive_controls_passed": True,
            "original_raft_shader_compiled_or_compared": False,
            "android_adreno_water_proven": False,
            "sourcefree_unity_nunit_exact_case_passed": True,
            "synthetic_gpu_invocations_expected": 64,
            "synthetic_gpu_words_expected": 1024,
            "computed_address_category_mismatches": [63] * 5,
            "computed_zero_signatures": [63] * 5,
            "buffered_address_category_mismatches": [0] * 5,
            "buffered_zero_signatures": [0] * 5,
            "zero_signature_is_float_FTZ_causality": False,
        },
    }
    entries = {}
    for name, run_id, job_id, sha, title in PINS:
        run = {"id": run_id, "head_sha": sha, "status": "completed",
               "conclusion": "success", "head_branch": "feature/android-native-port",
               "repository": {"full_name": "alwansan/raf"}}
        job = {"id": job_id, "run_id": run_id, "status": "completed",
               "conclusion": "success"}
        log = "PRIVATE ORIGINAL TRACE BEFORE\n" + STAMP + " " + title + " " + json.dumps(
            markers[name], separators=(",", ":")) + "\nPRIVATE DATA AFTER"
        entries[name] = (run, job, log)
    return evidence, entries, markers


class HistoricalCIProvenanceTests(unittest.TestCase):
    def test_successful_pinned_meta_and_one_marker_per_run(self):
        evidence, entries, _ = sample()
        result = verify(evidence, entries)
        self.assertTrue(result["retrieved_gitHub_CI_job_logs_match_curated_safe_report"])
        self.assertEqual(result["pinned_successful_runs_and_jobs_checked"], 3)
        self.assertFalse(result["CI_logs_are_signed_runtime_attestation"])
        self.assertFalse(result["shader_original_vs_Unity_numeric_parity_proven"])
        self.assertFalse(result["android_adreno_water_proven"])

    def test_reject_wrong_run_sha_failed_run_or_wrong_branch(self):
        for field, value in [("head_sha", "f" * 40), ("status", "in_progress"),
                             ("conclusion", "failure"),
                             ("head_branch", "main")]:
            evidence, entries, _ = sample()
            entries["original"][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                verify(evidence, entries)

    def test_reject_wrong_job_run_or_failure(self):
        for field, value in [("id", 100), ("run_id", 100),
                             ("status", "in_progress"), ("conclusion", "cancelled")]:
            evidence, entries, _ = sample()
            entries["candidate"][1][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                verify(evidence, entries)

    def test_reject_missing_or_duplicate_marker(self):
        evidence, entries, _ = sample()
        entries["original"] = (*entries["original"][:2], "NO MARKER")
        with self.assertRaises(ValueError):
            verify(evidence, entries)
        evidence, entries, _ = sample()
        entries["original"] = (*entries["original"][:2], entries["original"][2] * 2)
        with self.assertRaises(ValueError):
            verify(evidence, entries)

    def test_wrong_marker_job_and_duplicate_json_keys_rejected(self):
        evidence, entries, _ = sample()
        entries["original"] = (*entries["original"][:2],
            entries["original"][2].replace("RAFT_T1_FFT_BUTTERFLY_X_WRITER_LINEAGE",
                                            "RAFT_T1_FFT_HLSL_NESTED_PHI_X"))
        with self.assertRaises(ValueError):
            verify(evidence, entries)
        self.assertRaises(ValueError, _marker,
            STAMP + ' RAFT_T1_ADDRESS_PROVENANCE_GATE {"a":1,"a":2}',
            "RAFT_T1_ADDRESS_PROVENANCE_GATE")

    def test_original_wrong_input_storage_or_hidden_alias_rejected(self):
        evidence, entries, markers = sample()
        markers["original"]["possible_last_writer_component_sources"][0]["leaf_storage_class"] = "Private"
        title = PINS[0][-1]
        entries["original"] = (*entries["original"][:2],
            STAMP + " " + title + " " + json.dumps(markers["original"]))
        with self.assertRaises(ValueError):
            verify(evidence, entries)
        evidence, entries, markers = sample()
        markers["original"]["possible_unknown_alias_write"] = True
        entries["original"] = (*entries["original"][:2],
            STAMP + " " + title + " " + json.dumps(markers["original"]))
        with self.assertRaises(ValueError):
            verify(evidence, entries)

    def test_candidate_wrong_loop_phi_or_missing_bitcast_rejected(self):
        for kind in ("bad_loop", "no_bitcast"):
            evidence, entries, markers = sample()
            chain = markers["candidate"]["chain"]["incoming"]
            if kind == "bad_loop":
                chain[1]["predecessor_in_structural_cfg_cycle"] = False
            else:
                chain[0]["source"]["source"]["opcode"] = "OpIAdd"
            entries["candidate"] = (*entries["candidate"][:2],
                STAMP + " " + PINS[1][-1] + " " + json.dumps(markers["candidate"]))
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                verify(evidence, entries)

    def test_unity_signature_drift_or_false_positive_controls_rejected(self):
        for kind in ("computed_zero_signatures", "positive_controls_passed"):
            evidence, entries, markers = sample()
            markers["synthetic_unity"][kind] = [62] * 5 if kind.endswith("signatures") else False
            entries["synthetic_unity"] = (*entries["synthetic_unity"][:2],
                STAMP + " " + PINS[2][-1] + " " + json.dumps(markers["synthetic_unity"]))
            with self.subTest(kind=kind), self.assertRaises(ValueError):
                verify(evidence, entries)

    def test_wrong_curated_evidence_or_missing_run_rejected(self):
        evidence, entries, _ = sample()
        evidence["original"]["zip2_pin"] = "bad"
        with self.assertRaises(ValueError):
            verify(evidence, entries)
        evidence, entries, _ = sample()
        del entries["original"]
        with self.assertRaises(ValueError):
            verify(evidence, entries)

    def test_size_bom_symlink_and_duplicate_metadata_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / "meta"
            path.write_bytes(b"\xef\xbb\xbf" + b'{"id":1}')
            self.assertEqual(_load(path, MAX_META, json_data=True), {"id": 1})
            path.write_bytes(b'{"id":1,"id":2}')
            with self.assertRaises(ValueError):
                _load(path, MAX_META, json_data=True)
            path.write_bytes(b"a" * (MAX_META + 1))
            with self.assertRaises(ValueError):
                _load(path, MAX_META)
            link = root / "link"
            link.symlink_to(path)
            with self.assertRaises(ValueError):
                _load(link, MAX_LOG)
            self.assertRaises(ValueError, _load, root, MAX_LOG)

    def test_cli_success_redacts_private_log_lines(self):
        evidence, entries, _ = sample()
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            fixture = root / "evidence.json"
            fixture.write_text(json.dumps(evidence), encoding="utf-8")
            paths = ["verify", "--evidence", str(fixture)]
            for name, _, _, _, _ in PINS:
                for kind, value in zip(("run", "job", "log"), entries[name]):
                    path = root / f"{name}-{kind}.txt"
                    path.write_text(value if kind == "log" else json.dumps(value))
                    paths.extend(("--" + name + "-" + kind, str(path)))
            output = io.StringIO()
            with patch("sys.argv", paths), redirect_stdout(output):
                self.assertEqual(main(), 0)
            result = output.getvalue()
            self.assertIn("RAFT_T1_FFT_HISTORICAL_CI_LOG", result)
            for secret in ("PRIVATE ORIGINAL TRACE", "PRIVATE DATA AFTER", "OpBitcast",
                           "Input", str(root), PINS[0][3], "0x"):
                self.assertNotIn(secret, result)

    def test_cli_rejects_private_trace_without_leak(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "private"
            path.write_text("PRIVATE ORIGINAL DATA")
            output = io.StringIO()
            with patch("sys.argv", ["verify", "--evidence", str(path)]):
                with redirect_stderr(output):
                    with self.assertRaises(SystemExit) as err:
                        main()
            self.assertEqual(err.exception.code, 2)
            self.assertNotIn("PRIVATE ORIGINAL DATA", output.getvalue())


if __name__ == "__main__":
    unittest.main()
