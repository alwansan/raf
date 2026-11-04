"""B21 class108 SHA-pinned disposable exporter composition tests."""
from pathlib import Path
from tempfile import TemporaryDirectory
import hashlib
import unittest
from unittest import mock

from scripts import b21_stage_light_lineage as m
from scripts import b02_stage_texture_lineage as b02

BASE = Path(__file__).resolve().parents[1] / "android-port/Experiments/ExportLineage/RaftExportLineage.cs"


class TestB21LightLineage(unittest.TestCase):
    def test_all_three_capture_routes_preserved(self):
        before = BASE.read_bytes()
        self.assertEqual(b02.git_blob_sha1(before), b02.HELPER_BLOB_SHA1)
        rendered = m.render(before).decode("utf-8")
        self.assertIn('if (asset.ClassID is not (21 or 48))', rendered)
        self.assertIn('if (asset.ClassID != 28)', rendered)
        self.assertIn('if (asset.ClassID is not (1 or 108))', rendered)
        self.assertIn('RAFT_PRIVATE_EXPORT_LIGHT_LINEAGE', rendered)
        self.assertIn('RAFT_PRIVATE_EXPORT_TEXTURE_LINEAGE', rendered)
        self.assertIn('RAFT_PRIVATE_EXPORT_LINEAGE', rendered)
        self.assertEqual(rendered.count('json.WriteString("export_instance", exportInstance);'), 3)
        self.assertEqual(rendered.count('FileMode.CreateNew'), 3)
        self.assertEqual(before, BASE.read_bytes())

    def test_all_private_traces_share_export_instance(self):
        rendered = m.render(BASE.read_bytes()).decode()
        self.assertEqual(rendered.count('string exportInstance = Guid.NewGuid().ToString("N");'), 1)
        self.assertIn('CaptureLightObjects(container, collections, lightPath, exportInstance)', rendered)
        self.assertIn('CaptureTextureObjects(container, collections, texturePath, exportInstance)', rendered)

    def test_light_only_independent_optional_mode(self):
        rendered = m.render(BASE.read_bytes()).decode()
        self.assertIn('string.IsNullOrEmpty(texturePath) && string.IsNullOrEmpty(lightPath)', rendered)
        self.assertIn('if (string.IsNullOrEmpty(path))\n            return;', rendered)

    def test_non_exportable_not_equated_to_absent(self):
        rendered = m.render(BASE.read_bytes()).decode()
        self.assertIn('nonexportable_light_objects_skipped', rendered)
        self.assertIn('nonexportable_gameobjects_skipped', rendered)
        self.assertIn('if (!collection.Exportable)', rendered)
        self.assertIn('Ambiguous native scene object source identity', rendered)

    def test_tampered_w1_source_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'untrusted W1'):
            m.render(BASE.read_bytes() + b'\n//tampered')

    def test_changed_b02_stage_requires_review(self):
        with mock.patch.object(m, 'B02_RENDER_SHA256', '0' * 64):
            with self.assertRaisesRegex(ValueError, 'Unreviewed B02'):
                m.render(BASE.read_bytes())

    def test_missing_anchor_requires_review(self):
        staged = b02.render(BASE.read_bytes())
        edited = staged.replace(m.EARLY_RETURN.encode(), b"unrecognized conditional")
        with mock.patch.object(b02, 'render', return_value=edited):
            with mock.patch.object(m, 'B02_RENDER_SHA256', hashlib.sha256(edited).hexdigest()):
                with self.assertRaisesRegex(ValueError, 'Ambiguous Light'):
                    m.render(BASE.read_bytes())

    def test_stages_only_to_fresh_private_path(self):
        before = BASE.read_bytes()
        with TemporaryDirectory() as td:
            path = Path(td) / "RaftExportLineage.cs"
            report = m.stage(BASE, path)
            self.assertTrue(path.is_file())
            self.assertTrue(report['original_w1_helper_sha1_verified'])
            self.assertTrue(report['same_export_instance_with_w1_and_b02'])
            self.assertEqual(report['native_gameobject_class_id'], 1)
            self.assertFalse(report['same_export_gameobject_owner_verified'])
            self.assertFalse(report['shared_helpers_modified'])
            self.assertFalse(report['actual_raft_light_export_captured'])
            self.assertEqual(before, BASE.read_bytes())
            with self.assertRaisesRegex(ValueError, 'destination'):
                m.stage(BASE, path)

    def test_unsafe_source_link_refused(self):
        with TemporaryDirectory() as td:
            src = Path(td) / 'source.cs'
            src.symlink_to(BASE)
            with self.assertRaisesRegex(ValueError, 'Untrusted W1'):
                m.stage(src, Path(td) / 'output.cs')

    def test_unsafe_destination_parent_link_refused(self):
        with TemporaryDirectory() as td:
            parent = Path(td) / 'linked'
            parent.symlink_to(BASE.parent, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, 'staging destination'):
                m.stage(BASE, parent / 'output.cs')

    def test_light_trace_is_not_permanent_asset_or_shader_output(self):
        rendered = m.render(BASE.read_bytes()).decode()
        self.assertIn('Identity(json, "source", asset);', rendered)
        self.assertIn('Pointer(json, "export", collection.CreateExportPointer(container, asset, false));', rendered)
        self.assertNotIn('File.WriteAllText', rendered)
        self.assertNotIn('Shader.SetGlobal', rendered)


if __name__ == "__main__":
    unittest.main()
