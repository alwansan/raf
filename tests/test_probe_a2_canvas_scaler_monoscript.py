"""Synthetic-only original MonoScript + CanvasScaler pointer proof tests."""
from pathlib import Path
import tempfile
import unittest

from scripts.probe_a2_canvas_scaler_monoscript import (
    audit, inspect_scene_file, resolve_script, script_category,
    script_registry, ORIGINAL_SCRIPTS_BLOB,
)
from scripts.probe_a2_scene_ui_layout import SCENE_BLOBS, git_blob_sha


class FakeObject:
    def __init__(self, kind, path_id, tree=None, error=False):
        self.type = type("FakeType", (), {"name": kind})()
        self.path_id = path_id
        self.tree = tree
        self.error = error

    def read_typetree(self, **kwargs):
        if self.error:
            raise ValueError("Unknown original managed fields")
        return self.tree


class FakeFile:
    def __init__(self, objects, paths=None):
        self.objects = {o.path_id: o for o in objects}
        self.externals = [type("External", (), {"path": p})() for p in (paths or [])]


class FakeEnv:
    def __init__(self, file):
        self.file = file


class A2OriginalScalerTests(unittest.TestCase):
    def test_canvas_scaler_identity_requires_namespace_and_assembly(self):
        self.assertEqual(script_category({"m_ClassName": "CanvasScaler",
            "m_Namespace": "UnityEngine.UI", "m_AssemblyName": "UnityEngine.UI"}),
            "verified_unity_ui_canvas_scaler")
        self.assertEqual(script_category({"m_ClassName": "CanvasScaler",
            "m_Namespace": "Other.Namespace", "m_AssemblyName": "Unknown"}),
            "canvas_scaler_name_only_not_verified")
        self.assertEqual(script_category({"m_ClassName": "CanvasScaler"}),
                         "unknown")

    def test_rejects_other_external_script_owner_and_bad_ids(self):
        global_scripts = {25: "verified_unity_ui_canvas_scaler"}
        self.assertEqual(resolve_script({"m_FileID": 1, "m_PathID": 25},
            ["archive:/x/globalgamemanagers.assets"], {}, global_scripts),
            "verified_unity_ui_canvas_scaler")
        self.assertEqual(resolve_script({"m_FileID": 1, "m_PathID": 25},
            ["archive:/x/sharedassets0.assets"], {}, global_scripts),
            "unresolved_other_original_owner")
        self.assertEqual(resolve_script({"m_FileID": True, "m_PathID": 25},
            ["globalgamemanagers.assets"], {}, global_scripts), "unresolved_pointer")
        self.assertEqual(resolve_script({"m_FileID": 3, "m_PathID": 25},
            ["globalgamemanagers.assets"], {}, global_scripts), "unresolved_external_script")
        self.assertEqual(resolve_script(None, [], {}, global_scripts), "unresolved_pointer")

    def test_script_registry_only_monoscripts(self):
        objects = [
            FakeObject("MonoScript", 25, {"m_ClassName": "CanvasScaler",
                "m_Namespace": "UnityEngine.UI", "m_AssemblyName": "UnityEngine.UI"}),
            FakeObject("MonoScript", 26, error=True),
            FakeObject("GameObject", 22, {"m_Name": "Settings"}),
        ]
        names, counts = script_registry(objects)
        self.assertEqual(names[25], "verified_unity_ui_canvas_scaler")
        self.assertEqual(counts["monoscript_objects"], 2)
        self.assertEqual(counts["unknown"], 1)
        self.assertNotIn(22, names)

    def test_scene_reports_canvas_scaler_link_not_serialized_parameters(self):
        ptr = lambda fid, pid: {"m_FileID": fid, "m_PathID": pid}
        records = [
            FakeObject("GameObject", 1, {"m_Name": "MainSettings"}),
            FakeObject("Canvas", 2, {"m_GameObject": ptr(0, 1)}),
            FakeObject("MonoBehaviour", 3, {"m_GameObject": ptr(0, 1),
                "m_Script": ptr(1, 25)}),
        ]
        owner = FakeFile(records, ["archive:/test/globalgamemanagers.assets"])
        result = inspect_scene_file(owner, {25: "verified_unity_ui_canvas_scaler"})
        self.assertEqual(result["counts"]["verified_unity_ui_canvas_scaler"], 1)
        self.assertEqual(result["counts"]["canvas_scaler_owner_is_native_canvas_owner"], 1)
        self.assertEqual(result["counts"]["canvas_scaler_owner_named_settings"], 1)
        self.assertFalse(result["canvas_scaler_custom_fields_decoded"])
        self.assertNotIn("MainSettings", str(result))

    def test_audit_requires_exact_original_script_binary(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            for n in ("level0", "level1"):
                (root / n).write_bytes(b"synthetic fake scene file" * 6)
            (root / "globalgamemanagers.assets").write_bytes(b"synthetic original scripts" * 6)
            with self.assertRaisesRegex(ValueError, "fingerprint"):
                audit(root, unity_loader=lambda p: FakeEnv(FakeFile([])))
            # The repo's pinned original SHA is never accepted for synthetic bytes.
            self.assertEqual(len(ORIGINAL_SCRIPTS_BLOB), 40)
            self.assertEqual(len(SCENE_BLOBS["level0"]), 40)

if __name__ == "__main__":
    unittest.main()
