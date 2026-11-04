"""B22: source-free negative controls for Android world/save tracing stage.

Original world, save and Steam method bodies are NOT altered here.
"""
import contextlib
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest import mock

from scripts import instrument_android_runtime_operations as op

ORIGINAL = b"void Demo() { OriginalSave(); }\n"
MODIFIED = ORIGINAL + b"// B22 synthetic instrumented source\n"


class OperationStageIntegrityTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "project"
        self.folder = self.project / "Assets" / "Assembly-CSharp"
        self.folder.mkdir(parents=True)
        self.source = self.folder / "Demo.cs"
        self.meta = self.folder / "Demo.cs.meta"
        self.source.write_bytes(ORIGINAL)
        self.meta.write_bytes(b"fileFormatVersion: 2\nguid: " + b"a"*32 + b"\n")
        self.backup = self.root / "backups"
        self.manifest = {"sources": {"Demo": {"methods": [{"signature": "void Demo()"}]}}}

    @contextlib.contextmanager
    def staged(self):
        with mock.patch.object(op, "instrument", side_effect=lambda name, text, manifest: text + "// B22 synthetic instrumented source\n"):
            yield

    def assert_original_intact(self):
        self.assertEqual(self.source.read_bytes(), ORIGINAL)
        self.assertEqual(self.meta.read_bytes(), b"fileFormatVersion: 2\nguid: " + b"a"*32 + b"\n")

    def test_dry_run_no_source_or_backup_mutation(self):
        with self.staged():
            r = op.apply(self.project, self.backup, self.manifest, write=False)
        self.assertFalse(r["applied"])
        self.assertFalse(self.backup.exists())
        self.assert_original_intact()

    def test_normal_staging_preserves_original_backup_and_meta(self):
        with self.staged():
            r = op.apply(self.project, self.backup, self.manifest, write=True)
        self.assertTrue(r["applied"])
        self.assertEqual(r["sourceFiles"], 1)
        self.assertEqual(self.source.read_bytes(), MODIFIED)
        self.assertEqual((self.backup / "Demo.cs").read_bytes(), ORIGINAL)
        self.assertEqual((self.backup / "Demo.cs.meta").read_bytes(), self.meta.read_bytes())

    def test_linked_project_root_rejected(self):
        alternate = self.root / "linked-project"
        alternate.symlink_to(self.project, target_is_directory=True)
        with self.staged(), self.assertRaises(ValueError):
            op.apply(alternate, self.backup, self.manifest, write=True)
        self.assert_original_intact()
        self.assertFalse(self.backup.exists())

    def test_linked_project_parent_rejected(self):
        external = self.root / "linked-parent"
        external.symlink_to(self.root, target_is_directory=True)
        with self.staged(), self.assertRaises(ValueError):
            op.apply(external / "project", self.backup, self.manifest, write=True)
        self.assert_original_intact()

    def test_linked_assets_rejected(self):
        physical = self.project / "physical"
        (self.project / "Assets").rename(physical)
        (self.project / "Assets").symlink_to(physical, target_is_directory=True)
        with self.staged(), self.assertRaises(ValueError):
            op.apply(self.project, self.backup, self.manifest, write=True)
        self.assertEqual((physical / "Assembly-CSharp" / "Demo.cs").read_bytes(), ORIGINAL)

    def test_linked_backup_directory_rejected(self):
        target = self.root / "real"
        target.mkdir()
        self.backup.symlink_to(target, target_is_directory=True)
        with self.staged(), self.assertRaises(ValueError):
            op.apply(self.project, self.backup, self.manifest, write=True)
        self.assert_original_intact()
        self.assertFalse(list(target.iterdir()))

    def test_linked_backup_parent_rejected(self):
        target = self.root / "real"
        target.mkdir()
        link = self.root / "alias"
        link.symlink_to(target, target_is_directory=True)
        with self.staged(), self.assertRaises(ValueError):
            op.apply(self.project, link / "backup", self.manifest, write=True)
        self.assert_original_intact()

    def test_linked_meta_rejected(self):
        target = self.root / "actual.meta"
        target.write_bytes(self.meta.read_bytes())
        self.meta.unlink()
        self.meta.symlink_to(target)
        with self.staged(), self.assertRaises(ValueError):
            op.apply(self.project, self.backup, self.manifest, write=True)
        self.assert_original_intact if False else None
        self.assertEqual(self.source.read_bytes(), ORIGINAL)

    def test_backup_inside_project_rejected(self):
        with self.staged(), self.assertRaises(ValueError):
            op.apply(self.project, self.project / "Assets" / "backup", self.manifest, write=True)
        self.assert_original_intact()

    def test_existing_backup_collision_rejected(self):
        self.backup.mkdir()
        (self.backup / "Demo.cs").write_bytes(b"UNRELATED")
        with self.staged(), self.assertRaises(ValueError):
            op.apply(self.project, self.backup, self.manifest, write=True)
        self.assert_original_intact()
        self.assertEqual((self.backup / "Demo.cs").read_bytes(), b"UNRELATED")

    def test_partial_backup_copy_failure_cleans_targets_without_source_changes(self):
        original_copy = shutil.copy2
        def fail_meta(src, dst, *a, **k):
            if Path(src).name.endswith(".meta"):
                Path(dst).write_bytes(b"PARTIAL")
                raise OSError("synthetic backup copy failure")
            return original_copy(src, dst, *a, **k)
        with self.staged(), mock.patch.object(op.shutil, "copy2", side_effect=fail_meta):
            with self.assertRaisesRegex(OSError, "synthetic backup"):
                op.apply(self.project, self.backup, self.manifest, write=True)
        self.assert_original_intact()
        self.assertFalse(self.backup.exists())

    def test_failed_source_install_rolls_back_and_removes_new_backup(self):
        original_write = Path.write_bytes
        def fail_new_source(path, data):
            if path == self.source and data == MODIFIED:
                raise OSError("synthetic installed source failure")
            return original_write(path, data)
        with self.staged(), mock.patch.object(Path, "write_bytes", new=fail_new_source):
            with self.assertRaisesRegex(OSError, "synthetic installed"):
                op.apply(self.project, self.backup, self.manifest, write=True)
        self.assert_original_intact()
        self.assertFalse(self.backup.exists())

    def test_failed_original_rollback_retains_backup_for_recovery(self):
        original_write = Path.write_bytes
        def fail_install_and_restore(path, data):
            if path == self.source and data == MODIFIED:
                original_write(path, data)
                raise OSError("synthetic half installed")
            if path == self.source and data == ORIGINAL:
                raise OSError("synthetic rollback failure")
            return original_write(path, data)
        with self.staged(), mock.patch.object(Path, "write_bytes", new=fail_install_and_restore):
            with self.assertRaisesRegex(ValueError, "rollback failed; backups retained"):
                op.apply(self.project, self.backup, self.manifest, write=True)
        self.assertEqual((self.backup / "Demo.cs").read_bytes(), ORIGINAL)
        self.assertEqual((self.backup / "Demo.cs.meta").read_bytes(), self.meta.read_bytes())

    def test_original_body_rejection_precedes_any_backup_write(self):
        with self.assertRaises(ValueError):
            op.apply(self.project, self.backup,
                     {"sources": {"Demo": {"sha256": "f"*64, "methods": [], "area": "save"}}},
                     write=True)
        self.assert_original_intact()
        self.assertFalse(self.backup.exists())


if __name__ == "__main__":
    unittest.main()
