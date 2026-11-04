"""B21 original Light source→export GameObject exact owner negative controls."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts import b21_compare_light_owners as m

GUID = "a" * 32
SOURCE_EDGES = {("level0", 13): ("level0", 8), ("level1", 21): ("level1", 19)}
EXPORTED_EDGES = {(GUID, 108000): (GUID, 8), (GUID, 108001): (GUID, 19)}
VALUES = {"same_export_light_value_parity": True, "private_same_instance_w1_trace_matched": True}


def tracer(kind, scene, original_id, exported):
    return {"class_id": kind,
            "source": {"owner": scene, "path_id": original_id},
            "export": {"file_id": exported, "guid": GUID, "type": 2}}


def private_trace():
    return {"schema_version": 1, "export_instance": "b" * 32, "objects": [
        tracer(108, "level0", 13, 108000), tracer(108, "level1", 21, 108001),
        tracer(1, "level0", 8, 8), tracer(1, "level1", 19, 19),
    ]}


class TestOwners(unittest.TestCase):
    def test_two_original_light_owner_links_verified(self):
        result = m.check_owners(SOURCE_EDGES, EXPORTED_EDGES, private_trace(), VALUES)
        self.assertEqual(result["gameobject1_source_export_lineages_matched"], 2)
        self.assertTrue(result["exact_same_export_light_gameobject_owner_parity"])
        self.assertFalse(result["shader_lighting_pixels_verified"])

    def test_misattached_light_detected_with_values_still_equal(self):
        changed = {**EXPORTED_EDGES, (GUID, 108000): (GUID, 19)}
        result = m.check_owners(SOURCE_EDGES, changed, private_trace(), VALUES)
        self.assertFalse(result["exact_same_export_light_gameobject_owner_parity"])
        self.assertEqual(result["actual_misattached_original_lights"], 1)

    def test_missing_actual_light_record_not_considered_parity(self):
        changed = {(GUID, 108000): (GUID, 8)}
        result = m.check_owners(SOURCE_EDGES, changed, private_trace(), VALUES)
        self.assertEqual(result["actual_unresolved_light_owner_relations"], 1)

    def test_missing_original_go_trace_rejected(self):
        t = private_trace()
        t["objects"].pop()
        with self.assertRaisesRegex(m.ParityError, "missing_original"):
            m.check_owners(SOURCE_EDGES, EXPORTED_EDGES, t, VALUES)

    def test_two_source_gos_collapsing_in_export_refused(self):
        t = private_trace()
        t["objects"][-1]["export"]["file_id"] = 8
        with self.assertRaisesRegex(m.ParityError, "collapsed"):
            m.check_owners(SOURCE_EDGES, EXPORTED_EDGES, t, VALUES)

    def test_duplicate_source_gameobject_identity_rejected(self):
        t = private_trace()
        t["objects"].append(t["objects"][-1])
        with self.assertRaisesRegex(m.ParityError, "duplicate_traced_source_gameobject"):
            m.check_owners(SOURCE_EDGES, EXPORTED_EDGES, t, VALUES)

    def test_unproven_light_values_refuse_owner_success(self):
        with self.assertRaisesRegex(m.ParityError, "unproven"):
            m.check_owners(SOURCE_EDGES, EXPORTED_EDGES, private_trace(), {})

    def test_unexpected_class_refused(self):
        t = private_trace()
        t["objects"].append(tracer(222, "level0", 55, 999))
        with self.assertRaisesRegex(m.ParityError, "unexpected_class"):
            m.check_owners(SOURCE_EDGES, EXPORTED_EDGES, t, VALUES)

    def test_other_scene_gameobjects_excluded_without_false_link(self):
        t = private_trace()
        t["objects"].append(tracer(1, "level29", 4000, 9000))
        result = m.check_owners(SOURCE_EDGES, EXPORTED_EDGES, t, VALUES)
        self.assertEqual(result["gameobject1_source_export_lineages_matched"], 2)

    def test_actual_exported_light_owner_is_from_same_yaml_container(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            assets = root / "Assets"
            assets.mkdir()
            scene = assets / "a.unity"
            scene.write_text(
                "%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n"
                "--- !u!1 &8\nGameObject:\n  m_Name: Fixture\n"
                "--- !u!108 &108000\nLight:\n  m_GameObject: {fileID: 8}\n"
                "  m_Enabled: 1\n", encoding="utf8")
            Path(str(scene) + ".meta").write_text("fileFormatVersion: 2\nguid: " + GUID + "\n")
            result = m.actual_owner_edges(root)
            self.assertEqual(result[(GUID, 108000)], (GUID, 8))

    def test_actual_exported_owner_missing_gameobject_rejected(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            assets = root / "Assets"
            assets.mkdir()
            scene = assets / "a.unity"
            scene.write_text("%YAML 1.1\n--- !u!108 &108000\nLight:\n  m_GameObject: {fileID: 8}\n")
            Path(str(scene) + ".meta").write_text("guid: " + GUID + "\n")
            with self.assertRaisesRegex(m.ParityError, "not_gameobject"):
                m.actual_owner_edges(root)

    def test_export_ancestor_symlink_refused(self):
        with TemporaryDirectory() as td:
            root = Path(td)
            assets = root / "Assets"
            assets.mkdir()
            (assets / "linked").symlink_to(assets, target_is_directory=True)
            with self.assertRaisesRegex(m.ParityError, "unsafe_exported_scene_link"):
                m.actual_owner_edges(root)


if __name__ == "__main__":
    unittest.main()
