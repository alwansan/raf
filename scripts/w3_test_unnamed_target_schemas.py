#!/usr/bin/env python3
"""W3 synthetic model tests for the unnamed-target schema enumeration."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).parent
_spec = importlib.util.spec_from_file_location(
    "w3unnamed", HERE / "probe_w3_unnamed_target_schemas.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


class TestUnnamedSchemas(unittest.TestCase):
    def test_prop_type_hist_documented_enum(self):
        props = [{"m_Type": 0}, {"m_Type": 2}, {"m_Type": 2},
                 {"m_Type": 3}, {"m_Type": 4}]
        self.assertEqual(m.prop_type_hist(props),
                         {"Color": 1, "Float": 2, "Range": 1, "Texture": 1})

    def test_prop_type_hist_out_of_enum_fails_closed_to_unknown(self):
        self.assertEqual(m.prop_type_hist([{"m_Type": 99}]), {"unknown": 1})
        self.assertEqual(m.prop_type_hist([{}]), {"unknown": 1})

    def test_named_set_has_12_targets(self):
        self.assertEqual(len(m.NAMED), 12)

    def test_step7_artifact_exists_for_crosscheck(self):
        repo = HERE.parent
        self.assertTrue((repo / m.STEP7_ARTIFACT).exists())


if __name__ == "__main__":
    unittest.main()
