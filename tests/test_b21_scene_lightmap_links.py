"""B21 deterministic, source-free negative controls for original lightmap probe."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace

from scripts.b21_scene_lightmap_links import (
    MAX_OBJECTS, SourceError, analyze_scene, pointer_state, verify_source,
)


class Obj:
    def __init__(self, kind, pid, tree=None, broken=False):
        self.type = SimpleNamespace(name=kind)
        self.path_id = pid
        self.tree = tree
        self.broken = broken

    def read_typetree(self, check_read=False):
        if self.broken:
            raise ValueError("undecodable")
        return self.tree


def tex(file_id=0, path_id=99):
    return {"m_FileID": file_id, "m_PathID": path_id}


class B21OriginalLightmapTests(unittest.TestCase):
    def test_valid_color_and_renderer_links(self):
        rows = [
            Obj("LightmapSettings", 1, {
                "m_Lightmaps": [{"m_LightmapColor": tex(),
                                "m_LightmapDir": tex(0, 0),
                                "m_ShadowMask": tex(2, 42)}]}),
            Obj("Texture2D", 99),
            Obj("MeshRenderer", 2, {"m_LightmapIndex": 0}),
        ]
        result = analyze_scene(rows)
        counts = result["counts"]
        self.assertEqual(counts["renderer_indices_in_range"], 1)
        self.assertEqual(counts["m_LightmapColor_local_target_present"], 1)
        self.assertEqual(counts["m_ShadowMask_external_target_unverified"], 1)
        self.assertEqual(counts["m_LightmapDir_null_pointer"], 1)
        self.assertFalse(result["pixel_shading_or_missing_lightmap_cause_proven"])

    def test_missing_local_texture_tracked_not_claimed_fixed(self):
        rows = [Obj("LightmapSettings", 1, {"m_Lightmaps": [
            {"m_LightmapColor": tex(0, 90)}]})]
        result = analyze_scene(rows)
        self.assertEqual(result["counts"]["m_LightmapColor_local_target_missing"], 1)
        self.assertFalse(result["source_export_pptr_mapping_proven"])

    def test_external_file_id_never_called_missing(self):
        self.assertEqual(pointer_state(tex(1, 90), set()), "external_target_unverified")

    def test_empty_settings_is_not_a_loss_claim(self):
        result = analyze_scene([Obj("MeshRenderer", 2, {"m_LightmapIndex": 0})])
        self.assertEqual(result["counts"]["renderer_indices_without_decodable_settings"], 1)
        self.assertEqual(result["counts"]["lightmap_settings_absent_or_undecodable"], 1)

    def test_unassigned_indices_do_not_report_broken_link(self):
        result = analyze_scene([Obj("LightmapSettings", 1, {"m_Lightmaps": []}),
                                Obj("MeshRenderer", 2, {"m_LightmapIndex": 65535}),
                                Obj("Terrain", 3, {"m_LightmapIndex": -1})])
        self.assertEqual(result["counts"]["renderer_lightmap_unassigned"], 2)
        self.assertNotIn("renderer_indices_out_of_range", result["counts"])

    def test_renderer_out_of_range_is_observed_not_repaired(self):
        result = analyze_scene([Obj("LightmapSettings", 1, {"m_Lightmaps": [{}]}),
                                Obj("MeshRenderer", 2, {"m_LightmapIndex": 3})])
        self.assertEqual(result["counts"]["renderer_indices_out_of_range"], 1)
        self.assertFalse(result["original_assets_modified"])

    def test_malformed_lightmap_pointer_is_unknown(self):
        self.assertEqual(pointer_state({"fileID": 0, "pathID": 77}, set()),
                         "unknown_pointer_schema")
        self.assertEqual(pointer_state({"m_FileID": 0, "m_PathID": -99}, set()),
                         "unknown_pointer_schema")

    def test_null_pointer_is_not_missing_local_target(self):
        self.assertEqual(pointer_state(tex(0, 0), set()), "null_pointer")

    def test_missing_typetree_is_unknown_not_absence(self):
        result = analyze_scene([Obj("LightmapSettings", 1, broken=True),
                                Obj("MeshRenderer", 2, broken=True)])
        self.assertEqual(result["counts"]["LightmapSettings_typetree_unknown"], 1)
        self.assertEqual(result["counts"]["MeshRenderer_typetree_unknown"], 1)

    def test_duplicate_path_ids_refused(self):
        with self.assertRaisesRegex(SourceError, "duplicate_object_path_id"):
            analyze_scene([Obj("MeshRenderer", 1, {}), Obj("Texture2D", 1)])

    def test_invalid_path_ids_refused(self):
        with self.assertRaisesRegex(SourceError, "invalid_object_path_id"):
            analyze_scene([Obj("MeshRenderer", 0, {})])

    def test_double_lightmap_settings_refused(self):
        with self.assertRaisesRegex(SourceError, "multiple_lightmap_settings"):
            analyze_scene([Obj("LightmapSettings", 1, {"m_Lightmaps": []}),
                           Obj("LightmapSettings", 2, {"m_Lightmaps": []})])

    def test_unknown_lightmap_array_shape_preserved(self):
        result = analyze_scene([Obj("LightmapSettings", 1, {"m_Lightmaps": None})])
        self.assertEqual(result["counts"]["lightmaps_schema_unknown"], 1)

    def test_unbounded_objects_refused(self):
        with self.assertRaisesRegex(SourceError, "over_budget"):
            analyze_scene([None] * (MAX_OBJECTS + 1))

    def test_original_size_sha_and_tamper(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "level"
            raw = b"original test blob" * 20
            p.write_bytes(raw)
            digest = hashlib.sha256(raw).hexdigest()
            verify_source(p, (len(raw), digest))
            with self.assertRaisesRegex(SourceError, "sha256"):
                verify_source(p, (len(raw), "0" * 64))
            with self.assertRaisesRegex(SourceError, "size"):
                verify_source(p, (len(raw) + 1, digest))

    def test_source_symlink_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            valid = root / "valid"
            valid.write_bytes(b"a" * 150)
            link = root / "link"
            link.symlink_to(valid)
            with self.assertRaisesRegex(SourceError, "linked_original"):
                verify_source(link, (150, hashlib.sha256(b"a" * 150).hexdigest()))


if __name__ == "__main__":
    unittest.main()
