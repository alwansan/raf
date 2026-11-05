"""T3 exact same-export original Texture2D GUID to .meta classification tests."""
import tempfile
from pathlib import Path
import unittest
from scripts import t3_texture_importer_presence as p

class TextureImporterPresence(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.assets=Path(self.temp.name)/"Assets"
        self.assets.mkdir()
        self.guid="a"*32
    def trace(self, guid=None):
        return {"objects":[{"class_id":28,"export":{
            "file_id":2800000,"guid":guid or self.guid,"type":3}}]}
    def write(self, filename="image.png", guid=None, kind="TextureImporter",
              asset=True, bad_header=False):
        raw=self.assets/filename
        if asset:raw.write_bytes(b"FAKE_NOT_GAME")
        (self.assets/(filename+".meta")).write_text(
            "fileFormatVersion: 2\n"
            "guid: "+(guid or self.guid)+"\n"+
            ("guid: "+"b"*32+"\n" if bad_header else "")+
            kind+":\n  settings: {}\n",encoding="utf8")
    def observe(self, trace=None):
        return p.inventory(self.assets,trace or self.trace())
    def data(self,trace=None):
        return self.observe(trace)["matched_meta_GUID_categories"]
    def test_single_exact_real_texture_importer_tag(self):
        self.write()
        a=self.observe()
        self.assertEqual(a["selected_original_linked_Texture2D_trace_objects"],1)
        self.assertEqual(self.data()["found_TextureImporter"],1)
        self.assertFalse(a["original_sampler_sRGB_or_pixels_verified"])
    def test_no_meta_file_is_not_called_texture_importer(self):
        self.assertEqual(self.data()["export_target_GUID_absent_from_meta_files"],1)
    def test_native_format_importer_is_not_assumed_texture_importer(self):
        self.write(kind="NativeFormatImporter")
        a=self.data()
        self.assertEqual(a["found_NativeFormatImporter"],1)
        self.assertEqual(a["found_TextureImporter"],0)
    def test_default_importer_is_not_assumed_texture_importer(self):
        self.write(kind="DefaultImporter")
        self.assertEqual(self.data()["found_DefaultImporter"],1)
    def test_missing_exported_asset_not_ignored(self):
        self.write(asset=False)
        self.assertEqual(self.data()["target_meta_without_exported_asset"],1)
    def test_duplicate_meta_same_guid_is_not_unique(self):
        self.write("one.png")
        self.write("two.png")
        a=self.data()
        self.assertEqual(a["multiple_meta_files_claim_same_GUID"],1)
        self.assertEqual(a["found_TextureImporter"],0)
    def test_second_guid_in_one_meta_is_ambiguous(self):
        self.write(bad_header=True)
        self.assertEqual(self.data()["ambiguous_GUID_inside_target_meta"],1)
    def test_same_export_guid_shared_by_two_objects_is_reported(self):
        self.write()
        r=self.trace()
        r["objects"].append({"class_id":28,"export":{
            "file_id":2800001,"guid":self.guid,"type":3}})
        self.assertEqual(self.data(r)["source_Texture2D_objects_sharing_export_GUID"],2)
    def test_wrong_target_guid_cannot_appear_matched(self):
        self.write(guid="b"*32)
        self.assertEqual(self.data()["export_target_GUID_absent_from_meta_files"],1)
    def test_symlinked_export_target_rejected(self):
        outside=Path(self.temp.name)/"bad.data"
        outside.write_bytes(b"out")
        (self.assets/"link").symlink_to(outside)
        with self.assertRaisesRegex(ValueError,"unsafe_or_oversize"):
            self.observe()
    def test_invalid_trace_type_rejected(self):
        r=self.trace();r["objects"][0]["class_id"]=21
        with self.assertRaisesRegex(ValueError,"non_Texture2D"):
            self.observe(r)
    def test_missing_material_texture_target_trace_rejected(self):
        with self.assertRaisesRegex(ValueError,"no_original_selected"):
            self.observe({"objects":[]})
    def test_no_per_object_identity_or_guid_is_reported(self):
        self.write()
        s=str(self.observe())
        self.assertNotIn(self.guid,s)
        self.assertNotIn("image.png",s)
if __name__=="__main__":unittest.main()
