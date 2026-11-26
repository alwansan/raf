"""Receipt-gate/staging tests only; fabricated pixels are never GPU evidence."""
from copy import deepcopy
from contextlib import redirect_stdout
from hashlib import sha256
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import gt_synthetic_material_alpha as alpha


# Fixed independently calculated reference values, not alpha.expected_pixel().
BG = [0.125, 0.25, 0.5, 1.0]
TINT = [0.5, 0.75, 0.25, 1.0]
STRAIGHT = [BG, [.3125, .21875, .25, 1.], [.125, .75, .125, 1.],
            [.375, .09375, .25, 1.], [.09375, .3125, .34375, 1.], BG]
OPAQUE = [[0., 0., 0., 1.], [.5, .1875, 0., 1.], [.125, .75, .125, 1.],
          [.375, .09375, .25, 1.], [.0625, .375, .1875, 1.], [0., 0., 0., 1.]]
NO_TINT = [BG, [.5625, .25, .25, 1.], [.25, 1., .5, 1.],
           [.75, .125, 1., 1.], [.125, .375, .625, 1.], BG]
RAW_OPAQUE = [[0., 0., 0., 1.], [1., .25, 0., 1.], [.25, 1., .5, 1.],
              [.75, .125, 1., 1.], [.125, .5, .75, 1.], [0., 0., 0., 1.]]
REFERENCES = {
    "opaque_texture_tint": OPAQUE,
    "straight_alpha": STRAIGHT,
    "missing_texture_binding": [TINT] * 6,
    "missing_tint_binding": NO_TINT,
    "disabled_blending": OPAQUE,
}
HASHES = {"Assets/SyntheticMaterialAlpha.shader": "1" * 64,
          "Assets/Editor/SyntheticMaterialAlphaValidation.cs": "2" * 64}
RUN_ID = "in_memory_unit_test_only_not_a_render_run"


def unit_receipt():
    """Construct mock evidence in memory; never write it as an execution receipt."""
    report = dict(schema_version=1, run_id=RUN_ID, status="PASS",
        reason="fabricated_unit_test_input_only", Unity_version="2021.3.45f2",
        backend="Vulkan", active_color_space="Linear", synthetic_only=True,
        Unity_render_executed=True, Android_device=False, production_pixels=False, XAPK=False,
        rendered_case_count=5, positive_case_count=2, negative_controls_detected=3,
        shader_sha256=HASHES["Assets/SyntheticMaterialAlpha.shader"],
        probe_sha256=HASHES["Assets/Editor/SyntheticMaterialAlphaValidation.cs"],
        max_error=0., cases=[])
    for name, expected in REFERENCES.items():
        positive = name in ("opaque_texture_tint", "straight_alpha")
        intended = OPAQUE if name == "opaque_texture_tint" else STRAIGHT
        mismatch = max(abs(a - b) for pixel, wanted in zip(expected, intended)
                       for a, b in zip(pixel, wanted))
        report["cases"].append(dict(name=name, kind="positive" if positive else "negative",
            **{"pass": True}, max_error=0., intended_mismatch=mismatch,
            checked_pixel_count=24, samples=[dict(x=x, y=y,
                observed=list(expected[x]), expected=list(expected[x]), intended=list(intended[x]))
                for y in range(4) for x in range(6)]))
    return report


def validate(report, exit_code=0):
    return alpha.validate_receipt(report, run_id=RUN_ID, hashes=HASHES, exit_code=exit_code)


def row_named(report, name):
    return next(row for row in report["cases"] if row["name"] == name)


