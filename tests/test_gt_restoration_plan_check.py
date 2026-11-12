"""Source-free negative controls for GT's persistent restoration plan."""
from __future__ import annotations
import copy
import json
import unittest
from pathlib import Path

from scripts.gt_restoration_plan_check import check, _read

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "clients/GT/RESTORATION_PLAN.json"
STATE = ROOT / "clients/GT/state.json"
EVIDENCE = ROOT / "clients/GT/evidence/20261112_cl_device_graphics_failure_receipt.json"


class GTRestorationLedgerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plan = _read(PLAN)
        cls.state = _read(STATE)
        cls.evidence = _read(EVIDENCE)

    def verify(self, plan=None, state=None, evidence=None):
        return check(
            copy.deepcopy(self.plan if plan is None else plan),
            copy.deepcopy(self.state if state is None else state),
            copy.deepcopy(self.evidence if evidence is None else evidence))

    def test_real_source_and_owner_log_snapshots_consistent(self):
        result = self.verify()
        self.assertEqual(result["workstreams"], 12)
        self.assertEqual(result["milestones"], 6)
        self.assertEqual(result["source_owner_count"], 82)
        self.assertEqual(result["remaining_postvendor_dummy_material_docs"], 770)
        self.assertEqual(result["owner_device_water_error_count"], 42229)
        self.assertEqual(result["device_proof_workstreams"], 0)
        self.assertTrue(result["native_build_latest_result_unverified"])

    def test_original_source_sha_or_LFS_policy_changed_rejected(self):
        for mutation in ("bad_source", "lfs_allowed", "unsafe_meta"):
            plan = copy.deepcopy(self.plan)
            if mutation == "bad_source":
                plan["original_source"]["sha"] = "0"*40
            elif mutation == "lfs_allowed":
                plan["original_source"]["git_lfs_allowed"] = True
            else:
                plan["original_source"][
                    "original_meta_or_scene_guid_modification_allowed_without_proof"] = True
            with self.subTest(mutation=mutation), self.assertRaisesRegex(
                    ValueError, "original_source_policy_drift"):
                self.verify(plan=plan)

    def test_dropped_workstream_or_duplicate_milestone_rejected(self):
        plan = copy.deepcopy(self.plan)
        plan["workstreams"].pop()
        with self.assertRaisesRegex(ValueError, "workstreams"):
            self.verify(plan=plan)
        plan = copy.deepcopy(self.plan)
        plan["milestones"][2]["id"] = "M1"
        with self.assertRaisesRegex(ValueError, "milestones"):
            self.verify(plan=plan)

    def test_falsely_reduced_remaining_dummy_material_count_rejected(self):
        plan = copy.deepcopy(self.plan)
        plan["workstreams"][4]["scope"]["custom_dummy_after_vendor_restorers"] = 0
        with self.assertRaisesRegex(ValueError, "P04_dummy_docs"):
            self.verify(plan=plan)

    def test_fake_GPU_phone_evidence_rejected(self):
        plan = copy.deepcopy(self.plan)
        plan["workstreams"][6]["device_verified"] = True
        with self.assertRaisesRegex(ValueError, "device_acceptance"):
            self.verify(plan=plan)
        plan["workstreams"][6]["device_acceptance"] = {
            "strict_known_log_gate_passed": False,
            "apk_sha256": "a"*64, "phone_render_samples": 4,
            "session_id": "newer"}
        with self.assertRaisesRegex(ValueError, "unproven_device_acceptance"):
            self.verify(plan=plan)

    def test_water_drift_from_real_CL_receipt_rejected(self):
        plan = copy.deepcopy(self.plan)
        plan["workstreams"][6]["scope"]["device_spectrum_errors"] = 100
        with self.assertRaisesRegex(ValueError, "P06_device_spectrum_errors"):
            self.verify(plan=plan)
        evidence = copy.deepcopy(self.evidence)
        evidence["error_counts"]["invalid_kernel_index_6"] = 0
        with self.assertRaisesRegex(ValueError, "CL_invalid_kernel_index_6"):
            self.verify(evidence=evidence)

    def test_stale_new_build_run_rejected(self):
        plan = copy.deepcopy(self.plan)
        plan["reference_runs"]["new_native_active_at_snapshot"] = 1
        with self.assertRaisesRegex(ValueError, "current_native_run"):
            self.verify(plan=plan)

    def test_first_unproven_milestone_cannot_be_marked_complete(self):
        plan = copy.deepcopy(self.plan)
        plan["milestones"][1]["status"] = "complete"
        with self.assertRaisesRegex(ValueError, "milestone_complete_without_acceptance"):
            self.verify(plan=plan)

    def test_missing_proof_stage_or_numbered_evidence_rejected(self):
        plan = copy.deepcopy(self.plan)
        del plan["workstreams"][0]["export_verified"]
        with self.assertRaisesRegex(ValueError, "missing_stage_proof"):
            self.verify(plan=plan)
        plan = copy.deepcopy(self.plan)
        plan["workstreams"][0]["evidence"] = []
        with self.assertRaisesRegex(ValueError, "missing_numbered_evidence"):
            self.verify(plan=plan)


if __name__ == "__main__":
    unittest.main()
