"""Synthetic-only serialized UI data tests; no original game scene copied."""
import math
import tempfile
from pathlib import Path
import unittest

from scripts.probe_a2_scene_ui_layout import (
    SCENE_BLOBS, audit, git_blob_sha, local_pptr, scan_objects,
    verified_scene, vector2,
)


class FakeObject:
    def __init__(self, kind, path_id, tree=None, fail=False):
        self.type = type("FakeType", (), {"name": kind})()
        self.path_id = path_id
        self.tree = tree
        self.fail = fail

    def read_typetree(self, **kwargs):
        if self.fail:
            raise ValueError("Unknown source type tree")
        return self.tree


class FakeEnvironment:
    def __init__(self, objects):
        self.file = type("FakeFile", (), {"objects": {
            idx: obj for idx, obj in enumerate(objects)
        }})()


class A2SceneUiLayoutTests(unittest.TestCase):
    def test_local_pointer_requires_local_positive_id(self):
        self.assertEqual(local_pptr({"m_FileID": 0, "m_PathID": 98}), 98)
        self.assertIsNone(local_pptr({"m_FileID": 1, "m_PathID": 98}))
        self.assertIsNone(local_pptr({"m_FileID": 0, "m_PathID": -2}))
        self.assertIsNone(local_pptr({"m_FileID": True, "m_PathID": 3}))
        self.assertIsNone(local_pptr(None))

    def test_vector_shape_fail_closed(self):
        self.assertEqual(vector2({"x": 1, "y": -0.5}), (1., -.5))
        self.assertIsNone(vector2({"x": float("nan"), "y": 1}))
        self.assertIsNone(vector2({"x": math.inf, "y": 1}))
        self.assertIsNone(vector2({"x": True, "y": 1}))
        self.assertIsNone(vector2({"x": 1}))

    def test_settings_named_owner_not_proof_of_page_regression(self):
        objects = [
            FakeObject("GameObject", 9, {"m_Name": "SettingsPage"}),
            FakeObject("GameObject", 10, {"m_Name": "Unrelated"}),
            FakeObject("RectTransform", 11, {"m_GameObject": {"m_FileID": 0, "m_PathID": 9},
                "m_AnchorMin": {"x": 0, "y": 0},
                "m_AnchorMax": {"x": 1, "y": 1},
                "m_SizeDelta": {"x": 80, "y": 0}}),
            FakeObject("RectTransform", 12, {"m_GameObject": {"m_FileID": 1, "m_PathID": 9},
                "m_AnchorMin": {"x": 0.5, "y": 0.5},
                "m_AnchorMax": {"x": 0.5, "y": 0.5},
                "m_SizeDelta": {"x": 0, "y": 0}}),
        ]
        scan = scan_objects(objects)
        self.assertEqual(scan["counts"]["settings_name_gameobjects"], 1)
        self.assertEqual(scan["counts"]["rect_linked_to_settings_named_go"], 1)
        self.assertEqual(scan["counts"]["rect_stretch_anchor_geometry"], 1)
        self.assertEqual(scan["counts"]["rect_fixed_anchor_geometry"], 1)
        self.assertFalse(scan["settings_stretch_cause_proven"])
        self.assertNotIn("SettingsPage", str(scan))

    def test_mono_field_shape_is_candidate_not_confirmed_script(self):
        full = {"m_UiScaleMode": 1, "m_ReferenceResolution": {"x": 1920, "y": 1080},
                "m_ScreenMatchMode": 0, "m_MatchWidthOrHeight": 0.5}
        result = scan_objects([FakeObject("MonoBehaviour", 1, full),
                               FakeObject("MonoBehaviour", 2, {"m_ReferenceResolution": 1}),
                               FakeObject("MonoBehaviour", 3, fail=True)])
        self.assertEqual(result["counts"]["canvas_scaler_serialized_field_shape_candidates"], 1)
        self.assertEqual(result["decode_unknowns"]["MonoBehaviour_typetree_unknown"], 1)
        self.assertFalse(result["canvas_scaler_script_identity_confirmed"])
        self.assertTrue(result["nondecoded_mono_does_not_prove_absence"])

    def test_missing_typed_geometry_does_not_fake_fixed_anchor(self):
        result = scan_objects([FakeObject("RectTransform", 1, {"m_SizeDelta": {"x": 4, "y": 5}})])
        self.assertEqual(result["counts"]["rect_geometry_unknown"], 1)
        self.assertNotIn("rect_fixed_anchor_geometry", result["counts"])

    def test_reject_bad_blobs_and_lfs_pointer(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / "level0"
            p.write_bytes(b"hello" * 40)
            self.assertEqual(verified_scene(p, git_blob_sha(p.read_bytes()))["source_bytes"], 200)
            with self.assertRaisesRegex(ValueError, "fingerprint"):
                verified_scene(p, "0" * 40)
            p.write_bytes(b"version https://git-lfs.github.com/spec/v1\n" + b"x" * 160)
            with self.assertRaisesRegex(ValueError, "LFS pointer"):
                verified_scene(p, git_blob_sha(p.read_bytes()))
            p.unlink()
            p.symlink_to("/etc/passwd")
            with self.assertRaisesRegex(ValueError, "Unsafe"):
                verified_scene(p, "0" * 40)

    def test_six_original_pins_and_no_source_mutations(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = b"synthetic blob contents only" * 5
            for name in SCENE_BLOBS:
                (root / name).write_bytes(raw)
            expected = {name: git_blob_sha(raw) for name in SCENE_BLOBS}
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            loader = lambda _p: FakeEnvironment([FakeObject("Canvas", 3, {})])
            result = audit(root, expected=expected, loader=loader)
            self.assertEqual(result["selected_scene_count"], 6)
            self.assertTrue(result["original_git_blobs_verified"])
            self.assertFalse(result["unity_or_android_executed"])
            self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})
            with self.assertRaisesRegex(ValueError, "fingerprint"):
                audit(root, loader=loader)

    def test_scan_rejects_unbounded_object_inventory(self):
        from scripts.probe_a2_scene_ui_layout import MAX_OWNER_OBJECTS
        with self.assertRaisesRegex(ValueError, "Unbounded"):
            scan_objects([FakeObject("Canvas", i, {}) for i in range(MAX_OWNER_OBJECTS + 1)])


if __name__ == "__main__":
    unittest.main()
