#!/usr/bin/env python3
"""W3 synthetic model tests for the m_SavedProperties slot-coverage auditor."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).parent
_spec = importlib.util.spec_from_file_location("w3slotcov", HERE / "probe_w3_savedprops_slot_coverage.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


class TestSlotCoverage(unittest.TestCase):
    def setUp(self):
        self.agg = m.target_agg()
        self.echo: list[str] = []

    def test_shader_texture_slots_type4_only(self):
        parsed = {"m_PropInfo": {"m_Props": [
            {"m_Type": 4, "m_Name": "T1"}, {"m_Type": 2, "m_Name": "F1"},
            {"m_Type": 0, "m_Name": "C1"}, {"m_Type": 3, "m_Name": "R1"}]}}
        self.assertEqual(m.shader_texture_slots(parsed), {"T1"})

    def test_shader_texture_slots_non_string_rejected(self):
        parsed = {"m_PropInfo": {"m_Props": [{"m_Type": 4}, {"m_Type": 4, "m_Name": 5}]}}
        self.assertEqual(m.shader_texture_slots(parsed), set())

    def test_material_texenv_slots_tuple_form(self):
        # authentic UnityPy serialized-map shape: (name, {m_Texture: PPtr, m_Scale, m_Offset})
        mat = {"m_SavedProperties": {"m_TexEnvs": [
            ("_BumpMap", {"m_Texture": {"m_FileID": 0, "m_PathID": 1291},
                          "m_Scale": {"x": 1.0, "y": 1.0}, "m_Offset": {"x": 0.0, "y": 0.0}}),
            ("_MainTex", {"m_Texture": {"m_FileID": 69, "m_PathID": -42},
                          "m_Scale": {"x": 1.0, "y": 1.0}, "m_Offset": {"x": 0.0, "y": 0.0}})]}}
        self.assertEqual(m.material_texenv_slots(mat), {"_BumpMap", "_MainTex"})

    def test_material_texenv_slots_mixed_never_silent(self):
        mat = {"m_SavedProperties": {"m_TexEnvs": [
            {"m_First": "A", "m_Second": {}},
            ("B", {"m_Texture": {}}), (5, {}),
            ("C", {"m_Texture": {}})]}}
        # non-string keys are discarded explicitly, never silently as blank names
        self.assertEqual(m.material_texenv_slots(mat), {"A", "B", "C"})

    def test_material_texenv_slots(self):
        mat = {"m_SavedProperties": {"m_TexEnvs": [
            {"m_First": "A", "m_Second": {"m_FileID": 0, "m_PathID": 1}},
            {"m_First": "B", "m_Second": {"m_FileID": 0, "m_PathID": -1}}]}}
        self.assertEqual(m.material_texenv_slots(mat), {"A", "B"})
        # PPtr identity is never recorded here — structure-only aggregation

    def test_material_empty(self):
        self.assertEqual(m.material_texenv_slots({}), set())

    def test_coverage_counts(self):
        self.assertEqual(m.coverage_counts({"A", "B"}, {"A", "C"}), (1, 1))
        self.assertEqual(m.coverage_counts({"A"}, {"A", "B", "C"}), (0, 2))
        self.assertEqual(m.coverage_counts(set(), set()), (0, 0))

    def test_aggregation_perfect_vs_gap(self):
        m.aggregate_material(self.agg, {"A", "B"}, {"A", "B"}, self.echo)
        m.aggregate_material(self.agg, {"A"}, set(), self.echo)
        self.assertEqual(self.agg["materials"], 2)
        self.assertEqual(self.agg["materials_all_declared_slots_present"], 1)
        self.assertEqual(self.agg["missing_slot_occurrences_total"], 1)
        self.assertIn("MISS:A", self.echo)

    def test_commitment_empty_rejected(self):
        self.assertIsNone(m.commit_names([]))
        self.assertIsNone(m.commit_names([""]))

    def test_priority_identity_size(self):
        self.assertEqual(len(m.PRIORITY), 11)


if __name__ == "__main__":
    unittest.main()
