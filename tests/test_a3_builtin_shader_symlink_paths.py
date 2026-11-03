"""A3 synthetic no-Unity filesystem redirect regressions for the built-in shader restorer."""
from pathlib import Path
import tempfile
import unittest

from scripts.restore_builtin_shaders import restore_project


def fixture(root):
    project = root / "project"
    shader = project / "Assets/Shaders/standard.shader"
    shader.parent.mkdir(parents=True)
    shader.write_text('Shader "Standard" { SubShader { Pass {} } }', encoding="utf-8")
    meta = Path(str(shader) + ".meta")
    meta.write_bytes(b"guid: " + b"a" * 32 + b"\n")
    sources = {"DefaultResourcesExtra/Standard.shader":
               'Shader "Standard" { SubShader { Pass {} } }'}
    return project, shader, meta, {"Standard": "DefaultResourcesExtra/Standard.shader"}, sources


class A3BuiltinPathTests(unittest.TestCase):
    def test_normal_non_symlink_restore_keeps_guid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project, shader, meta, mapping, sources = fixture(root)
            before = meta.read_bytes()
            self.assertEqual(restore_project(project, root / "backup", mapping, sources, b"MIT"), 1)
            self.assertEqual(meta.read_bytes(), before)
            self.assertEqual((project / "Assets/StreamingAssets/RaftAndroidNotices/unity-builtin-shaders-MIT.txt").read_bytes(), b"MIT")
            self.assertEqual((project / "Assets/RaftAndroid/BuiltinShaderSources/license.txt").read_bytes(), b"MIT")

    def test_streaming_assets_symlink_parent_refused_before_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project, shader, meta, mapping, sources = fixture(root)
            before, guid = shader.read_bytes(), meta.read_bytes()
            outside = root / "outside"
            outside.mkdir()
            (project / "Assets/StreamingAssets").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "(?i)unsafe|symlink"):
                restore_project(project, root / "backup", mapping, sources, b"MIT")
            self.assertEqual(list(outside.iterdir()), [])
            self.assertEqual(shader.read_bytes(), before)
            self.assertEqual(meta.read_bytes(), guid)
            self.assertFalse((root / "backup").exists())

    def test_builtin_source_symlink_parent_refused_before_mutation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project, shader, meta, mapping, sources = fixture(root)
            before, guid = shader.read_bytes(), meta.read_bytes()
            outside = root / "outside"
            outside.mkdir()
            (project / "Assets/RaftAndroid").symlink_to(outside, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "(?i)unsafe|symlink"):
                restore_project(project, root / "backup", mapping, sources, b"MIT")
            self.assertEqual(list(outside.iterdir()), [])
            self.assertEqual(shader.read_bytes(), before)
            self.assertEqual(meta.read_bytes(), guid)
            self.assertFalse((root / "backup").exists())

    def test_assets_root_symlink_refused_even_with_matching_shader(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            project, shader, meta, mapping, sources = fixture(root)
            outside = root / "moved-assets"
            (project / "Assets").rename(outside)
            (project / "Assets").symlink_to(outside, target_is_directory=True)
            before, guid = shader.read_bytes(), meta.read_bytes()
            with self.assertRaisesRegex(ValueError, "(?i)unsafe|symlink"):
                restore_project(project, root / "backup", mapping, sources, b"MIT")
            self.assertEqual(shader.read_bytes(), before)
            self.assertEqual(meta.read_bytes(), guid)
            self.assertFalse((root / "backup").exists())
            self.assertFalse((outside / "RaftAndroid").exists())


if __name__ == "__main__":
    unittest.main()
