"""Synthetic fail-closed tests for the W2 external material pointer classifier.

No original game data is required: every case uses pure functions or a tiny
temporary fixture root. These tests must stay independent of LFS hydration.
"""

from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from scripts.probe_w2_external_material_shader_refs import (
    AGGREGATE_TOP_KEYS,
    classify_pointer,
    classify_target,
    external_index,
)


class ExternalIndexTests(unittest.TestCase):
    def test_file_id_one_maps_to_first_external(self):
        self.assertEqual(external_index(1), 0)

    def test_file_id_three_maps_to_third_external(self):
        self.assertEqual(external_index(3), 2)

    def test_file_id_zero_means_own_owner(self):
        self.assertIsNone(external_index(0))

    def test_negative_file_id_unresolved(self):
        self.assertIsNone(external_index(-4))

    def test_non_integer_rejected(self):
        with self.assertRaises(ValueError):
            external_index("3")

    def test_missing_file_id_rejected(self):
        with self.assertRaises(ValueError):
            external_index(None)


class ClassifyPointerTests(unittest.TestCase):
    def test_internal_pointer(self):
        self.assertEqual(classify_pointer(0, 3), "own")

    def test_external_within_table(self):
        self.assertEqual(classify_pointer(2, 3), "external")

    def test_beyond_table_unresolved(self):
        self.assertEqual(classify_pointer(4, 3), "unresolved:oob-beyond-table")

    def test_negative_unresolved(self):
        self.assertEqual(classify_pointer(-1, 3), "unresolved:oob-negative-or-zero-own")

    def test_zero_owners_table(self):
        self.assertEqual(classify_pointer(1, 0), "unresolved:oob-beyond-table")


class ClassifyTargetTests(unittest.TestCase):
    def test_exists_reports_object_type(self):
        self.assertEqual(classify_target(7, {"Shader": {7, 9}}), "target-exists:Shader")

    def test_missing_when_not_present(self):
        self.assertEqual(classify_target(8, {"Shader": {7, 9}}), "target-missing")

    def test_unvalidated_without_owner_sets(self):
        self.assertEqual(classify_target(7, {}), "target-unvalidated")

    def test_null_path_id(self):
        self.assertEqual(classify_target(0, {"Shader": {7}}), "target:null-path-id")


class AggregateSchemaTests(unittest.TestCase):
    def test_expected_top_keys_are_fixed(self):
        self.assertEqual(
            AGGREGATE_TOP_KEYS,
            {
                "schema_version",
                "owners",
                "material_shader",
                "material_texture_env",
                "convention_control",
                "distinct_external_targets",
                "target_validation",
                "validation_owners",
                "no_unity_or_gpu_execution",
                "original_payloads_modified",
                "aggregate_only",
            },
        )

    def test_aggregate_counter_has_no_path_ids(self):
        sample = {"resources.assets:external:sharedassets0.assets": 142}
        as_json = json.dumps(sample)
        self.assertNotIn("pathID", as_json)
        self.assertNotIn("10101", as_json)


class PinVerificationTests(unittest.TestCase):
    def test_wrong_size_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "resources.assets").write_bytes(b"0" * 10)
            from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources

            pins = {name: EXPECTED[name] for name in ("resources.assets",)}
            with self.assertRaises(ValueError):
                verify_sources(root, pointers_only=False, expected=pins)

    def test_missing_owner_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            from scripts.verify_targeted_lfs_compute_sources import EXPECTED, verify_sources

            pins = {name: EXPECTED[name] for name in ("resources.assets",)}
            with self.assertRaises(ValueError):
                verify_sources(root, pointers_only=False, expected=pins)


if __name__ == "__main__":
    unittest.main()
