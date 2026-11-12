"""GT exact nonstandard exported image pointer-to-original class test fixtures."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts.gt_diagnose_texture_export_lineage import analyze

A,B="a"*32,"b"*32


def original_trace(cls=89,fid=8900000):
    return {"schema_version":1,"export_instance":"f"*32,
            "objects":[{"class_id":cls,
              "source":{"owner":"sharedassets6.assets","path_id":100},
              "export":{"file_id":fid,"guid":B,"type":3},
              "exportable":True}]}


def material(fid=8900000):
    return (f"%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n"
      f"--- !u!21 &2100000\nMaterial:\n  m_SavedProperties:\n"
      f"    m_TexEnvs:\n    - _Cube:\n"
      f"        m_Texture: {{fileID: {fid}, guid: {B}, type: 3}}\n"
      f"        m_Scale: {{x: 1, y: 1}}\n"
      f"        m_Offset: {{x: 0, y: 0}}\n    m_Ints: []\n")


class TexturedCubeTests(unittest.TestCase):
    def setUp(self):
        t=tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root=Path(t.name)
        self.assets=self.root/"project/Assets"
        self.assets.mkdir(parents=True)
        (self.assets/"material.mat").write_text(material())
        (self.assets/"material.mat.meta").write_text("guid: "+A+"\nNativeFormatImporter:\n")
        (self.assets/"target.png").write_bytes(b"fixture")
        self.meta=self.assets/"target.png.meta"
        self.meta.write_text("guid: "+B+"\nTextureImporter:\n  textureShape: 2\n")
        self.trace=self.root/"private-trace.json"
        self.trace.write_text(json.dumps(original_trace()))

    def run_analyze(self):
        return analyze(self.root/"project",self.trace)

    def test_exact_Cubemap_export_guid_and_importer_cubemap_shape(self):
        r=self.run_analyze()
        self.assertEqual(r["counts"]["class_cubemap"],1)
        self.assertEqual(r["counts"]["file_id_8900000"],1)
        self.assertEqual(r["counts"]["importer_shape_enum_2"],1)
        self.assertEqual(r["counts"]["same_instance_cubemap_pointer_and_importer_shape_coherent"],1)
        self.assertEqual(r["distinct_nonstandard_image_pointers"],1)
        self.assertFalse(r["all_nonstandard_targets_proven_importable"])
        self.assertNotIn(B,json.dumps(r))

    def test_importer_shape_mismatch_is_not_counted_as_coherent(self):
        self.meta.write_text("guid: "+B+"\nTextureImporter:\n  textureShape: 1\n")
        r=self.run_analyze()
        self.assertEqual(r["counts"]["requires_unresolved_import_or_source_repair"],1)
        self.assertEqual(r["counts"].get("same_instance_cubemap_pointer_and_importer_shape_coherent",0),0)

    def test_nonstandard_pointer_without_source_object_trace(self):
        self.trace.write_text(json.dumps(original_trace(cls=89,fid=8900001)))
        r=self.run_analyze()
        self.assertEqual(r["counts"]["no_exact_source_export_texture_trace"],1)
        self.assertEqual(r["counts"]["requires_unresolved_import_or_source_repair"],1)

    def test_wrong_source_class_is_not_cubemap_proof(self):
        self.trace.write_text(json.dumps(original_trace(cls=28)))
        r=self.run_analyze()
        self.assertEqual(r["counts"]["class_texture2d"],1)
        self.assertEqual(r["counts"]["requires_unresolved_import_or_source_repair"],1)

    def test_real_class_187_array_with_importer_shape_enum_is_not_silently_classified_as_2d(self):
        self.meta.write_text("guid: "+B+"\nTextureImporter:\n  textureShape: 3\n")
        (self.assets/"material.mat").write_text(material(18700000))
        self.trace.write_text(json.dumps(original_trace(cls=187,fid=18700000)))
        r=self.run_analyze()
        self.assertEqual(r["counts"]["class_texture2darray"],1)
        self.assertEqual(r["counts"]["file_id_18700000"],1)
        self.assertEqual(r["counts"]["importer_shape_enum_3"],1)
        self.assertEqual(r["counts"]["requires_unresolved_import_or_source_repair"],1)
        self.assertFalse(r["all_nonstandard_targets_proven_importable"])

    def test_broken_trace_schema_fails_closed(self):
        self.trace.write_text(json.dumps({"schema_version":1,"objects":[]}))
        with self.assertRaisesRegex(ValueError,"bad_original_exporter_trace_schema"):
            self.run_analyze()


if __name__=="__main__":
    unittest.main()
