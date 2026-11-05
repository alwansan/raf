"""T5: exact real native-run water limitation acknowledgement replay.

This is a source-free test of the unchanged production acknowledgement guard.
The five shader booleans come from CI42052375742's public aggregate output;
no original shader, GUID, bytecode, game data or device result is accessed.
"""
from copy import deepcopy
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from scripts.record_documented_water_limitation import check, unmet_conditions
from scripts.verify_water_render_contract import REQUIRED_PASS_COUNT, native_ready


FIXTURE = Path(__file__).parent / "fixtures" / "t5_native_water_42052375742.json"
ORIGINAL_SOURCE = "b0c4b4c05011d915cd845259f06b5f80ee368092"
RUN_ID = 42052375742


class T5LiveWaterAcknowledgment(unittest.TestCase):
    def setUp(self):
        self.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.report = deepcopy(self.fixture["aggregated_live_report"])
        self.old = self.fixture["original_request_list"]
        self.corrected = self.fixture["expected_corrected_list"]

    def _execute(self, root, acknowledgements, report=None):
        project = Path(root) / "project"
        project.mkdir(exist_ok=True)
        request = Path(root) / "request.json"
        request.write_text(
            json.dumps({
                "request_id": "t5-exact-live-aggregate-source-gated",
                "documented_water_limitations": acknowledgements,
            }), encoding="utf-8"
        )
        target = Path(root) / "experimental-water-limitation.json"
        with patch("scripts.record_documented_water_limitation.inspect",
                   return_value=(self.report if report is None else report)):
            return check(project, request, target)

    def test_provenance_is_exact_failed_immutable_run(self):
        p = self.fixture["provenance"]
        self.assertEqual(p["github_run_id"], RUN_ID)
        self.assertEqual(p["source_sha"], ORIGINAL_SOURCE)
        self.assertEqual(p["job_id"], 127331915972)
        self.assertIn("Authentic water gate", p["failed_step"])

    def test_original_shader_contract_population_is_complete(self):
        self.assertEqual(
            set(self.report["shader_contracts"]), set(REQUIRED_PASS_COUNT)
        )
        self.assertFalse(native_ready(self.report))
        self.assertFalse(self.report["device_execution_verified"])
        self.assertFalse(self.report["authentic_water_kernel_identity_verified"])

    def test_expected_corrected_ack_is_exact_actual_guard_output(self):
        self.assertEqual(set(self.corrected), set(unmet_conditions(self.report)))
        self.assertEqual(len(self.corrected), 5)
        self.assertEqual(len(set(self.corrected)), 5)

    def test_old_request_rejected_by_actual_guard(self):
        with TemporaryDirectory() as root:
            with self.assertRaisesRegex(
                    ValueError, "do not exactly match the live unmet conditions"):
                self._execute(root, self.old)
            self.assertFalse(
                (Path(root) / "experimental-water-limitation.json").exists()
            )

    def test_corrected_request_is_experimental_only(self):
        with TemporaryDirectory() as root:
            record = self._execute(root, self.corrected)
            self.assertTrue(record["experimental"])
            self.assertEqual(record["strict_water_gate"], "not_passed")
            self.assertFalse(record["authentic_water_kernel_identity_verified"])
            self.assertFalse(record["device_execution_verified"])
            self.assertFalse(record["water_compute_source_candidate_present"])
            self.assertFalse(record["modified_source"])
            self.assertEqual(
                set(record["unmet_conditions"]), set(self.corrected)
            )
            self.assertEqual(
                json.loads(
                    (Path(root) / "experimental-water-limitation.json").read_text()
                )["unmet_conditions"], sorted(self.corrected)
            )

    def test_changed_entries_are_exactly_blur_out_depth_in(self):
        removed = set(self.old) - set(self.corrected)
        added = set(self.corrected) - set(self.old)
        self.assertEqual(
            removed,
            {"shader_pass_contract:UltimateWater/Utilities/Blur (Subsurface Scattering)"}
        )
        self.assertEqual(
            added, {"shader_pass_contract:UltimateWater/Depth/Depth Copy"}
        )

    def test_stale_extra_blur_fails_closed(self):
        with TemporaryDirectory() as root:
            with self.assertRaises(ValueError):
                self._execute(
                    root, self.corrected +
                    ["shader_pass_contract:UltimateWater/Utilities/Blur (Subsurface Scattering)"]
                )

    def test_missing_depth_fails_closed(self):
        with TemporaryDirectory() as root:
            with self.assertRaises(ValueError):
                self._execute(
                    root, [x for x in self.corrected if "Depth/Depth Copy" not in x]
                )

    def test_unlisted_new_water_breakage_fails_closed(self):
        altered = deepcopy(self.report)
        altered["shader_contracts"]["Sandbox/VolumetricLight"][
            "contract_satisfied"
        ] = False
        with TemporaryDirectory() as root:
            with self.assertRaises(ValueError):
                self._execute(root, self.corrected, report=altered)

    def test_later_source_repair_of_depth_fails_stale_request(self):
        altered = deepcopy(self.report)
        altered["shader_contracts"]["UltimateWater/Depth/Depth Copy"][
            "contract_satisfied"
        ] = True
        with TemporaryDirectory() as root:
            with self.assertRaises(ValueError):
                self._execute(root, self.corrected, report=altered)

    def test_duplicate_ack_is_refused(self):
        with TemporaryDirectory() as root:
            with self.assertRaisesRegex(ValueError, "duplicated"):
                self._execute(root, self.corrected + [self.corrected[0]])

    def test_no_claim_that_blur_is_authenticated_gpu_program(self):
        self.assertTrue(
            self.report["shader_contracts"][
                "UltimateWater/Utilities/Blur (Subsurface Scattering)"
            ]["contract_satisfied"]
        )
        self.assertFalse(native_ready(self.report))
        self.assertFalse(self.report["authentic_water_kernel_identity_verified"])


if __name__ == "__main__":
    unittest.main()
