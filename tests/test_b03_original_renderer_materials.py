import hashlib
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from scripts.b03_original_renderer_materials import (
    SourceError, analyze_scene, pointer_shape, probe,
)


def item(path_id, name, tree=None, broken=False):
    def read_typetree(check_read=False):
        if broken:
            raise RuntimeError("unreadable")
        return tree
    return SimpleNamespace(
        path_id=path_id, type=SimpleNamespace(name=name),
        read_typetree=read_typetree,
    )


class OriginalRendererMaterialTests(unittest.TestCase):
    def test_real_local_material_pointer_positive(self):
        scene = [item(1, "Material"), item(2, "MeshRenderer",
                       {"m_Materials": [{"m_FileID": 0, "m_PathID": 1}]})]
        result = analyze_scene(scene, 0)
        self.assertEqual(result["counts"]["local_material_target_verified"], 1)
        self.assertTrue(result["original_material_array_decoded_for_all_renderers"])
        self.assertEqual(len(result["original_renderer_material_edges_sha256"]), 64)

    def test_declared_external_not_falsely_resolved(self):
        scene = [item(1, "MeshRenderer",
                      {"m_Materials": [{"m_FileID": 1, "m_PathID": 115}]})]
        result = analyze_scene(scene, 2)
        self.assertEqual(result["counts"]["external_target_unverified"], 1)
        self.assertFalse(result["external_material_target_object_verified"])

    def test_null_pointer_classification(self):
        kind, fid, pid = pointer_shape({"m_FileID": 0, "m_PathID": 0}, {}, 0)
        self.assertEqual((kind, fid, pid), ("null_material_slot", 0, 0))

    def test_wrong_local_type_rejected(self):
        with self.assertRaisesRegex(SourceError, "wrong_local_material"):
            pointer_shape({"m_FileID": 0, "m_PathID": 3}, {3: "Shader"}, 0)

    def test_missing_local_material_target_rejected(self):
        with self.assertRaisesRegex(SourceError, "missing_local_material"):
            pointer_shape({"m_FileID": 0, "m_PathID": 3}, {}, 0)

    def test_external_index_out_of_range_rejected(self):
        with self.assertRaisesRegex(SourceError, "out_of_bounds"):
            pointer_shape({"m_FileID": 2, "m_PathID": 3}, {}, 1)

    def test_pathid_zero_with_nonzero_fileid_rejected(self):
        with self.assertRaises(SourceError):
            pointer_shape({"m_FileID": 1, "m_PathID": 0}, {}, 1)

    def test_bad_pointer_schema_rejected(self):
        for value in (None, [], {"m_FileID": 0}, {"m_FileID": 0, "m_PathID": 1, "m_Name": "alias"}):
            with self.subTest(value=value), self.assertRaises(SourceError):
                pointer_shape(value, {}, 0)

    def test_boolean_and_negative_ids_rejected(self):
        for value in (True, -1, 1.5):
            with self.subTest(value=value), self.assertRaises(SourceError):
                pointer_shape({"m_FileID": value, "m_PathID": 2}, {}, 2)

    def test_duplicate_and_null_object_id_rejected(self):
        for scene in ([item(1, "Material"), item(1, "MeshRenderer")],
                      [item(0, "MeshRenderer", {"m_Materials": []})]):
            with self.assertRaises(SourceError):
                analyze_scene(scene, 0)

    def test_non_renderer_decoy_materials_ignored(self):
        scene = [item(1, "MonoBehaviour", {"m_Materials": ["garbage"]}),
                 item(2, "MeshRenderer", {"m_Materials": []})]
        r = analyze_scene(scene, 0)
        self.assertEqual(r["counts"]["original_renderer_objects"], 1)
        self.assertNotIn("original_material_slots", r["counts"])

    def test_invalid_material_array_remains_unknown(self):
        scene = [item(1, "MeshRenderer", {"m_Materials": "not-an-array"})]
        r = analyze_scene(scene, 0)
        self.assertEqual(r["counts"]["renderer_material_array_schema_unknown"], 1)
        self.assertFalse(r["original_material_array_decoded_for_all_renderers"])

    def test_unreadable_renderer_not_miscounted_healthy(self):
        scene = [item(1, "SkinnedMeshRenderer", broken=True)]
        r = analyze_scene(scene, 0)
        self.assertEqual(r["counts"]["renderer_typetree_undecodable"], 1)
        self.assertFalse(r["original_material_array_decoded_for_all_renderers"])

    def test_edges_sha_is_stable_across_reader_order(self):
        scene = [item(10, "MeshRenderer", {"m_Materials": [{"m_FileID": 1, "m_PathID": 34}]}),
                 item(11, "SkinnedMeshRenderer", {"m_Materials": [{"m_FileID": 0, "m_PathID": 0}]})]
        a = analyze_scene(scene, 1)
        b = analyze_scene(list(reversed(scene)), 1)
        self.assertEqual(a["original_renderer_material_edges_sha256"], b["original_renderer_material_edges_sha256"])

    def test_no_original_source_deletion_or_game_output(self):
        scene = [item(2, "MeshRenderer", {"m_Materials": [{"m_FileID": 0, "m_PathID": 1}]}),
                 item(1, "Material")]
        r = analyze_scene(scene, 0)
        self.assertNotIn("1\t0\t", str(r))
        self.assertFalse(r["same_export_renderer_material_lineage_verified"])
        self.assertFalse(r["shader_program_or_device_pixels_verified"])

    def test_symlinked_source_root_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            real = root / "source"
            real.mkdir()
            linked = root / "symlink"
            linked.symlink_to(real, target_is_directory=True)
            with self.assertRaises(SourceError):
                probe(linked, loader=lambda _: None)

    def test_invalid_externals_count_rejected(self):
        for bad in (True, -1, 65536, "2"):
            with self.subTest(bad=bad), self.assertRaises(SourceError):
                analyze_scene([item(2, "MeshRenderer", {"m_Materials": []})], bad)

    def test_material_slot_budget_protected(self):
        scene = [item(2, "MeshRenderer", {"m_Materials": [{}] * 257})]
        with self.assertRaisesRegex(SourceError, "slot_count_over_budget"):
            analyze_scene(scene, 0)


if __name__ == "__main__":
    unittest.main()
