"""Source-free B21 vs typed-local admission regressions."""
import unittest
from types import SimpleNamespace
from scripts.b21_scene_lightmap_links import analyze_scene, SourceError
from tools.gt_lightmap_local_binding.audit import analyze

def obj(name, cid, pid, tree=None, broken=False):
    def read_typetree(check_read=False):
        if broken:
            raise ValueError("unreadable authored typetree")
        return tree
    return SimpleNamespace(type=SimpleNamespace(name=name, value=cid), path_id=pid,
                           read_typetree=read_typetree)

def ptr(pid=99, fid=0):
    return {"m_FileID": fid, "m_PathID": pid}

def scene(color=None, direction=None, shadow=None, index=0, target_name="Texture2D", target_class=28):
    return [obj("LightmapSettings", 157, 1, {"m_Lightmaps": [{
        "m_LightmapColor": ptr() if color is None else color,
        "m_LightmapDir": ptr(0) if direction is None else direction,
        "m_ShadowMask": ptr(0) if shadow is None else shadow}]}),
        obj("MeshRenderer", 23, 2, {"m_LightmapIndex": index}),
        obj(target_name, target_class, 99)]

class TypedLightmapTests(unittest.TestCase):
    def reject(self, rows, key):
        r = analyze(rows)
        self.assertFalse(r["all_assigned_renderers_local_texture_links_complete"])
        self.assertEqual(r["counts"][key], 1)

    def test_positive_typed_and_optional_null(self):
        r = analyze(scene())
        self.assertTrue(r["all_assigned_renderers_local_texture_links_complete"])
        self.assertEqual(r["counts"]["renderer_local_texture_links_complete"], 1)
        self.assertFalse(r["source_export_pptr_mapping_proven"])
        self.assertFalse(r["lighting_pixels_or_device_proven"])

    def test_old_presence_is_not_typed_identity(self):
        rows = scene(target_name="Mesh", target_class=43)
        self.assertEqual(analyze_scene(rows)["counts"]["m_LightmapColor_local_target_present"], 1)
        self.reject(rows, "m_LightmapColor_local_target_wrong_class")

    def test_disagreeing_name_class(self):
        for name, cid in (("Texture2D", 43), ("Mesh", 28), ("Texture2D", None)):
            with self.subTest(name=name, cid=cid):
                self.reject(scene(target_name=name, target_class=cid), "m_LightmapColor_local_target_type_unverified")

    def test_old_in_range_does_not_establish_color(self):
        for value, key in ((ptr(88), "local_target_missing"), (ptr(0), "null_pointer"),
                           (ptr(99, 1), "external_target_unverified"), ({"m_FileID": False, "m_PathID": 99}, "unknown_pointer_schema")):
            with self.subTest(value=value):
                rows = scene(color=value)
                self.assertEqual(analyze_scene(rows)["counts"]["renderer_indices_in_range"], 1)
                self.reject(rows, "renderer_color_" + key)

    def test_optional_external_or_wrong_class_not_admitted(self):
        self.reject(scene(direction=ptr(99, 1)), "m_LightmapDir_external_target_unverified")
        rows = scene(shadow=ptr(98)) + [obj("Mesh", 43, 98)]
        self.reject(rows, "m_ShadowMask_local_target_wrong_class")

    def test_optional_missing_schema_is_not_null(self):
        rows = scene()
        del rows[0].read_typetree()["m_Lightmaps"][0]["m_ShadowMask"]
        self.reject(rows, "m_ShadowMask_unknown_pointer_schema")

    def test_ambiguous_physical_settings_old_accepts(self):
        rows = scene() + [obj("LightmapSettings", 157, 4, broken=True)]
        self.assertEqual(analyze_scene(rows)["counts"]["renderer_indices_in_range"], 1)
        self.reject(rows, "renderer_settings_unresolved")

    def test_reserved_index_never_regular_offset(self):
        rows = scene(index=65534)
        self.assertEqual(analyze_scene(rows)["counts"]["renderer_indices_out_of_range"], 1)
        self.reject(rows, "renderer_index_reserved_unverified")

    def test_absent_or_out_of_range(self):
        self.reject(scene()[1:], "renderer_settings_unresolved")
        self.reject(scene(index=1), "renderer_index_out_of_range")

    def test_unknown_renderer_index_prevents_positive(self):
        rows = scene() + [obj("MeshRenderer", 23, 3, {"m_LightmapIndex": True})]
        self.reject(rows, "renderer_index_unknown")

    def test_no_assigned_renderer_not_vacuous_success(self):
        for index in (-1, 65535):
            self.reject(scene(index=index), "renderer_unassigned")

    def test_duplicate_and_bad_ids_fail_closed(self):
        for rows in (scene() + [obj("Mesh", 43, 99)], scene() + [obj("Mesh", 43, 0)]):
            with self.assertRaises(SourceError):
                analyze(rows)

    def test_scene_scoped_same_pathid_different_class(self):
        self.assertTrue(analyze(scene())["all_assigned_renderers_local_texture_links_complete"])
        self.reject(scene(target_name="Mesh", target_class=43), "m_LightmapColor_local_target_wrong_class")

if __name__ == "__main__":
    unittest.main()
