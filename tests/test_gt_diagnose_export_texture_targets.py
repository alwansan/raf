"""GT original-export target classifier: synthetic positives/negative controls."""
from pathlib import Path
import tempfile
import unittest

from scripts.gt_diagnose_export_texture_targets import inspect, classify
from scripts.verify_exported_material_texture_links import GuardError

A, B, C = "a"*32, "b"*32, "c"*32


def material(refs):
    lines=["%YAML 1.1","%TAG !u! tag:unity3d.com,2011:",
           "--- !u!21 &2100000","Material:","  m_SavedProperties:",
           "    m_TexEnvs:"]
    for i,ref in enumerate(refs):
        lines += [f"    - _Test{i}:",f"        m_Texture: {ref}",
                  "        m_Scale: {x: 1, y: 1}",
                  "        m_Offset: {x: 0, y: 0}"]
    lines += ["    m_Ints: []","    m_Floats: []","    m_Colors: []"]
    return "\n".join(lines)+"\n"


def ptr(fid=2800000, guid=B, kind=3):
    return "{fileID: %s, guid: %s, type: %s}" % (fid,guid,kind)


class ExportTargetClassifierTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.assets=self.root/"Assets"
        self.assets.mkdir()
        self.write_material([ptr()])

    def write_material(self, refs):
        (self.assets/"m.mat").write_text(material(refs))
        (self.assets/"m.mat.meta").write_text("guid: "+A+"\nNativeFormatImporter:\n")

    def image(self, meta="TextureImporter:\n"):
        (self.assets/"tex.png").write_bytes(b"fixture")
        (self.assets/"tex.png.meta").write_text("guid: "+B+"\n"+meta)

    def test_valid_image(self):
        self.image()
        d=inspect(self.root)
        self.assertEqual(d["status"],"TARGET_TYPES_VALID")
        self.assertEqual(d["counts"]["valid_imported_image"],1)
        self.assertNotIn(B,str(d))
        self.assertNotIn("tex.png",str(d))

    def test_missing_target(self):
        d=inspect(self.root)
        self.assertEqual(d["counts"]["missing_target_guid"],1)
        self.assertEqual(d["external_texture_refs_invalid"],1)

    def test_wrong_fileid_separate_from_wrong_importer(self):
        self.image()
        self.write_material([ptr(123),ptr()])
        d=inspect(self.root)
        self.assertEqual(d["counts"]["imported_image_wrong_file_id"],1)
        self.assertEqual(d["counts"]["valid_imported_image"],1)
        (self.assets/"tex.png.meta").write_text("guid: "+B+"\nAudioImporter:\n")
        d=inspect(self.root)
        self.assertEqual(d["counts"]["imported_image_wrong_importer"],1)
        self.assertEqual(d["counts"]["imported_image_wrong_file_id"],1)

    def test_serialized_texture_class_fid_exact(self):
        (self.assets/"tex.asset").write_text("--- !u!28 &2800000\nTexture2D:\n")
        (self.assets/"tex.asset.meta").write_text("guid: "+B+"\nNativeFormatImporter:\n")
        d=inspect(self.root)
        self.assertEqual(d["counts"]["valid_serialized_texture_object"],1)
        self.write_material([ptr(2800001)])
        self.assertEqual(inspect(self.root)["counts"]["serialized_texture_subobject_missing"],1)

    def test_unsupported_format(self):
        (self.assets/"tex.wav").write_bytes(b"fixture")
        (self.assets/"tex.wav.meta").write_text("guid: "+B+"\nAudioImporter:\n")
        self.assertEqual(inspect(self.root)["counts"]["unsupported_texture_target_file_type"],1)

    def test_invalid_duplicate_guid_fails_before_scan(self):
        self.image()
        (self.assets/"duplicate.png").write_bytes(b"x")
        (self.assets/"duplicate.png.meta").write_text("guid: "+B+"\nTextureImporter:\n")
        with self.assertRaisesRegex(GuardError,"duplicate_or_reserved_meta_guid"):
            inspect(self.root)

    def test_null_and_builtin_ref_are_not_mislabeled_verified(self):
        self.write_material(["{fileID: 0}",
                             ptr(10302,"0000000000000000f000000000000000",0)])
        d=inspect(self.root)
        self.assertEqual(d["status"],"TARGET_TYPES_VALID")
        self.assertEqual(d["counts"]["null"],1)
        self.assertEqual(d["counts"]["built_in_unverified"],1)
        self.assertFalse(d["shader_program_or_device_pixels_verified"])


if __name__=="__main__":
    unittest.main()
