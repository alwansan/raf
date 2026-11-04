"""Small original-input acceptance probe: synthetic negative safety controls."""
from pathlib import Path
import tempfile
import unittest

from scripts.b05_probe_original_texenv_shapes import (
    OWNER, classify_original, inspect,
)


def slot(name="_MainTex", file_id=0, path_id=9, scale=(1., 1.), offset=(0., 0.)):
    return (name, {
        "m_Texture": {"m_FileID": file_id, "m_PathID": path_id},
        "m_Scale": {"x": scale[0], "y": scale[1]},
        "m_Offset": {"x": offset[0], "y": offset[1]},
    })


class OriginalTexEnvTests(unittest.TestCase):
    def test_real_shaped_synthetic_materials_aggregate_only(self):
        items = [
            {"m_TexEnvs": [slot(), slot("_Null", path_id=0),
                          slot("_External", file_id=2, path_id=55)]},
            {"m_TexEnvs": []},
        ]
        r = classify_original(items)
        self.assertEqual((r["materials"], r["texenv_slots"]), (2, 3))
        self.assertEqual((r["bound_same_owner"], r["bound_external_owner"], r["null_slots"]), (1, 1, 1))
        self.assertEqual(r["uv_complete"], 3)
        self.assertEqual(r["materials_without_slots"], 1)
        self.assertFalse(r["source_export_texenv_fidelity_verified"])
        self.assertFalse(r["unity_android_pixels_verified"])
        self.assertNotIn("_MainTex", str(r))
        self.assertNotIn("_External", str(r))
        self.assertNotIn("path_id", str(r).lower())

    def test_original_uv_unavailable_never_marked_complete(self):
        src = slot()
        del src[1]["m_Scale"]
        del src[1]["m_Offset"]
        r = classify_original([{"m_TexEnvs": [src]}])
        self.assertEqual((r["uv_missing"], r["uv_complete"]), (1, 0))

    def test_missing_materials_or_missing_texenv_fails(self):
        with self.assertRaisesRegex(ValueError, "No authentic original"):
            classify_original([])
        with self.assertRaisesRegex(ValueError, "TexEnvs"):
            classify_original([{"m_Colors": []}])

    def test_duplicate_slot_or_invalid_external_pointers_fail(self):
        with self.assertRaisesRegex(ValueError, "duplicate"):
            classify_original([{"m_TexEnvs": [slot(), slot()]}])
        with self.assertRaisesRegex(ValueError, "no target"):
            classify_original([{"m_TexEnvs": [slot(file_id=2, path_id=0)]}])

    def test_uv_partial_and_nonfinite_fail(self):
        src = slot()
        del src[1]["m_Offset"]
        with self.assertRaisesRegex(ValueError, "Incomplete"):
            classify_original([{"m_TexEnvs": [src]}])
        with self.assertRaisesRegex(ValueError, "Nonfinite"):
            classify_original([{"m_TexEnvs": [slot(scale=(float("nan"), 1.))]}])

    def test_unverified_original_bytes_fail_before_unitypy(self):
        with tempfile.TemporaryDirectory() as t:
            parent = Path(t)
            (parent / "Raft_Data").mkdir()
            (parent / "Raft_Data" / OWNER).write_bytes(b"wrong")
            with self.assertRaisesRegex(ValueError, "SHA256"):
                inspect(parent)

    def test_symlink_owner_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            parent = Path(t)
            (parent / "Raft_Data").mkdir()
            (parent / "Raft_Data" / OWNER).symlink_to(parent / "fake")
            with self.assertRaisesRegex(ValueError, "linked"):
                inspect(parent)


if __name__ == "__main__":
    unittest.main()
