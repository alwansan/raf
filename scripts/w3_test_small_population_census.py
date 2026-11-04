#!/usr/bin/env python3
"""W3 synthetic model tests for the small-population census tooling."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).parent
_spec = importlib.util.spec_from_file_location("w3census", HERE / "probe_w3_small_population_census.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


class TestSmallPopulationCensus(unittest.TestCase):
    def test_expect_table_matches_committed_evidence(self):
        self.assertEqual(m.EXPECT["standard_reference_count"], 674)
        self.assertEqual(m.EXPECT["standardvcolor_reference_count"], 18)
        self.assertEqual(m.EXPECT["standard_empty_keyword_materials"], 22)

    def test_targets_identity(self):
        self.assertEqual(m.TARGET_STD[2], "Standard")
        self.assertEqual(m.TARGET_SVC[2], "StandardVColor")
        self.assertEqual(m.TARGET_SVC[:2], ("sharedassets36.assets", 880))

    def test_inherited_coverage_tooling(self):
        self.assertEqual(m.coverage_counts({"A"}, {"A"}), (0, 0))
        self.assertEqual(m.coverage_counts({"A", "B"}, {"B"}), (1, 0))

    def test_commitment_semantics_unchanged(self):
        self.assertIsNone(m.commit_names([]))
        self.assertIsNotNone(m.commit_names(["X"]))
        self.assertEqual(m.commit_names(["X", "Y"]), m.commit_names(["Y", "X"]))


if __name__ == "__main__":
    unittest.main()
