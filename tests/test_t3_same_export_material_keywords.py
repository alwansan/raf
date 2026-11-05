"""T3 Material keyword/pass parity source-free regression controls.

Real acceptance requires the separate SHA-locked original/export pipeline;
synthetic fixtures deliberately make no claims about game pixels.
"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest import mock

from scripts import b43_material_keyword_fidelity as b43
from scripts import t3_same_export_material_keywords as t3
from scripts import t3_same_export_material_colors as t3colors


def fixture():
    source = {}
    exported = {}
    rows = []
    for i in range(1, t3.COUNT + 1):
        src = (t3.OWNER, i)
        dst = (2100000 + i, "b" * 32)
        # Cover nontrivial valid/invalid and disabled pass data.
        values = (("ALPHA_TEST", "WATER"), ("LEGACY",), ("SHADOWCASTER",))
        source[src] = values
        exported[dst] = values
        rows.append({
            "class_id": 21,
            "source": {"owner": t3.OWNER, "path_id": i},
            "export": {"file_id": dst[0], "guid": dst[1], "type": 2},
            "exportable": True,
        })
    w1 = {"schema_version": 1, "export_instance": "a" * 32,
          "objects": rows}
    b02 = {"schema_version": 1, "export_instance": "a" * 32,
           "objects": [{"class_id": 28}]}
    return w1, b02, source, exported


class ScopedKeywordControls(unittest.TestCase):
    def test_full_source_default_unchanged_and_forbidden_scope_fails_closed(self):
        with self.assertRaisesRegex(b43.GuardError, "unapproved_original"):
            b43.source_materials(Path("."), selected_owners={"not-pinned.assets"})
        with self.assertRaisesRegex(b43.GuardError, "unapproved_original"):
            b43.source_materials(Path("."), selected_owners=set())

    def test_true_scoped_comparison_with_original_41_traces(self):
        w1, b02, source, exported = fixture()
        trace = t3colors.select_same_export_materials(w1, b02)
        accepted = t3.aggregate(b43.compare(trace, source, exported))
        self.assertEqual(accepted["status"], "SCOPED_KEYWORD_PASS_MATCH")
        self.assertEqual(accepted["source_objects"], 41)
        self.assertTrue(accepted["original_material_shader_keyword_or_pass_fidelity_proven"])
        self.assertFalse(accepted["shader_program_or_variant_equivalence_verified"])
        self.assertFalse(accepted["android_device_pixels_verified"])
        self.assertFalse(accepted["ready_for_build"])

    def test_missing_or_changed_keyword_fails_without_success_flags(self):
        w1, b02, source, exported = fixture()
        broken = dict(exported)
        broken[next(iter(broken))] = (("ALPHA_TEST",), ("LEGACY",), ("SHADOWCASTER",))
        with self.assertRaisesRegex(b43.GuardError, "mismatch"):
            b43.compare(t3colors.select_same_export_materials(w1, b02), source, broken)

    def test_disabled_pass_drift_not_accepted(self):
        w1, b02, source, exported = fixture()
        broken = dict(exported)
        broken[next(iter(broken))] = (("ALPHA_TEST", "WATER"), ("LEGACY",), ())
        with self.assertRaisesRegex(b43.GuardError, "mismatch"):
            b43.compare(t3colors.select_same_export_materials(w1, b02), source, broken)

    def test_cross_export_trace_rejected(self):
        w1, b02, _, _ = fixture()
        b02["export_instance"] = "c" * 32
        with self.assertRaisesRegex(ValueError, "Different exporter instances"):
            t3colors.select_same_export_materials(w1, b02)

    def test_extra_original_material_trace_rejected(self):
        w1, b02, _, _ = fixture()
        w1["objects"].append({
            "class_id": 21,
            "source": {"owner": t3.OWNER, "path_id": 42},
            "export": {"file_id": 2100042, "guid": "b" * 32, "type": 2},
            "exportable": True,
        })
        with self.assertRaisesRegex(ValueError, "population"):
            t3colors.select_same_export_materials(w1, b02)

    def test_reject_false_private_aggregate_or_leaked_extra_data(self):
        ok = {"status": "MATCH", "source_objects": 41, "export_documents": 41,
              "predefined_redirects": 0, "implicit_font_exclusions": 0,
              "keyword_state_equal": True,
              "shader_program_or_variant_equivalence_verified": False,
              "unity_or_device_verified": False, "ready_for_build": False,
              "private_material_name": "must-not-appear",
              "original_guid": "private"}
        safe = t3.aggregate(ok)
        self.assertNotIn("private_material_name", safe)
        self.assertNotIn("original_guid", safe)
        for field, changed in (("source_objects", 40),
                               ("keyword_state_equal", False),
                               ("ready_for_build", True),
                               ("shader_program_or_variant_equivalence_verified", True)):
            item = dict(ok, **{field: changed})
            with self.subTest(field=field), self.assertRaises(ValueError):
                t3.aggregate(item)

    def test_wrapper_calls_byte_pinned_selected_owner_mode(self):
        w1, b02, original, exported = fixture()
        with TemporaryDirectory() as td:
            root = Path(td)
            (root / "w1.json").write_text(json.dumps(w1))
            (root / "b02.json").write_text(json.dumps(b02))
            with (mock.patch.object(b43, "source_materials", return_value=original) as src,
                  mock.patch.object(b43, "exported_materials", return_value=exported)):
                result = t3.run(root, root, root / "w1.json", root / "b02.json")
            src.assert_called_once_with(root, selected_owners={t3.OWNER})
            self.assertEqual(result["export_documents"], 41)

    def test_result_written_only_as_safe_inconclusive_on_private_failure(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            w1, b02, _, _ = fixture()
            (root / "w1.json").write_text(json.dumps(w1))
            (root / "b02.json").write_text(json.dumps(b02))
            with mock.patch.object(b43, "source_materials", side_effect=ValueError("PRIVATE SHADER NAME")):
                rc = t3.main([
                    "--original", str(root / "original"),
                    "--project", str(root / "export"),
                    "--w1-trace", str(root / "w1.json"),
                    "--b02-trace", str(root / "b02.json"),
                    "--out", str(root / "public.json"),
                ])
            self.assertEqual(rc, 2)
            public = (root / "public.json").read_text()
            self.assertNotIn("PRIVATE", public)
            self.assertEqual(json.loads(public)["status"], "INCONCLUSIVE")


if __name__ == "__main__":
    unittest.main()
