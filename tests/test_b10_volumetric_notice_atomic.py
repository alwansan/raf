"""B10 real shader-restorer fault-injection tests (synthetic inputs only)."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts.restore_tmp_shaders import restore
from scripts.restore_volumetric_shaders import (
    COMMIT, EXPECTED, NOTICE, ROOT, restore_project, sources,
)
from tests.test_restore_volumetric_shaders import VolumetricTests


class B10VolumetricNoticeAtomicTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.project = self.root / "project"
        self.backup = self.root / "external-backup"
        manifest, blobs = VolumetricTests().fixture()
        self.shaders, self.license = sources(manifest, blobs.__getitem__)
        self.notice = self.project / NOTICE
        self.originals = {}
        for i, name in enumerate(self.shaders):
            shader = self.project / "Assets/Shader" / (str(i) + ".shader")
            shader.parent.mkdir(parents=True, exist_ok=True)
            shader.write_text('Shader "' + name + '" { SubShader { Pass {} } }\n')
            meta = Path(str(shader) + ".meta")
            meta.write_text("guid: original-" + str(i) + "\n")
            self.originals[shader] = (shader.read_bytes(), meta.read_bytes())

    def assert_originals(self):
        for shader, (original, metadata) in self.originals.items():
            self.assertEqual(shader.read_bytes(), original)
            self.assertEqual(Path(str(shader) + ".meta").read_bytes(), metadata)

    def test_success_publishes_notice_with_shader_replacements(self):
        self.assertEqual(restore_project(self.project, self.backup, self.shaders, self.license), 3)
        self.assertEqual(self.notice.read_bytes(), self.license)
        self.assertEqual((self.project / ROOT / "LICENSE.md").read_bytes(), self.license)
        for shader, (original, metadata) in self.originals.items():
            self.assertNotEqual(shader.read_bytes(), original)
            self.assertEqual(Path(str(shader) + ".meta").read_bytes(), metadata)
            self.assertEqual((self.backup / shader.relative_to(self.project / "Assets")).read_bytes(), original)

    def test_notice_open_error_removes_prior_new_deps_and_preserves_shaders(self):
        orig = Path.open
        def inject(path, mode="r", *args, **kwargs):
            if path == self.notice and mode == "xb":
                raise OSError("synthetic notice-create failure")
            return orig(path, mode, *args, **kwargs)
        with patch.object(Path, "open", inject):
            with self.assertRaisesRegex(OSError, "notice-create"):
                restore_project(self.project, self.backup, self.shaders, self.license)
        self.assert_originals()
        self.assertFalse(self.notice.exists())
        self.assertFalse((self.project / ROOT / "LICENSE.md").exists())
        self.assertTrue(self.backup.exists())

    def test_partial_notice_write_error_unlinks_partial_and_rolls_back(self):
        orig, target = Path.open, self.notice
        class PartialWriter:
            def __enter__(self):
                self.stream = orig(target, "xb")
                return self
            def write(self, data):
                self.stream.write(data[:4])
                self.stream.flush()
                raise OSError("synthetic partial-notice write")
            def __exit__(self, exc_type, exc_value, traceback):
                self.stream.close()
                return False
        def inject(path, mode="r", *args, **kwargs):
            if path == target and mode == "xb":
                return PartialWriter()
            return orig(path, mode, *args, **kwargs)
        with patch.object(Path, "open", inject):
            with self.assertRaisesRegex(OSError, "partial-notice"):
                restore_project(self.project, self.backup, self.shaders, self.license)
        self.assert_originals()
        self.assertFalse(self.notice.exists())
        self.assertFalse((self.project / ROOT / "LICENSE.md").exists())
        self.assertTrue(self.backup.exists())

    def test_symlinked_notice_parent_rejected_before_backup(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.project / "Assets/StreamingAssets").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "(?i)unsafe|symlink"):
            restore_project(self.project, self.backup, self.shaders, self.license)
        self.assert_originals()
        self.assertFalse(self.backup.exists())
        self.assertEqual(list(outside.iterdir()), [])

    def test_symlinked_notice_leaf_rejected_even_if_bytes_match(self):
        outside = self.root / "outside.txt"
        outside.write_bytes(self.license)
        self.notice.parent.mkdir(parents=True)
        self.notice.symlink_to(outside)
        with self.assertRaisesRegex(ValueError, "(?i)unsafe|symlink"):
            restore_project(self.project, self.backup, self.shaders, self.license)
        self.assert_originals()
        self.assertFalse(self.backup.exists())
        self.assertEqual(outside.read_bytes(), self.license)

    def test_existing_matching_notice_not_reopened_or_rewritten(self):
        self.notice.parent.mkdir(parents=True)
        self.notice.write_bytes(self.license)
        orig = Path.open
        def inject(path, mode="r", *args, **kwargs):
            if path == self.notice and mode in ("wb", "xb", "ab"):
                raise AssertionError("matching notice must remain untouched")
            return orig(path, mode, *args, **kwargs)
        with patch.object(Path, "open", inject):
            self.assertEqual(restore_project(self.project, self.backup, self.shaders, self.license), 3)
        self.assertEqual(self.notice.read_bytes(), self.license)

    def test_different_existing_notice_is_rejected_before_backup(self):
        self.notice.parent.mkdir(parents=True)
        self.notice.write_bytes(b"conflicting notice")
        with self.assertRaisesRegex(ValueError, "Conflicting"):
            restore_project(self.project, self.backup, self.shaders, self.license)
        self.assert_originals()
        self.assertFalse(self.backup.exists())

    def test_unsafe_extra_assets_fail_closed(self):
        malformed = (
            {"../other": b"x"}, {"/tmp/elsewhere": b"x"},
            {"Assets/../outside": b"x"}, {"Assets//foo": b"x"},
            {"Assets\\foo": b"x"}, {"Assets/ok\x00bad": b"x"},
            {"Unrelated/thing": b"x"}, {ROOT + "LICENSE.md": b"x"},
            {NOTICE: "not bytes"}, {NOTICE: b"x" * (1024 * 1024 + 1)},
        )
        for extra in malformed:
            with self.subTest(path=next(iter(extra))):
                with self.assertRaises(ValueError):
                    restore(self.project, self.backup, self.shaders, {}, self.license,
                            shader_prefix=tuple(EXPECTED[p][0] for p in EXPECTED),
                            include_root=ROOT, label="VOLUMETRIC",
                            vendor_version=COMMIT, extra_additions=extra)
                self.assert_originals()
                self.assertFalse(self.backup.exists())


if __name__ == "__main__":
    unittest.main()
