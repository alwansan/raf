"""B21 synthetic integrity, evidence boundaries and negative controls."""
import hashlib
from pathlib import Path
import tempfile
import unittest
from types import SimpleNamespace

from scripts.b21_original_dynamic_lights import (
    SourceError, audit_lights, classification, color_classification,
    local_owner_status, run,
)
from scripts.b21_scene_lightmap_links import PIN


class Obj:
    def __init__(self, kind, pid, body=None, fail=False):
        self.type = SimpleNamespace(name=kind)
        self.path_id = pid
        self.body = body
        self.fail = fail

    def read_typetree(self, check_read=False):
        if self.fail:
            raise ValueError("typed decoder missing")
        return self.body


def source_light(color=None, owner=3, intensity=1.0):
    return {
        "m_GameObject": {"m_FileID": 0, "m_PathID": owner},
        "m_Enabled": 1,
        "m_Color": color or {"r": 0.5, "g": 0.25, "b": 0.75, "a": 1.0},
        "m_Intensity": intensity,
        "m_Range": 10.0,
        "m_Type": 2,
    }


class Tests(unittest.TestCase):
    def test_native_enabled_light_with_existing_owner(self):
        result = audit_lights([Obj("Light", 2, source_light()), Obj("GameObject", 3)])
        c = result["counts"]
        self.assertEqual(c["original_light_component_objects"], 1)
        self.assertEqual(c["original_light_local_owner_present"], 1)
        self.assertEqual(c["original_light_color_finite_other_rgb"], 1)
        self.assertEqual(c["original_light_intensity_positive"], 1)
        self.assertFalse(result["lighting_pixel_equivalence_proven"])
        self.assertFalse(result["source_light_values_emitted"])

    def test_missing_local_owner_not_called_verified(self):
        r = audit_lights([Obj("Light", 2, source_light())])
        self.assertEqual(r["counts"]["original_light_local_owner_missing"], 1)

    def test_external_owner_unverified_not_missing(self):
        self.assertEqual(local_owner_status({"m_FileID": 1, "m_PathID": 5}, set()),
                         "external_owner_not_verified")

    def test_unknown_pointer_schema_rejected_to_unknown(self):
        self.assertEqual(local_owner_status({"fileID": 0, "pathID": 5}, set()),
                         "owner_pointer_unknown")

    def test_black_color_is_not_white(self):
        c = {"r": 0, "g": 0, "b": 0, "a": 1}
        self.assertEqual(color_classification(c), "black_rgb")

    def test_white_color_classification(self):
        c = {"r": 1, "g": 1, "b": 1, "a": 1}
        self.assertEqual(color_classification(c), "unit_white_rgb")

    def test_nonfinite_channel_cannot_be_considered_white(self):
        c = {"r": float("nan"), "g": 1, "b": 1, "a": 1}
        self.assertEqual(color_classification(c), "nonfinite_color")

    def test_negative_channel_unknown(self):
        c = {"r": -1, "g": 0, "b": 1, "a": 1}
        self.assertEqual(color_classification(c), "negative_components_unverified")

    def test_missing_color_schema_unknown(self):
        self.assertEqual(color_classification({"r": 1}), "unknown_color_schema")

    def test_nonfinite_intensity_not_claimed_positive(self):
        self.assertEqual(classification(float("inf")), "unknown_or_nonfinite")

    def test_negative_intensity_not_silently_fixed(self):
        self.assertEqual(classification(-2.5), "negative_unverified")

    def test_boolean_intensity_not_numeric(self):
        self.assertEqual(classification(True), "unknown_or_nonfinite")

    def test_disabled_light_counted(self):
        b = source_light()
        b["m_Enabled"] = 0
        c = audit_lights([Obj("Light", 2, b), Obj("GameObject", 3)])["counts"]
        self.assertEqual(c["original_light_enabled_no"], 1)

    def test_typetree_failure_marked_unknown(self):
        c = audit_lights([Obj("Light", 2, fail=True)])["counts"]
        self.assertEqual(c["original_light_typetree_unknown"], 1)
        self.assertNotIn("original_light_enabled_yes", c)

    def test_duplicate_native_path_id_rejected(self):
        with self.assertRaisesRegex(SourceError, "duplicate_object_id"):
            audit_lights([Obj("Light", 2, source_light()), Obj("GameObject", 2)])

    def test_unexpected_light_type_flagged(self):
        b = source_light()
        b["m_Type"] = "directional?"
        c = audit_lights([Obj("Light", 2, b), Obj("GameObject", 3)])["counts"]
        self.assertEqual(c["original_light_type_unknown"], 1)

    def test_root_symlink_rejected_before_loader(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            source = base / "source"
            source.mkdir()
            link = base / "linked"
            link.symlink_to(source, target_is_directory=True)
            with self.assertRaisesRegex(SourceError, "unsafe_lighting_source_root"):
                run(link, loader=lambda _: self.fail("loader should not run"))

    def test_untrusted_shas_fails_before_loader(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name, (size, _) in PIN.items():
                (root / name).write_bytes(b"x" * size)
            with self.assertRaisesRegex(SourceError, "original_sha256_mismatch"):
                run(root, loader=lambda _: self.fail("loader should not run"))


if __name__ == "__main__":
    unittest.main()
