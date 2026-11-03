"""A11 synthetic source-export scope checks. No proprietary shader data."""
import contextlib
import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts.probe_a11_shader_export_scope import ScopeError, main, snapshot, verify


def add_shader(project, name, content=b'Shader "Synthetic" {}', meta=None):
    path = project / "Assets" / "Shaders" / (name + ".shader")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(content)
    if meta is None:
        meta = b"fileFormatVersion: 2\nguid: " + hashlib.sha256(name.encode()).hexdigest()[:32].encode() + b"\n"
    path.with_name(path.name + ".meta").write_bytes(meta)
    return path


class ShaderExportScopeTests(unittest.TestCase):
    def fixture(self, root):
        project = root / "ExportedProject"
        path = add_shader(project, "a")
        return project, path

    def test_positive_snapshot_is_integrity_only_not_completeness(self):
        with tempfile.TemporaryDirectory() as temp:
            project, _ = self.fixture(Path(temp))
            record = snapshot(project)
            result = verify(project, record, expected_shaders=1, expected_computes=0)
            self.assertTrue(result["local_snapshot_bytes_unchanged"])
            self.assertTrue(result["reported_counts_consistent"])
            self.assertFalse(result["original_export_provenance_verified"])
            self.assertFalse(result["built_in_identity_matches_verified"])
            self.assertFalse(result["ready_for_build"])
            self.assertNotIn("Shaders/a", json.dumps(record))

    def test_107_file_sample_rejected_against_140_run_report(self):
        with tempfile.TemporaryDirectory() as temp:
            project, _ = self.fixture(Path(temp))
            for i in range(1, 107):
                add_shader(project, "local-" + str(i))
            record = snapshot(project)
            self.assertEqual(record["shader_files"], 107)
            with self.assertRaisesRegex(ScopeError, "reported_shader_count_mismatch"):
                verify(project, record, expected_shaders=140, expected_computes=0)

    def test_changed_shader_content_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            project, path = self.fixture(Path(temp))
            record = snapshot(project)
            path.write_bytes(b'Shader "Different Synthetic" {}')
            with self.assertRaisesRegex(ScopeError, "snapshot_scope_or_content_mismatch"):
                verify(project, record)

    def test_changed_meta_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            project, path = self.fixture(Path(temp))
            record = snapshot(project)
            path.with_name(path.name + ".meta").write_bytes(
                b"fileFormatVersion: 2\nguid: ffffffffffffffffffffffffffffffff\n")
            with self.assertRaisesRegex(ScopeError, "snapshot_scope_or_content_mismatch"):
                verify(project, record)

    def test_rename_rejected_even_with_identical_source_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            project, path = self.fixture(Path(temp))
            record = snapshot(project)
            renamed = path.with_name("b.shader")
            path.rename(renamed)
            path.with_name(path.name + ".meta").rename(renamed.with_name(renamed.name + ".meta"))
            with self.assertRaisesRegex(ScopeError, "snapshot_scope_or_content_mismatch"):
                verify(project, record)

    def test_new_file_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            project, _ = self.fixture(Path(temp))
            record = snapshot(project)
            add_shader(project, "b")
            with self.assertRaisesRegex(ScopeError, "snapshot_scope_or_content_mismatch"):
                verify(project, record)

    def test_missing_metadata_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            project, path = self.fixture(Path(temp))
            path.with_name(path.name + ".meta").unlink()
            with self.assertRaisesRegex(ScopeError, "missing_or_unsafe_shader_meta"):
                snapshot(project)

    def test_symlinked_subfolder_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, _ = self.fixture(root)
            target = root / "off-project"
            target.mkdir()
            (project / "Assets" / "Redirect").symlink_to(target, target_is_directory=True)
            with self.assertRaisesRegex(ScopeError, "redirected_asset_entry"):
                snapshot(project)

    def test_empty_inventory_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "Assets").mkdir()
            with self.assertRaisesRegex(ScopeError, "empty_shader_export_inventory"):
                snapshot(root)

    def test_modified_manifest_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            project, _ = self.fixture(Path(temp))
            record = snapshot(project)
            record["original_export_provenance_verified"] = True
            with self.assertRaisesRegex(ScopeError, "snapshot_scope_or_content_mismatch"):
                verify(project, record)

    def test_cli_red_green_outputs_aggregate_only(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, _ = self.fixture(root)
            manifest = root / "snapshot.json"
            with contextlib.redirect_stdout(io.StringIO()) as captured:
                rc = main(["--project", str(project), "--write-local-snapshot", str(manifest)])
            self.assertEqual(rc, 0)
            self.assertIn('"original_export_provenance_verified": false', captured.getvalue().lower())
            with contextlib.redirect_stdout(io.StringIO()) as captured:
                ok = main(["--project", str(project), "--verify-local-snapshot", str(manifest),
                           "--expected-shaders", "1", "--expected-computes", "0"])
            self.assertEqual(ok, 0)
            self.assertNotIn("Synthetic", captured.getvalue())
            with contextlib.redirect_stdout(io.StringIO()) as captured:
                rejected = main(["--project", str(project), "--verify-local-snapshot", str(manifest),
                                 "--expected-shaders", "140", "--expected-computes", "0"])
            self.assertEqual(rejected, 2)
            self.assertIn("reported_shader_count_mismatch", captured.getvalue())
            self.assertNotIn("Synthetic", captured.getvalue())

    def test_symlinked_project_ancestor_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            actual_parent = root / "trusted"
            project, _ = self.fixture(actual_parent)
            alias = root / "link"
            alias.symlink_to(actual_parent, target_is_directory=True)
            with self.assertRaisesRegex(ScopeError, "symlinked_project_ancestor"):
                snapshot(alias / "ExportedProject")

    def test_invalid_guids_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, path = self.fixture(root)
            path.with_name(path.name + ".meta").write_bytes(b"fileFormatVersion: 2\nguid: BAD\n")
            with self.assertRaisesRegex(ScopeError, "invalid_shader_meta_guid"):
                snapshot(project)

    def test_duplicate_guids_fail_closed_even_for_unique_paths(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, first = self.fixture(root)
            second = add_shader(project, "other")
            second.with_name(second.name + ".meta").write_bytes(
                first.with_name(first.name + ".meta").read_bytes()
            )
            with self.assertRaisesRegex(ScopeError, "duplicate_shader_meta_guid"):
                snapshot(project)

    def test_orphan_shader_metadata_fails_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, _ = self.fixture(root)
            orphan = project / "Assets" / "Shaders" / "missing.shader.meta"
            orphan.write_bytes(b"fileFormatVersion: 2\nguid: 0123456789abcdef0123456789abcdef\n")
            with self.assertRaisesRegex(ScopeError, "orphan_shader_meta"):
                snapshot(project)

    def test_mismatched_expected_count_rejects_before_snapshot_write(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, _ = self.fixture(root)
            out = root / "should-not-exist.json"
            with contextlib.redirect_stdout(io.StringIO()) as log:
                code = main(["--project", str(project), "--write-local-snapshot", str(out),
                             "--expected-shaders", "140", "--expected-computes", "0"])
            self.assertEqual(code, 2)
            self.assertFalse(out.exists())
            self.assertIn("reported_shader_count_mismatch", log.getvalue())

    def test_one_sided_expected_count_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            project, _ = self.fixture(root)
            record = snapshot(project)
            with self.assertRaisesRegex(ScopeError, "incomplete_expected_counts"):
                verify(project, record, expected_shaders=1)
            out = root / "should-not-exist.json"
            with contextlib.redirect_stdout(io.StringIO()) as log:
                code = main(["--project", str(project), "--write-local-snapshot", str(out),
                             "--expected-shaders", "1"])
            self.assertEqual(code, 2)
            self.assertFalse(out.exists())
            self.assertIn("incomplete_expected_counts", log.getvalue())


if __name__ == "__main__":
    unittest.main()
