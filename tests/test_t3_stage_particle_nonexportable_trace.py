"""Source-free private T3 B02 nonexportable Texture2D lineage instrumenter tests."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts import b21_stage_light_lineage as b21
from scripts import t3_stage_particle_nonexportable_trace as t3

PINNED_W1=Path("android-port/Experiments/ExportLineage/RaftExportLineage.cs")


class DisposableTexture2DTrace(unittest.TestCase):
    def test_exact_W1_B02_B21_staged_helper_includes_private_nonexportable_class28(self):
        private_base=b21.render(PINNED_W1.read_bytes())
        changed=t3.annotate(private_base)
        self.assertIn(b'nonexportable_texture_sources',changed)
        self.assertIn(b'nonExportableSourceObjects.Add(asset);',changed)
        self.assertIn(b'Identity(json, "source", asset);',changed)
        self.assertIn(b'if (asset.ClassID != 28)',changed)
        self.assertIn(b'if (!collection.Exportable)',changed)
        self.assertEqual(changed.count(b'json.WriteString("export_instance", exportInstance);'),3)
        self.assertNotEqual(changed,private_base)
        self.assertIn(b'nonexportable_light_objects_skipped',changed)

    def test_helper_byte_drift_and_mismatched_anchor_fail_closed(self):
        original=b21.render(PINNED_W1.read_bytes())
        with self.assertRaisesRegex(ValueError,"anchor_drift"):
            t3.annotate(original.replace(
                b'nonExportable++;',b'nonExportable+=1;',1))
        with self.assertRaisesRegex(ValueError,"missing_expected"):
            t3.annotate(b"private static void CaptureTextureObjects() {}")

    def test_disposable_stage_keeps_exact_W1_base_untouched(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            before=PINNED_W1.read_bytes()
            basedir=root/"shared_original";basedir.mkdir()
            tempdir=root/"runner_disposable";tempdir.mkdir()
            base=basedir/"RaftExportLineage.cs";base.write_bytes(before)
            output=tempdir/"RaftExportLineage.cs"
            output.write_bytes(b21.render(before))
            result=t3.stage(base,output)
            self.assertTrue(result["original_W1_B02_B21_source_authentic"])
            self.assertTrue(result["only_disposable_helper_modified"])
            self.assertFalse(result["private_source_IDs_published"])
            self.assertFalse(result["exporter_selection_or_asset_import_behavior_changed"])
            self.assertEqual(base.read_bytes(),before)
            self.assertNotEqual(output.read_bytes(),b21.render(before))

    def test_reject_stage_on_shared_or_modified_helper(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            parent=root/"owner";parent.mkdir()
            base=parent/"a.cs";base.write_bytes(PINNED_W1.read_bytes())
            other=parent/"b.cs";other.write_bytes(b21.render(base.read_bytes()))
            with self.assertRaisesRegex(ValueError,"non_disposable"):
                t3.stage(base,other)
            outside=root/"runner";outside.mkdir()
            modified=outside/"staged.cs"
            modified.write_bytes(b21.render(base.read_bytes())+b"// drift")
            with self.assertRaisesRegex(ValueError,"drifted"):
                t3.stage(base,modified)


if __name__=="__main__":
    unittest.main()
