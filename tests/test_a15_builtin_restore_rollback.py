"""A15 CPU-only fail-first tests for built-in shader publication rollback.

Synthetic vendor paths/content only; no original game shaders, Unity or LFS.
"""
from pathlib import Path
from unittest import mock
import tempfile
import unittest

from scripts.restore_builtin_shaders import NOTICE, ROOT, restore_project


def fixture(base):
    project = base / "project"
    shader = project / "Assets/Shaders/standard.shader"
    shader.parent.mkdir(parents=True)
    before = b'Shader "Standard" { SubShader { Pass {} } }'
    shader.write_bytes(before)
    meta = Path(str(shader) + ".meta")
    original_meta = b"guid: " + b"a" * 32 + b"\n"
    meta.write_bytes(original_meta)
    custom = shader.parent / "private.shader"
    original_custom = b'Shader "Raft/SyntheticCustom" { Pass {} }'
    custom.write_bytes(original_custom)
    src = "DefaultResourcesExtra/Standard.shader"
    inc = "CGIncludes/helper.cginc"
    files = {src: 'Shader "Standard" { CGPROGRAM\n#include "helper.cginc"\nENDCG }',
             inc: "// synthetic include\n"}
    return project, shader, meta, custom, before, original_meta, original_custom, {"Standard": src}, files


class _PartialWriter:
    def __init__(self, actual):
        self.actual = actual

    def __enter__(self):
        self.actual.__enter__()
        return self

    def __exit__(self, *args):
        return self.actual.__exit__(*args)

    def write(self, content):
        self.actual.write(content[:max(1, len(content) // 2)])
        raise OSError("A15 simulated interrupted write")


class BuiltinRestoreRollbackTests(unittest.TestCase):
    def test_partial_new_include_is_removed_and_originals_are_unchanged(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, shader, meta, custom, original, guid, private, mapping, files = fixture(root)
            include = project / ROOT / "CGIncludes/helper.cginc"
            real_open = Path.open

            def interrupt(path, mode="r", *args, **kwargs):
                handle = real_open(path, mode, *args, **kwargs)
                if path == include and mode in ("wb", "xb"):
                    return _PartialWriter(handle)
                return handle

            with mock.patch.object(Path, "open", interrupt):
                with self.assertRaisesRegex(OSError, "interrupted write"):
                    restore_project(project, root / "backup", mapping, files, b"MIT")
            self.assertEqual(shader.read_bytes(), original)
            self.assertEqual(meta.read_bytes(), guid)
            self.assertEqual(custom.read_bytes(), private)
            self.assertFalse(include.exists(), "stranded partial include prevents next restore")
            self.assertFalse((project / NOTICE).exists(), "new notice must be rolled back")
            self.assertFalse((project / ROOT / "license.txt").exists())
            self.assertEqual((root / "backup/Shaders/standard.shader").read_bytes(), original)

    def test_shader_replacement_failure_reverts_new_additions(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, shader, meta, custom, original, guid, private, mapping, files = fixture(root)
            real_open = Path.open
            failed = [False]

            def interrupt(path, mode="r", *args, **kwargs):
                handle = real_open(path, mode, *args, **kwargs)
                if path == shader and mode in ("wb", "xb") and not failed[0]:
                    failed[0] = True
                    return _PartialWriter(handle)
                return handle

            with mock.patch.object(Path, "open", interrupt):
                with self.assertRaisesRegex(OSError, "interrupted write"):
                    restore_project(project, root / "backup", mapping, files, b"MIT")
            self.assertTrue(failed[0])
            self.assertEqual(shader.read_bytes(), original)
            self.assertEqual(meta.read_bytes(), guid)
            self.assertEqual(custom.read_bytes(), private)
            for target in (project / NOTICE, project / ROOT / "license.txt",
                           project / ROOT / "CGIncludes/helper.cginc"):
                self.assertFalse(target.exists(), f"stranded new target: {target.name}")

    def test_matching_preexisting_notice_is_never_rewritten(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, shader, meta, custom, original, guid, private, mapping, files = fixture(root)
            notice = project / NOTICE
            notice.parent.mkdir(parents=True)
            notice.write_bytes(b"MIT")
            real_open = Path.open

            def guard(path, mode="r", *args, **kwargs):
                if path == notice and mode in ("wb", "xb"):
                    raise AssertionError("identical preexisting notice must not be rewritten")
                return real_open(path, mode, *args, **kwargs)

            with mock.patch.object(Path, "open", guard):
                self.assertEqual(restore_project(project, root / "backup", mapping, files, b"MIT"), 1)
            self.assertEqual(notice.read_bytes(), b"MIT")
            self.assertEqual(meta.read_bytes(), guid)
            self.assertEqual(custom.read_bytes(), private)
            self.assertNotEqual(shader.read_bytes(), original)

    def test_concurrent_new_destination_is_not_overwritten_or_deleted(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, shader, meta, custom, original, guid, private, mapping, files = fixture(root)
            include = project / ROOT / "CGIncludes/helper.cginc"
            real_open = Path.open
            forged = b"concurrent-fixture-writer"
            observed = [False]

            def race(path, mode="r", *args, **kwargs):
                if path == include and mode in ("wb", "xb") and not observed[0]:
                    observed[0] = True
                    with real_open(path, "xb") as file:
                        file.write(forged)
                    raise FileExistsError("A15 concurrent destination")
                return real_open(path, mode, *args, **kwargs)

            with mock.patch.object(Path, "open", race):
                with self.assertRaisesRegex(FileExistsError, "concurrent destination"):
                    restore_project(project, root / "backup", mapping, files, b"MIT")
            self.assertTrue(observed[0])
            self.assertEqual(include.read_bytes(), forged)
            self.assertEqual(shader.read_bytes(), original)
            self.assertEqual(meta.read_bytes(), guid)
            self.assertEqual(custom.read_bytes(), private)
            self.assertFalse((project / NOTICE).exists())
            self.assertFalse((project / ROOT / "license.txt").exists())


if __name__ == "__main__":
    unittest.main()
