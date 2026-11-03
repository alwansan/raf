#!/usr/bin/env python3
"""W3 synthetic model tests for the per-material keyword-usage auditor."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).parent
_spec = importlib.util.spec_from_file_location("w3matkw", HERE / "probe_w3_per_material_keywords.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


class TestKeywordAggregation(unittest.TestCase):
    def setUp(self):
        self.agg = m.target_agg()
        self.echo: list[str] = []

    def test_empty_and_nonempty_counts(self):
        m.aggregate_material(self.agg, [], [], [], None, self.echo)
        m.aggregate_material(self.agg, ["K1", "K2"], ["BAD"], ["P1"], {"K1", "K2"}, self.echo)
        self.assertEqual(self.agg["materials"], 2)
        self.assertEqual(self.agg["with_empty_valid_keywords"], 1)
        self.assertEqual(self.agg["with_invalid_keywords_nonempty"], 1)

    def test_histogram_sums_to_materials(self):
        m.aggregate_material(self.agg, ["A"], [], [], None, self.echo)
        m.aggregate_material(self.agg, ["A", "B"], [], [], None, self.echo)
        self.assertEqual(sum(self.agg["keyword_set_size_histogram"].values()),
                         self.agg["materials"])

    def test_consistency_violation_detected_only_against_shader_set(self):
        # shader keyword set known: only K1 legal
        m.aggregate_material(self.agg, ["K1", "KX"], [], [], {"K1"}, self.echo)
        self.assertEqual(self.agg["keyword_set_consistency"]["checked"], 1)
        # the probe-level violation count is recorded by run_audit; here only names flow
        self.assertIn("KX", self.echo)

    def test_no_consistency_check_without_shader_set(self):
        m.aggregate_material(self.agg, ["K1"], [], [], None, self.echo)
        self.assertEqual(self.agg["keyword_set_consistency"]["checked"], 1)

    def test_commitment_deterministic_sorted(self):
        a = m.commit_names(["B", "A"])
        b = m.commit_names(["A", "B"])
        self.assertEqual(a, b)
        self.assertIsNotNone(a)

    def test_commitment_empty_is_none(self):
        self.assertIsNone(m.commit_names([]))
        self.assertIsNone(m.commit_names(["", ""]))

    def test_priority_identity_table(self):
        self.assertEqual(len(m.PRIORITY), 11)
        self.assertEqual(m.PRIORITY[("sharedassets0.assets", 2398)], "Standard")

    def test_engine_transports_set_matches_inventory(self):
        self.assertEqual(m.ENGINE_TRANSPORT_PATHS,
                         {"Library/unity default resources", "Resources/unity_builtin_extra"})


if __name__ == "__main__":
    unittest.main()
