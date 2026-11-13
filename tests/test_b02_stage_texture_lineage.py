"""B02 optional Texture2D28 exporter trace staging tests."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest import mock

from scripts import b02_stage_texture_lineage as m

HELPER = Path(__file__).resolve().parents[1] / "android-port/Experiments/ExportLineage/RaftExportLineage.cs"


class StageFixture(unittest.TestCase):
    def test_verified_original_and_nonmutating_staging(self):
        original = HELPER.read_bytes()
        self.assertEqual(m.git_blob_sha1(original), m.HELPER_BLOB_SHA1)
        with TemporaryDirectory() as d:
            dest = Path(d) / "helper.cs"
            r = m.stage(HELPER, dest)
            data = dest.read_text()
            self.assertTrue(r["source_git_blob_verified"])
            self.assertEqual(original, HELPER.read_bytes())
            self.assertIn(m.REVIEWED_SHADER_FILTER, data)
            self.assertIn("if (asset.ClassID is not (21 or 48) &&", data)
            self.assertIn("asset.ClassID is (28 or 84 or 89 or 117 or 187)", data)
            self.assertIn("CaptureTextureObjects(container, collections, texturePath, exportInstance)", data)
            self.assertIn("if (asset.ClassID != 28)", data)
            self.assertEqual(data.count('json.WriteString("export_instance", exportInstance);'), 2)
            self.assertIn("FileMode.CreateNew", data)
            self.assertFalse(r["modified_shared_source"])

    def test_source_pin_tamper_rejected(self):
        with self.assertRaisesRegex(ValueError, "untrusted W1"):
            m.render(HELPER.read_bytes() + b"changed")

    def test_missing_anchor_rejected_even_with_replaced_pin(self):
        raw = HELPER.read_bytes().replace(m.GUID_ANCHOR.encode(), b"//missing")
        with mock.patch.object(m, "HELPER_BLOB_SHA1", m.git_blob_sha1(raw)):
            with self.assertRaisesRegex(ValueError, "ambiguous"):
                m.render(raw)

    def test_existing_target_and_link_rejected(self):
        with TemporaryDirectory() as d:
            output = Path(d) / "helper.cs"
            output.write_text("protected")
            with self.assertRaisesRegex(ValueError, "destination"):
                m.stage(HELPER, output)
            self.assertEqual(output.read_text(), "protected")
            output.unlink()
            output.symlink_to(HELPER)
            with self.assertRaisesRegex(ValueError, "destination"):
                m.stage(HELPER, output)

    def test_source_link_and_destination_parent_link_rejected(self):
        with TemporaryDirectory() as d:
            fake = Path(d) / "source.cs"
            fake.symlink_to(HELPER)
            with self.assertRaisesRegex(ValueError, "source"):
                m.stage(fake, Path(d) / "out.cs")
            linked = Path(d) / "linked"
            linked.symlink_to(HELPER.parent, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "parent"):
                m.stage(HELPER, linked / "new.cs")

    def test_report_is_aggregate_and_not_pixel_proof(self):
        with TemporaryDirectory() as d:
            report = m.stage(HELPER, Path(d) / "staged.cs")
            self.assertFalse(report["texture_pixels_or_android_verified"])
            self.assertNotIn("path_id", str(report))


if __name__ == "__main__":
    unittest.main()