class SyntheticMaterialAlphaTests(unittest.TestCase):
    def test_fresh_staging_contains_only_fixture_and_cannot_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "fresh"
            result = alpha.construct(project)
            self.assertEqual(result["status"], "PREPARED")
            self.assertIs(result["Unity_render_executed"], False)
            names = {p.relative_to(project).as_posix() for p in project.rglob("*") if p.is_file()}
            self.assertEqual(names, {"Assets/SyntheticMaterialAlpha.shader",
                "Assets/Editor/SyntheticMaterialAlphaValidation.cs", "Packages/manifest.json",
                "ProjectSettings/ProjectVersion.txt", "ProjectSettings/ProjectSettings.asset",
                "synthetic-alpha-fixture.json"})
            before = {name: (project / name).read_bytes() for name in names}
            self.assertEqual(alpha.check_project(project), alpha.source_hashes())
            with self.assertRaises(ValueError):
                alpha.construct(project)
            self.assertEqual(before, {name: (project / name).read_bytes() for name in names})

    def test_extra_asset_changed_shader_and_rewritten_manifest_are_rejected(self):
        for corruption in ("extra_asset", "shader", "shader_and_manifest"):
            with self.subTest(corruption=corruption), tempfile.TemporaryDirectory() as directory:
                project = Path(directory) / "fresh"
                alpha.construct(project)
                shader = project / "Assets/SyntheticMaterialAlpha.shader"
                if corruption == "extra_asset":
                    (project / "Assets/Unapproved.asset").write_text("synthetic forbidden extra")
                else:
                    shader.write_bytes(shader.read_bytes() + b"\n// changed candidate\n")
                    if corruption == "shader_and_manifest":
                        manifest_path = project / "synthetic-alpha-fixture.json"
                        manifest = json.loads(manifest_path.read_text())
                        manifest["files"]["Assets/SyntheticMaterialAlpha.shader"] = sha256(shader.read_bytes()).hexdigest()
                        manifest_path.write_text(json.dumps(manifest))
                with self.assertRaises(ValueError):
                    alpha.check_project(project)

    def test_no_unity_writes_not_run_exits_two_and_never_launches(self):
        with tempfile.TemporaryDirectory() as directory:
            parent = Path(directory)
            project, output = parent / "fresh", parent / "receipt.json"
            alpha.construct(project)
            arguments = ["probe", "run", "--project", str(project), "--out", str(output),
                         "--unity", str(parent / "nonexistent_Unity")]
            with patch("sys.argv", arguments), patch.object(alpha.subprocess, "run") as launch, redirect_stdout(io.StringIO()):
                self.assertEqual(alpha.main(), 2)
                launch.assert_not_called()
            result = json.loads(output.read_text())
            self.assertEqual(result["status"], "NOT_RUN")
            self.assertIs(result["Unity_render_executed"], False)
            self.assertIs(result["Vulkan_raster_validation_passed"], False)
            self.assertNotIn("process_exit_code", result)
            self.assertFalse(output.with_suffix(".unity.json").exists())
            with self.assertRaises(ValueError):
                alpha.execute(project, output, unity=parent / "nonexistent_Unity")

    def test_verify_cli_missing_receipt_cannot_pass_even_with_zero_exit(self):
        with tempfile.TemporaryDirectory(prefix="alpha-unit-only-") as directory:
            parent = Path(directory)
            receipt, output = parent / "missing.json", parent / "unit-verification.json"
            arguments = ["probe", "verify", "--receipt", str(receipt), "--out", str(output),
                         "--run-id", RUN_ID, "--exit-code", "0"]
            with patch("sys.argv", arguments), patch.object(alpha, "source_hashes", return_value=HASHES), \
                    patch.object(alpha.subprocess, "run") as launch, redirect_stdout(io.StringIO()):
                self.assertEqual(alpha.main(), 2)
                launch.assert_not_called()
            result = json.loads(output.read_text())
            self.assertEqual(result["status"], "NOT_RUN")
            self.assertEqual(result["reason"], "Unity_receipt_missing")
            self.assertIs(result["Unity_render_executed"], False)
            self.assertIs(result["Vulkan_raster_validation_passed"], False)
            self.assertNotIn("validated_pixels", result)

    def test_verify_cli_accepts_complete_mock_only_with_matching_run_and_source(self):
        # These disposable files use fake hashes and a test nonce. They are
        # unit-test input, never persisted as an actual rendering receipt.
        with tempfile.TemporaryDirectory(prefix="alpha-unit-only-") as directory:
            parent = Path(directory)
            receipt = parent / "fabricated-unit-input.json"
            output = parent / "unit-verification.json"
            report = unit_receipt()
            report["graphics_device_name"] = "unit-test-only-not-a-device"
            receipt.write_text(json.dumps(report))
            arguments = ["probe", "verify", "--receipt", str(receipt), "--out", str(output),
                         "--run-id", RUN_ID, "--exit-code", "0"]
            with patch("sys.argv", arguments), patch.object(alpha, "source_hashes", return_value=HASHES), \
                    patch.object(alpha.subprocess, "run") as launch, redirect_stdout(io.StringIO()):
                self.assertEqual(alpha.main(), 0)
                launch.assert_not_called()
            result = json.loads(output.read_text())
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["validated_pixels"], 120)
            self.assertEqual(result["validated_cases"], 5)
            self.assertEqual(result["negative_controls_detected"], 3)
            self.assertEqual(result["run_id"], RUN_ID)
            self.assertEqual(result["receipt_sha256"], sha256(receipt.read_bytes()).hexdigest())
            self.assertEqual(result["graphics_device_name"], "unit-test-only-not-a-device")
            for field in ("Android_device", "production_pixels", "XAPK"):
                self.assertIs(result[field], False)

    def test_verify_cli_rejects_stale_failed_or_forged_inputs_despite_zero_exit(self):
        corruptions = ("stale_nonce", "stale_shader", "stale_probe", "nonzero_exit",
                       "reported_failure", "positive_pixel_failure", "malformed_json")
        for corruption in corruptions:
            with self.subTest(corruption=corruption), tempfile.TemporaryDirectory(prefix="alpha-unit-only-") as directory:
                parent = Path(directory)
                receipt = parent / "fabricated-unit-input.json"
                output = parent / "unit-verification.json"
                report, exit_code = unit_receipt(), 0
                if corruption == "stale_nonce":
                    report["run_id"] = "different_previous_unit_run"
                elif corruption == "stale_shader":
                    report["shader_sha256"] = "3" * 64
                elif corruption == "stale_probe":
                    report["probe_sha256"] = "4" * 64
                elif corruption == "nonzero_exit":
                    exit_code = 2
                elif corruption == "reported_failure":
                    report["status"] = "FAIL"
                elif corruption == "positive_pixel_failure":
                    # Keep all true flags and numeric summaries: the CLI must
                    # still reach the independent per-pixel check.
                    row_named(report, "straight_alpha")["samples"][0]["observed"] = [0., 0., 0., 1.]
                receipt.write_text("{broken" if corruption == "malformed_json" else json.dumps(report))
                arguments = ["probe", "verify", "--receipt", str(receipt), "--out", str(output),
                             "--run-id", RUN_ID, "--exit-code", str(exit_code)]
                with patch("sys.argv", arguments), patch.object(alpha, "source_hashes", return_value=HASHES), \
                        redirect_stdout(io.StringIO()):
                    self.assertEqual(alpha.main(), 2)
                result = json.loads(output.read_text())
                self.assertEqual(result["status"], "FAIL")
                self.assertIs(result["Vulkan_raster_validation_passed"], False)
                self.assertNotIn("validated_pixels", result)

    def test_verify_file_refuses_existing_output_without_overwriting(self):
        with tempfile.TemporaryDirectory(prefix="alpha-unit-only-") as directory:
            parent = Path(directory)
            output = parent / "existing-unit-report.json"
            sentinel = b"preserve existing output exactly\n"
            output.write_bytes(sentinel)
            with self.assertRaisesRegex(ValueError, "fresh_verification_output_required"):
                alpha.verify_file(parent / "missing.json", output, run_id=RUN_ID, exit_code=0)
            self.assertEqual(output.read_bytes(), sentinel)

    def test_verify_cli_preserves_unavailable_classification_only_for_current_identity(self):
        for stale_field in (None, "run_id", "shader_sha256", "probe_sha256"):
            with self.subTest(stale_field=stale_field), tempfile.TemporaryDirectory(prefix="alpha-unit-only-") as directory:
                parent = Path(directory)
                receipt, output = parent / "fabricated-unit-input.json", parent / "unit-verification.json"
                report = unit_receipt()
                report.update(status="NOT_RUN", reason="real_Vulkan_backend_required",
                    backend="OpenGLCore", Unity_render_executed=False, rendered_case_count=0,
                    positive_case_count=0, negative_controls_detected=0, cases=[])
                if stale_field is not None:
                    report[stale_field] = "stale-unit-only-value"
                receipt.write_text(json.dumps(report))
                arguments = ["probe", "verify", "--receipt", str(receipt), "--out", str(output),
                             "--run-id", RUN_ID, "--exit-code", "2"]
                with patch("sys.argv", arguments), patch.object(alpha, "source_hashes", return_value=HASHES), \
                        redirect_stdout(io.StringIO()):
                    self.assertEqual(alpha.main(), 2)
                result = json.loads(output.read_text())
                self.assertIs(result["Unity_render_executed"], False)
                self.assertIs(result["Vulkan_raster_validation_passed"], False)
                if stale_field is None:
                    self.assertEqual(result["status"], "NOT_RUN")
                    self.assertEqual(result["receipt_status"], "NOT_RUN")
                    self.assertIn("real_Vulkan_backend_required", result["reason"])
                else:
                    self.assertEqual(result["status"], "FAIL")
                    self.assertNotIn("receipt_status", result)
                    self.assertNotIn("receipt_reason", result)

    def test_verify_cli_preserves_failed_draw_evidence_but_rejects_stale_render_claim(self):
        for stale_field in (None, "run_id", "shader_sha256", "probe_sha256"):
            with self.subTest(stale_field=stale_field), tempfile.TemporaryDirectory(prefix="alpha-unit-only-") as directory:
                parent = Path(directory)
                receipt, output = parent / "fabricated-unit-input.json", parent / "unit-verification.json"
                report = unit_receipt()
                report.update(status="FAIL", reason="pixel_or_negative_control_mismatch")
                row_named(report, "straight_alpha")["samples"][0]["observed"] = [0., 0., 0., 1.]
                if stale_field is not None:
                    report[stale_field] = "stale-unit-only-value"
                receipt.write_text(json.dumps(report))
                arguments = ["probe", "verify", "--receipt", str(receipt), "--out", str(output),
                             "--run-id", RUN_ID, "--exit-code", "2"]
                with patch("sys.argv", arguments), patch.object(alpha, "source_hashes", return_value=HASHES), \
                        redirect_stdout(io.StringIO()):
                    self.assertEqual(alpha.main(), 2)
                result = json.loads(output.read_text())
                self.assertEqual(result["status"], "FAIL")
                self.assertIs(result["Vulkan_raster_validation_passed"], False)
                self.assertIs(result["Unity_render_executed"], stale_field is None)
                self.assertNotIn("validated_pixels", result)
                if stale_field is None:
                    self.assertEqual(result["receipt_status"], "FAIL")
                    self.assertEqual(result["receipt_reason"], "pixel_or_negative_control_mismatch")
                else:
                    self.assertNotIn("receipt_status", result)
                    self.assertNotIn("receipt_reason", result)

    def test_mock_receipt_and_known_zero_half_alpha_reference(self):
        validated = validate(unit_receipt())
        self.assertEqual(validated["validated_cases"], 5)
        self.assertEqual(validated["validated_pixels"], 120)
        self.assertEqual(validated["negative_controls_detected"], 3)
        # Independently computed alpha0 and alpha0.5 values, including retained background.
        self.assertEqual(alpha.expected_pixel("straight_alpha", 0), (BG, BG))
        self.assertEqual(alpha.expected_pixel("straight_alpha", 1),
                         ([.3125, .21875, .25, 1.], [.3125, .21875, .25, 1.]))
        self.assertEqual(alpha.expected_pixel("straight_alpha", 4),
                         ([.09375, .3125, .34375, 1.], [.09375, .3125, .34375, 1.]))

    def test_wrong_identity_backend_scope_and_exit_are_rejected(self):
        changes = {"backend": "OpenGLCore", "Unity_version": "2021.3.44f1",
            "active_color_space": "Gamma", "run_id": "stale_previous_run",
            "shader_sha256": "3" * 64, "probe_sha256": "4" * 64,
            "Unity_render_executed": False, "synthetic_only": False,
            "Android_device": True, "production_pixels": True, "XAPK": True,
            "rendered_case_count": True, "negative_controls_detected": 2}
        for key, value in changes.items():
            with self.subTest(field=key):
                report = unit_receipt()
                report[key] = value
                with self.assertRaises(ValueError):
                    validate(report)
        for exit_code in (1, 2, -9, None, False, "0"):
            with self.subTest(exit_code=exit_code), self.assertRaises(ValueError):
                validate(unit_receipt(), exit_code=exit_code)

    def test_missing_duplicate_or_unknown_cases_are_rejected(self):
        for corruption in ("missing", "duplicate", "unknown"):
            with self.subTest(corruption=corruption):
                report = unit_receipt()
                if corruption == "missing":
                    report["cases"].pop()
                elif corruption == "duplicate":
                    report["cases"][-1] = deepcopy(report["cases"][0])
                else:
                    report["cases"][-1]["name"] = "unverified_case"
                with self.assertRaises(ValueError):
                    validate(report)

    def test_missing_pixels_duplicate_coordinates_and_invalid_positions_rejected(self):
        for corruption in ("missing", "duplicate", "outside", "bool_coordinate", "wrong_count"):
            with self.subTest(corruption=corruption):
                report = unit_receipt()
                row = report["cases"][0]
                if corruption == "missing":
                    row["samples"].pop()
                elif corruption == "duplicate":
                    row["samples"][-1] = deepcopy(row["samples"][0])
                elif corruption == "outside":
                    row["samples"][0]["x"] = 6
                elif corruption == "bool_coordinate":
                    row["samples"][0]["x"] = False
                else:
                    row["checked_pixel_count"] = 23
                with self.assertRaises(ValueError):
                    validate(report)

    def test_nonfinite_and_nonnumeric_pixel_or_summary_values_rejected(self):
        for field, value in (("observed", float("nan")), ("expected", float("inf")),
                             ("intended", True), ("observed", "0.5")):
            with self.subTest(field=field, value=value):
                report = unit_receipt()
                report["cases"][0]["samples"][0][field][0] = value
                with self.assertRaises(ValueError):
                    validate(report)
        report = unit_receipt()
        report["max_error"] = float("nan")
        with self.assertRaises(ValueError):
            validate(report)

    def test_forged_oracles_and_numeric_summaries_cannot_mask_bad_pixels(self):
        for corruption in ("oracle", "case_error", "case_mismatch", "total_error"):
            with self.subTest(corruption=corruption):
                report = unit_receipt()
                row = report["cases"][0]
                if corruption == "oracle":
                    # A self-consistent but wrong observed/expected pair must not pass.
                    row["samples"][0]["observed"][0] = .25
                    row["samples"][0]["expected"][0] = .25
                elif corruption == "case_error":
                    row["samples"][0]["observed"][0] = .001  # Within tolerance, summary still forged0.
                elif corruption == "case_mismatch":
                    report["cases"][-1]["intended_mismatch"] = .99
                else:
                    report["max_error"] = .001
                with self.assertRaises(ValueError):
                    validate(report)

    def test_dropped_texture_tint_or_alpha_blend_fails_despite_pass_flags(self):
        mutations = (("opaque_texture_tint", [TINT] * 6),
                     ("opaque_texture_tint", RAW_OPAQUE),
                     ("straight_alpha", OPAQUE),
                     ("straight_alpha", [BG] * 6))
        for name, actual in mutations:
            with self.subTest(case=name, actual=actual):
                report = unit_receipt()
                for sample in row_named(report, name)["samples"]:
                    sample["observed"] = list(actual[sample["x"]])
                with self.assertRaises(ValueError):
                    validate(report)

    def test_controls_require_the_predicted_fault_not_arbitrary_bad_pixels(self):
        for name in ("missing_texture_binding", "missing_tint_binding", "disabled_blending"):
            for corruption in ("no_fault", "arbitrary_black"):
                with self.subTest(case=name, corruption=corruption):
                    report = unit_receipt()
                    for sample in row_named(report, name)["samples"]:
                        sample["observed"] = (list(sample["intended"]) if corruption == "no_fault"
                                              else [0., 0., 0., 1.])
                    with self.assertRaises(ValueError):
                        validate(report)

    def test_malformed_json_object_shapes_fail_with_a_caught_validation_error(self):
        for location in ("root", "case", "sample"):
            with self.subTest(location=location):
                report = unit_receipt()
                if location == "root":
                    report = []
                elif location == "case":
                    report["cases"][0] = []
                else:
                    report["cases"][0]["samples"][0] = []
                # execute() catches ValueError and writes a failed wrapper receipt.
                with self.assertRaises(ValueError):
                    validate(report)


if __name__ == "__main__":
    unittest.main()
