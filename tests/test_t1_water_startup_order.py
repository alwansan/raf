"""Adversarial, source-free controls for T1's CL phone chronology audit."""
import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.t1_water_startup_order import analyze, load_summary


BASE = 1_794_145_730_000


def fixture():
    def event(first, last, n=1):
        return {"count": n, "first_observed_unix_ms": BASE + first,
                "last_observed_unix_ms": BASE + last}
    return {
        "schema": 1,
        "session": "20261108-164850-270",
        "target_package": "com.alwansan.raft.androidtest",
        "end_unix_ms": BASE + 300_000,
        "final_error_category_breakdown": {
            "ultimate_water_invalid_pass": event(27_579, 291_986, 74_359),
            "water_fft_invalid_compute_kernel": event(27_581, 291_983, 11_165),
        },
        "final_game_milestones": {
            "fmod_bootstrap_log_observed": event(11_759, 11_759),
            "raft_android_early_startup_log_observed": event(20_876, 20_876),
            "world_loaded_message_observed": event(92_065, 92_065),
        },
        "final_render_failure_breakdown": {
            "ultimate_water_invalid_pass_by_material": {
                "spectrum": 29_700, "foam_global": 44_659,
                "subsurface_blur": 0, "utility_noise": 0,
                "other_ultimate_water": 0,
            },
            "invalid_kernel_index_root_lines": {
                "index_6": 11_165, "other_index": 0,
            }
        },
        "final_shader_pass_errors_total": 74_359,
        "final_compute_kernel_errors_total": 11_165,
        "performance_statistics": {
            "shader_pass_errors_total_at_last_sample": 73_663,
            "compute_kernel_errors_total_at_last_sample": 11_049,
        },
    }


class StartupOrderTests(unittest.TestCase):
    def test_real_session_shape_and_exact_delta_contract(self):
        result = analyze(fixture())
        self.assertEqual(result["timing_ms"]["first_water_before_world_loaded"], 64_486)
        self.assertEqual(result["timing_ms"]["first_fft_before_world_loaded"], 64_484)
        self.assertEqual(result["timing_ms"]["fft_first_after_water_first"], 2)
        self.assertEqual(result["timing_ms"]["first_water_after_early_startup"], 6_703)
        self.assertEqual(result["last_sample_underreports_final_by"],
                         {"water_invalid_pass": 696, "fft_invalid_compute_kernel": 116})
        self.assertTrue(result["first_errors_observed_before_world_loaded"])
        self.assertFalse(result["limits"]["kernel6_original_unity_identity_proven"])
        self.assertFalse(result["limits"]["full_preworld_error_count_known"])

    def test_no_fake_preworld_claim_when_errors_start_later(self):
        data = fixture()
        data["final_error_category_breakdown"]["ultimate_water_invalid_pass"]["first_observed_unix_ms"] = BASE + 92_066
        data["final_error_category_breakdown"]["water_fft_invalid_compute_kernel"]["first_observed_unix_ms"] = BASE + 92_067
        result = analyze(data)
        self.assertFalse(result["first_errors_observed_before_world_loaded"])

    def test_breakdown_and_index_counters_fail_closed(self):
        for mutate in (
            lambda d: d["final_render_failure_breakdown"]["ultimate_water_invalid_pass_by_material"].update(spectrum=1),
            lambda d: d["final_render_failure_breakdown"]["invalid_kernel_index_root_lines"].update(other_index=1),
            lambda d: d.update(final_shader_pass_errors_total=1),
            lambda d: d.update(final_compute_kernel_errors_total=1),
        ):
            data = fixture()
            mutate(data)
            with self.subTest(mutate=mutate):
                with self.assertRaisesRegex(ValueError, "inconsistent"):
                    analyze(data)

    def test_last_sample_counts_cannot_supersede_final(self):
        data = fixture()
        data["performance_statistics"]["shader_pass_errors_total_at_last_sample"] = 74_360
        with self.assertRaisesRegex(ValueError, "exceed final"):
            analyze(data)

    def test_wrong_source_package_session_or_missing_world(self):
        for mutate in (
            lambda d: d.update(session="20261105-220911-559"),
            lambda d: d.update(target_package="com.example.logger"),
            lambda d: d["final_game_milestones"]["world_loaded_message_observed"].update(count=0),
        ):
            data = fixture()
            mutate(data)
            with self.assertRaises(ValueError):
                analyze(data)

    def test_symlink_fifo_and_oversize_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real = root / "real.json"
            real.write_text(json.dumps(fixture()), encoding="utf-8")
            fake = root / "alias.json"
            fake.symlink_to(real)
            with self.assertRaises((ValueError, OSError)):
                load_summary(fake)
            fifo = root / "fifo"
            if hasattr(os, "mkfifo"):
                os.mkfifo(fifo)
                # O_NONBLOCK is critical: opening a FIFO without writer must not hang.
                with self.assertRaises(ValueError):
                    load_summary(fifo)
            large = root / "oversize.json"
            large.write_bytes(b"A" * 131_073)
            with self.assertRaises(ValueError):
                load_summary(large)

    def test_nested_duplicate_in_unused_last_sample_is_detected_not_trusted(self):
        data = fixture()
        raw = json.dumps(data)[:-1] + ', "last_sample": {"render_error_flood_warning": false, "render_error_flood_warning": true}}'
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "summary.json"
            path.write_text(raw, encoding="utf-8")
            parsed, duplicates, sha = load_summary(path)
        self.assertEqual(duplicates, 1)
        result = analyze(parsed, ignored_last_sample_duplicates=duplicates, input_sha256=sha)
        self.assertEqual(result["non_authoritative_last_sample_duplicate_keys"], 1)
        self.assertEqual(len(result["summary_sha256"]), 64)

    def test_duplicate_authoritative_evidence_rejected(self):
        raw = json.dumps(fixture())[:-1] + ', "final_shader_pass_errors_total": 1}'
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "duplicate.json"
            path.write_text(raw, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "duplicate authoritative"):
                load_summary(path)

    def test_clean_file_load_and_output_redaction(self):
        data = fixture()
        data["last_sample"] = {"private_device_identifier": "NEVER_EXPORT_THIS"}
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "summary.json"
            path.write_text(json.dumps(data), encoding="utf-8")
            parsed, ignored, checksum = load_summary(path)
        result = analyze(parsed, ignored_last_sample_duplicates=ignored, input_sha256=checksum)
        self.assertNotIn("NEVER_EXPORT_THIS", json.dumps(result))
        self.assertNotIn("private_device_identifier", json.dumps(result))

    def test_noninteger_or_tampered_event_time_rejected(self):
        for mutate in (
            lambda d: d["final_error_category_breakdown"]["ultimate_water_invalid_pass"].update(count=True),
            lambda d: d["final_error_category_breakdown"]["water_fft_invalid_compute_kernel"].update(first_observed_unix_ms=-1),
            lambda d: d.update(end_unix_ms=BASE + 10),
        ):
            data = fixture()
            mutate(data)
            with self.assertRaises(ValueError):
                analyze(data)


if __name__ == "__main__":
    unittest.main()
