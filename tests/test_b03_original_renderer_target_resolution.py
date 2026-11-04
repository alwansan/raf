import hashlib
from collections import Counter
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from scripts.b03_original_renderer_target_resolution import (
    SourceError, resolve_scene_targets, select_original_objects, verify_owner,
)


def obj(pid, kind, slots=None):
    return SimpleNamespace(path_id=pid, type=SimpleNamespace(name=kind),
                           read_typetree=lambda check_read=False:
                           {"m_Materials": slots if slots is not None else []})


class TargetResolverTests(unittest.TestCase):
    def setUp(self):
        self.owners = {"resources.assets": {42: "Material", 50: "Mesh"}}
        self.manifest = Counter({"resources.assets": 1})

    def test_exact_original_material_in_verified_provider(self):
        objects = [obj(1, "MeshRenderer", [{"m_FileID": 1, "m_PathID": 42}])]
        r = resolve_scene_targets(objects, ["a/resources.assets"], self.owners, self.manifest)
        self.assertEqual(r["counts"]["external_staged_material_target_verified"], 1)
        self.assertTrue(r["staged_material_object_links_valid"])

    def test_missing_target_detected(self):
        objects = [obj(1, "MeshRenderer", [{"m_FileID": 1, "m_PathID": 999}])]
        r = resolve_scene_targets(objects, ["resources.assets"], self.owners, self.manifest)
        self.assertEqual(r["errors"]["external_staged_provider_missing_object"], 1)
        self.assertFalse(r["staged_material_object_links_valid"])

    def test_wrong_target_type_detected(self):
        objects = [obj(1, "MeshRenderer", [{"m_FileID": 1, "m_PathID": 50}])]
        r = resolve_scene_targets(objects, ["resources.assets"], self.owners, self.manifest)
        self.assertEqual(r["errors"]["external_staged_provider_wrong_object_type"], 1)

    def test_unselected_owner_classified_unknown_not_fake_success(self):
        objects = [obj(1, "MeshRenderer", [{"m_FileID": 1, "m_PathID": 50}])]
        r = resolve_scene_targets(objects, ["different.assets"], self.owners,
                                  Counter({"different.assets": 1}))
        self.assertEqual(r["counts"]["external_other_zip2_provider_unverified"], 1)
        self.assertFalse(r["original_external_other_owners_verified"])

    def test_nonmanifest_name_rejected(self):
        objects = [obj(1, "MeshRenderer", [{"m_FileID": 1, "m_PathID": 50}])]
        r = resolve_scene_targets(objects, ["unknown.assets"], self.owners, self.manifest)
        self.assertEqual(r["errors"]["external_owner_name_not_uniquely_verified"], 1)

    def test_local_and_null_targets_are_preserved(self):
        objects = [obj(10, "Material"), obj(1, "SkinnedMeshRenderer", [
            {"m_FileID": 0, "m_PathID": 10},
            {"m_FileID": 0, "m_PathID": 0},
        ])]
        r = resolve_scene_targets(objects, [], self.owners, self.manifest)
        self.assertEqual(r["counts"]["original_null_slots"], 1)
        self.assertEqual(r["counts"]["local_material_object_class_verified"], 1)

    def test_duplicate_and_invalid_owner_ids_rejected(self):
        with self.assertRaises(SourceError):
            select_original_objects([obj(5, "Material"), obj(5, "Material")])
        with self.assertRaises(SourceError):
            select_original_objects([obj(-3, "Material")])

    def test_stage_source_hash_authentication(self):
        with tempfile.TemporaryDirectory() as root:
            file = Path(root) / "owner"
            raw = b"real original byte check fixture"
            file.write_bytes(raw)
            pin = len(raw), hashlib.sha256(raw).hexdigest()
            verify_owner(file, pin)
            file.write_bytes(b"REAL original byte check fixture")
            with self.assertRaises(SourceError):
                verify_owner(file, pin)

    def test_owner_link_is_denied(self):
        with tempfile.TemporaryDirectory() as root:
            a = Path(root) / "real"
            b = Path(root) / "symlink"
            a.write_bytes(b"x")
            b.symlink_to(a)
            with self.assertRaises(SourceError):
                verify_owner(b, (1, hashlib.sha256(b"x").hexdigest()))

    def test_unknown_external_type_cannot_claim_device(self):
        o = [obj(1, "MeshRenderer", [{"m_FileID": 1, "m_PathID": 42}])]
        r = resolve_scene_targets(o, ["resources.assets"], self.owners, self.manifest)
        self.assertFalse(r["android_rendering_proven"])
        self.assertFalse(r["same_instance_export_renderer_identity_verified"])


if __name__ == "__main__":
    unittest.main()
