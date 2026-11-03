#!/usr/bin/env python3
"""W3 synthetic model tests for the priority-shader property/keyword schema extractor."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

HERE = Path(__file__).parent
_spec = importlib.util.spec_from_file_location("w3schema", HERE / "probe_w3_shader_property_schema.py")
m = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(m)


def parsed_of(props, keywords=None, deps=None):
    return {"m_PropInfo": {"m_Props": props},
            "m_KeywordNames": keywords or [],
            "m_Dependencies": deps or []}


class TestSchemaExtractor(unittest.TestCase):
    def test_type_mapping(self):
        s = m.extract_schema(parsed_of([
            {"m_Type": 0, "m_Name": "c1"}, {"m_Type": 1, "m_Name": "v1"},
            {"m_Type": 2, "m_Name": "f1"}, {"m_Type": 3, "m_Name": "r1"},
            {"m_Type": 4, "m_Name": "t1"},
        ]))
        self.assertEqual(s["props_by_type"], {"Color": 1, "Vector": 1, "Float": 1,
                                              "ScalarType3": 1, "Texture": 1, "unknown": 0})

    def test_unknown_type_kept_out_of_named_buckets(self):
        s = m.extract_schema(parsed_of([{"m_Type": 99, "m_Name": "x"}]))
        self.assertEqual(s["props_by_type"]["unknown"], 1)
        self.assertEqual(s["props_total"], 1)

    def test_missing_name_fail_closed(self):
        s = m.extract_schema(parsed_of([{"m_Type": 2}]))
        self.assertEqual(s["props_by_type"]["Float"], 0)
        self.assertEqual(s["props_by_type"]["unknown"], 1)
        self.assertIsNone(s["name_lists_commitment"]["all"])

    def test_empty_inputs(self):
        s = m.extract_schema(parsed_of([]))
        self.assertEqual(s["props_total"], 0)
        self.assertIsNone(s["keywords_commitment"])
        self.assertEqual(s["keyword_names_count"], 0)
        self.assertEqual(s["dependencies_count"], 0)

    def test_commitment_is_deterministic_sorted(self):
        a = m.extract_schema(parsed_of([{"m_Type": 2, "m_Name": "b"}, {"m_Type": 2, "m_Name": "a"}]))
        b = m.extract_schema(parsed_of([{"m_Type": 2, "m_Name": "a"}, {"m_Type": 2, "m_Name": "b"}]))
        self.assertEqual(a["name_lists_commitment"]["all"], b["name_lists_commitment"]["all"])

    def test_keyword_commitment(self):
        s = m.extract_schema(parsed_of([], keywords=["ALPHA", "BETA"]))
        self.assertEqual(s["keyword_names_count"], 2)
        self.assertEqual(s["keywords_commitment"],
                         "ca0beabf6e4a8b9036f018785569eb4f7fdd993384127f34d6673d5d618ec58e")

    def test_dependency_commitment(self):
        s = m.extract_schema(parsed_of([], deps=[{"m_DependencyShaderName": "D1"}]))
        self.assertEqual(s["dependencies_count"], 1)
        self.assertIsNotNone(s["dependencies_commitment"])

    def test_dependency_non_string_ignored(self):
        s = m.extract_schema(parsed_of([], deps=[{"m_DependencyShaderName": 5}, {}]))
        self.assertIsNone(s["dependencies_commitment"])


if __name__ == "__main__":
    unittest.main()
