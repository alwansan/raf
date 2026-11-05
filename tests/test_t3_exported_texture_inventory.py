"""T3 output-wide TextureImporter/image GUID census: public synthetic fixtures."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from scripts import t3_exported_texture_inventory as m

class ExportOutputShape(unittest.TestCase):
    def setUp(self):
        self.tmp = TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.assets = self.root/"Assets"
        self.assets.mkdir()
        self.guid = "a"*32

    def trace(self, guid=None):
        return {"objects":[{"class_id":28,
                             "export":{"file_id":2800000,
                                       "guid":guid or self.guid,"type":3}}]}

    def write(self, name, kind="TextureImporter", guid=None, payload=b"abc"):
        file=self.assets/name
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_bytes(payload)
        Path(str(file)+".meta").write_text(
            "fileFormatVersion: 2\nguid: "+(guid or self.guid)+"\n"+
            kind+":\n  textureSettings: {}\n", encoding="utf8")

    def inspect(self, trace=None):
        return m.aggregate_output(self.assets, trace or self.trace())

    def test_no_image_and_no_meta_is_proven_only_bounded_empty(self):
        report=self.inspect()
        self.assertEqual(report["exact_source_linked_GUIDs_absent_from_meta"],1)
        self.assertEqual(report["bounded_export_texture_asset_assessment"],
                         "NO_TEXTURE_ASSET_FILES_IN_BOUNDED_EXPORT")
        self.assertFalse(report["real_Unity_editor_import_or_device_pixels_verified"])

    def test_true_guid_with_png_texture_importer(self):
        self.write("Textures/fake.png")
        r=self.inspect()
        self.assertEqual(r["exact_source_linked_GUIDs_present_once_in_meta"],1)
        self.assertEqual(r["all_output"]["image_file_candidates"],1)
        self.assertEqual(r["all_output"]["all_meta_TextureImporter"],1)
        self.assertEqual(r["bounded_export_texture_asset_assessment"],
                         "ALL_SELECTED_GUIDS_IN_EXPORT_META")

    def test_exported_texture_with_alternate_guid_is_not_same_source(self):
        self.write("Textures/fake.png",guid="b"*32)
        r=self.inspect()
        self.assertEqual(r["exact_source_linked_GUIDs_absent_from_meta"],1)
        self.assertEqual(r["all_output"]["all_meta_TextureImporter"],1)
        self.assertEqual(r["bounded_export_texture_asset_assessment"],
                         "TEXTURE_ASSETS_PRESENT_GUID_CORRESPONDENCE_UNPROVEN")

    def test_other_importer_and_zero_byte_image_not_counted_as_match(self):
        self.write("src.dds",kind="NativeFormatImporter",guid="c"*32,payload=b"")
        r=self.inspect()
        self.assertEqual(r["all_output"]["zero_byte_image_candidates"],1)
        self.assertEqual(r["all_output"]["all_meta_NativeFormatImporter"],1)
        self.assertEqual(r["exact_source_linked_GUIDs_present_once_in_meta"],0)

    def test_embedded_Texture2D_yaml_counts_without_png(self):
        (self.assets/"embedded.asset").write_bytes(
            b"%YAML 1.1\n--- !u!28 &2800000\nTexture2D:\n  m_Name: fake\n")
        r=self.inspect()
        self.assertEqual(r["all_output"]["embedded_Texture2D_YAML_documents"],1)
        self.assertEqual(r["bounded_export_texture_asset_assessment"],
                         "TEXTURE_ASSETS_PRESENT_GUID_CORRESPONDENCE_UNPROVEN")

    def test_duplicate_meta_guid_not_exact_unique_source(self):
        self.write("a.png")
        self.write("b.png")
        r=self.inspect()
        self.assertEqual(r["exact_source_linked_GUIDs_duplicate_meta"],1)
        self.assertEqual(r["all_output"]["duplicate_global_meta_GUIDs"],1)

    def test_malformed_metadata_guid_is_counted_but_not_accepted(self):
        self.write("a.png")
        (self.assets/"a.png.meta").write_text(
            "guid: "+"b"*32+"\nguid: "+self.guid+"\nTextureImporter:\n")
        r=self.inspect()
        self.assertEqual(r["all_output"]["metadata_invalid_GUID_cardinality"],1)
        self.assertEqual(r["exact_source_linked_GUIDs_absent_from_meta"],1)

    def test_symlinked_asset_refused_without_following(self):
        outside=self.root/"outside.txt"
        outside.write_text("not-an-image")
        (self.assets/"evil.png").symlink_to(outside)
        with self.assertRaisesRegex(ValueError,"linked_or_oversize"):
            self.inspect()

    def test_wrong_trace_class_refused(self):
        t=self.trace()
        t["objects"][0]["class_id"]=21
        with self.assertRaisesRegex(ValueError,"unexpected_selected_source_class"):
            self.inspect(t)

    def test_trace_unknown_type_and_duplicate_guid_refused(self):
        trace=self.trace()
        trace["objects"][0]["export"]["type"]=42
        with self.assertRaisesRegex(ValueError,"invalid_original_exported"):
            self.inspect(trace)
        trace=self.trace()
        trace["objects"].append(trace["objects"][0].copy())
        with self.assertRaisesRegex(ValueError,"share_export_GUID"):
            self.inspect(trace)

    def test_report_never_contains_original_guid_or_asset_name(self):
        self.write("PrivateName.png")
        r=str(self.inspect())
        self.assertNotIn(self.guid,r)
        self.assertNotIn("PrivateName",r)
        self.assertFalse(self.inspect()["game_original_assets_modified"])

if __name__ == "__main__":
    unittest.main()
