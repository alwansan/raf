"""B21 same-export source Light108 parity checks; no proprietary fixture required."""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts import b21_compare_export_lights as m

GUID = "a" * 32
INSTANCE = "b" * 32


def source_light(color=(0.6, 0.4, 0.8, 1.0)):
    return (1, 2, color, 0.75, 12.5)


def trace(source_id=123, target=108000, scene="level0", guid=GUID):
    return {
        "schema_version": 1,
        "export_instance": INSTANCE,
        "objects": [{
            "class_id": 108,
            "source": {"owner": scene, "path_id": source_id},
            "collection_type": "AssetRipper.Export.UnityProjects.SceneExportCollection",
            "export": {"file_id": target, "guid": guid, "type": 2}
        }],
        "nonexportable_light_objects_skipped": 0,
    }


def w1():
    return {"schema_version": 1, "export_instance": INSTANCE,
            "objects": [{"class_id": 21}]}


class TestSameExportLightParity(unittest.TestCase):
    def test_same_instance_exact_identity_compares_every_field(self):
        original = {("level0", 123): source_light()}
        actual = {(GUID, 108000): source_light()}
        result = m.compare(original, actual, trace(), w1())
        self.assertTrue(result["same_export_light_value_parity"])
        self.assertEqual(result["matched_exported_light_values"], 1)
        self.assertFalse(result["original_light_visual_equivalence_proven"])

    def test_light_trace_can_skip_other_original_scenes(self):
        t = trace()
        t["objects"].append(trace(45, 108001, scene="level6")["objects"][0])
        result = m.compare({("level0", 123): source_light()},
                           {(GUID, 108000): source_light()}, t, w1())
        self.assertEqual(result["other_scene_lights_out_of_scope"], 1)

    def test_color_drift_reported_without_repair(self):
        result = m.compare({("level0", 123): source_light()},
                           {(GUID, 108000): source_light(color=(1, 1, 1, 1))},
                           trace(), w1())
        self.assertEqual(result["value_mismatches"]["changed_color_rgba"], 1)
        self.assertFalse(result["same_export_light_value_parity"])
        self.assertEqual(result["assets_changed"], 0)

    def test_enabled_intensity_type_and_range_drift_independent(self):
        result = m.compare({("level0", 123): source_light()},
                           {(GUID, 108000): (0, 1, source_light()[2], 2.0, 50.0)},
                           trace(), w1())
        self.assertEqual(len(result["value_mismatches"]), 4)

    def test_missing_same_instance_w1_rejected(self):
        with self.assertRaisesRegex(m.ParityError, "not_same_export_instance"):
            m.compare({("level0", 123): source_light()},
                      {(GUID, 108000): source_light()}, trace(),
                      {"schema_version": 1, "export_instance": "c" * 32, "objects": []})

    def test_untraced_original_light_rejected(self):
        with self.assertRaisesRegex(m.ParityError, "original_lights_absent"):
            m.compare({("level0", 123): source_light(), ("level1", 5): source_light()},
                      {(GUID, 108000): source_light()}, trace(), w1())

    def test_export_without_actual_light_rejected(self):
        with self.assertRaisesRegex(m.ParityError, "not_found_in_actual"):
            m.compare({("level0", 123): source_light()}, {}, trace(), w1())

    def test_two_original_lights_collapsing_to_one_export_pointer_rejected(self):
        t = trace()
        t["objects"].append(trace(source_id=456, target=108000, scene="level1")["objects"][0])
        with self.assertRaisesRegex(m.ParityError, "collapsed"):
            m.compare({("level0", 123): source_light(), ("level1", 456): source_light()},
                      {(GUID, 108000): source_light()}, t, w1())

    def test_trace_scene_names_are_not_guessed_from_source_paths(self):
        self.assertIsNone(m.trace_key({"owner": "wrong/path/level0", "path_id": 123}))
        self.assertEqual(m.trace_key({"owner": "level0", "path_id": 123}), ("level0", 123))

    def test_invalid_traced_guids_rejected(self):
        with self.assertRaisesRegex(m.ParityError, "unsupported_export_light_pointer"):
            m.trace_pointer({"file_id": 3, "guid": "wrong", "type": 2})

    def test_export_zero_guid_rejected_not_guessed(self):
        with self.assertRaisesRegex(m.ParityError, "export_scene_guid_unavailable"):
            m.trace_pointer({"file_id": 3, "guid": "0" * 32, "type": 2})

    def test_malformed_source_color_refused(self):
        tree = {"m_Enabled": 1, "m_Type": 2,
                "m_GameObject": {"m_FileID": 0, "m_PathID": 3},
                "m_Color": {"r": 1}, "m_Intensity": 2, "m_Range": 5}
        with self.assertRaisesRegex(m.ParityError, "invalid_original_light_color"):
            m.fields_from_tree(tree)

    def test_bad_yaml_color_and_nonfinite_rejected(self):
        with self.assertRaisesRegex(m.ParityError, "duplicate_exported_light_color"):
            m.yaml_rgba("{r: 1, r: 2, b: 3, a: 1}")
        with self.assertRaisesRegex(m.ParityError, "invalid_numeric_yaml"):
            m.yaml_rgba("{r: NaN, g: 1, b: 1, a: 1}")

    def test_actual_exported_scene_with_light_and_real_owner(self):
        with TemporaryDirectory() as tmp:
            project = Path(tmp)
            assets = project / "Assets"
            assets.mkdir()
            file = assets / "scene.unity"
            file.write_text(
                "%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n"
                "--- !u!1 &8\nGameObject:\n  m_Name: ProvenanceFixture\n"
                "--- !u!108 &108000\nLight:\n"
                "  m_GameObject: {fileID: 8}\n"
                "  m_Enabled: 1\n  m_Type: 2\n"
                "  m_Color: {r: 0.6, g: 0.4, b: 0.8, a: 1}\n"
                "  m_Intensity: 0.75\n  m_Range: 12.5\n", encoding="utf8")
            Path(str(file) + ".meta").write_text("fileFormatVersion: 2\nguid: " + GUID + "\n")
            lights = m.exported_lights(project)
            self.assertEqual(lights[(GUID, 108000)], source_light())

    def test_missing_export_owner_refused(self):
        with self.assertRaisesRegex(m.ParityError, "owner_object_missing"):
            m.exported_light_body(
                "Light:\n  m_GameObject: {fileID: 66}\n"
                "  m_Enabled: 1\n  m_Type: 2\n"
                "  m_Color: {r: 0.6, g: 0.4, b: 0.8, a: 1}\n"
                "  m_Intensity: 0.75\n  m_Range: 12.5\n", set())

    def test_duplicate_export_light_fields_refused(self):
        body = ("Light:\n  m_GameObject: {fileID: 8}\n"
                "  m_Enabled: 1\n  m_Enabled: 0\n  m_Type: 2\n"
                "  m_Color: {r: 0.6, g: 0.4, b: 0.8, a: 1}\n"
                "  m_Intensity: 0.75\n  m_Range: 12.5\n")
        with self.assertRaisesRegex(m.ParityError, "duplicate_exported_light_field"):
            m.exported_light_body(body, {8})

    def test_export_symlink_entry_refused(self):
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            assets = base / "Assets"
            assets.mkdir()
            (assets / "linked").symlink_to(base, target_is_directory=True)
            with self.assertRaisesRegex(m.ParityError, "symlink_inside_export"):
                m.exported_lights(base)


if __name__ == "__main__":
    unittest.main()
