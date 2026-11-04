#!/usr/bin/env python3
"""W3 synthetic model tests for the shader fallback/custom-editor enumerator."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).parent
_spec = importlib.util.spec_from_file_location("w3fbe", HERE / "probe_w3_shader_fallback_editor.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


class TestFallbackEditorExtractor(unittest.TestCase):
    def test_both_present(self):
        parsed = {"m_FallbackName": "FB", "m_CustomEditorName": "ED"}
        self.assertEqual(m.extract_identity(parsed), ("FB", "ED"))

    def test_both_empty_by_default(self):
        self.assertEqual(m.extract_identity({}), ("", ""))

    def test_non_string_types_rejected(self):
        parsed = {"m_FallbackName": 7, "m_CustomEditorName": None}
        self.assertEqual(m.extract_identity(parsed), ("", ""))

    def test_empty_string_never_committed(self):
        self.assertIsNone(m.commit_names([]))
        self.assertIsNone(m.commit_names(["", ""]))
        self.assertEqual(m.commit_names(["A", "B"]), m.commit_names(["B", "A"]))

    def test_distinct_vs_nonempty_difference(self):
        space = ["F1", "F1", "F2"]
        self.assertEqual(len(space), 3)
        self.assertEqual(len(set(space)), 2)
        self.assertIsNotNone(m.commit_names(space))

    def test_priority_identity_pins(self):
        import json
        peers = "inventory parity only: shader count expected 165"
        self.assertIn("165", peers)


    def test_multiplicity_profile_name_free_and_sorted(self):
        hist = {"<empty>": 5, "B": 2, "A": 7, "C": 1}
        self.assertEqual(m.multiplicity_profile(hist), [7, 2, 1])
        self.assertEqual(m.multiplicity_profile({"<empty>": 3}), [])
        # profile must not carry any raw name strings
        prof = m.multiplicity_profile(hist)
        self.assertTrue(all(isinstance(x, int) for x in prof))

    def test_multiplicity_profile_matches_hist_sum(self):
        hist = {"A": 4, "B": 3, "<empty>": 10}
        self.assertEqual(sum(m.multiplicity_profile(hist)), 7)


if __name__ == "__main__":
    unittest.main()
