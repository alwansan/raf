#!/usr/bin/env python3
"""W3 synthetic model tests for the game-wide keyword consistency closure."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from types import SimpleNamespace
import sys

HERE = Path(__file__).parent
sys.path.insert(0, str(HERE))

_spec = importlib.util.spec_from_file_location("w3globalkw", HERE / "probe_w3_game_wide_keyword_closure.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


class TestGameWideClosure(unittest.TestCase):
    def test_inherited_shared_tooling_still_fail_closed(self):
        _spec2 = importlib.util.spec_from_file_location(
            "w3inv2", HERE / "probe_w3_full_material_shader_inventory.py")
        inv = importlib.util.module_from_spec(_spec2)
        _spec2.loader.exec_module(inv)
        tt = [SimpleNamespace(path="sharedassets0.assets"), SimpleNamespace(path="Library/unity default resources")]
        with self.assertRaises(inv.UnresolvedMaterialShaderLink):
            inv.resolve_owner_by_fileid(tt, -1)
        with self.assertRaises(inv.UnresolvedMaterialShaderLink):
            inv.resolve_owner_by_fileid(tt, 3)

    def test_agg_shape_for_unnamed_targets(self):
        agg = m.build_target_agg()
        self.assertEqual(agg["materials"], 0)
        self.assertIn("keyword_set_consistency", agg)

    def test_violation_counting_is_name_mentions(self):
        agg = m.build_target_agg()
        echo: list[str] = []
        # one material with TWO extra names must register 2 mentions, 1 material
        m.aggregate_material(agg, ["OK1", "BAD1", "BAD2"], [], [], {"OK1"}, echo)
        mentions = sum(1 for n in echo if n.startswith("VIOLATION:"))
        self.assertEqual(mentions, 2)
        self.assertEqual(agg["materials"], 1)

    def test_clean_material_zero_mentions(self):
        agg = m.build_target_agg()
        echo: list[str] = []
        m.aggregate_material(agg, ["A", "B"], [], [], {"A", "B"}, echo)
        self.assertEqual(sum(1 for n in echo if n.startswith("VIOLATION:")), 0)


if __name__ == "__main__":
    unittest.main()
