"""GT fail-closed source-authentic Texture2DArray flipbook metadata correction tests.

All images/refs are synthetic and do not contain original game imagery.
"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from PIL import Image

from scripts.gt_repair_array_flipbook_importers import execute
from scripts.gt_stage_serialized_owners import InventoryError
from scripts.gt_validate_texture2darray_flipbook import audit,index_exported_array_meta


class SourceArrayImporterRepairTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.project=self.root/"ExportedProject"
        self.assets=self.project/"Assets"
        self.assets.mkdir(parents=True)
        self.backup=self.root/"protected_originals"
        self.source={}
        self.trace={"schema_version":1,"export_instance":"a"*32,"objects":[]}
        self.original_images={}
        for i in range(9):
            key=("sharedassets0.assets",i+1)
            self.source[key]={"width":4,"height":4,"depth":2,
                              "original_stream_size":32}
            guid=f"{i+100:032x}"
            img=self.assets/f"array-{i}.png"
            Image.new("RGBA",(8,4),(40+i,50+i,60+i,255)).save(img)
            self.original_images[img.name]=img.read_bytes()
            (self.assets/(img.name+".meta")).write_text(
                f"fileFormatVersion: 2\nguid: {guid}\n"
                "TextureImporter:\n  textureShape: 4\n"
                "  flipbookRows: 0\n  flipbookColumns: 0\n")
            self.trace["objects"].append({
                "class_id":187,
                "source":{"owner":key[0],"path_id":key[1]},
                "export":{"file_id":18700000,"guid":guid,"type":3},
            })

    def test_fix_nine_original_source_importers_and_preserve_all_guids_and_images(self):
        result=execute(self.project,self.backup,self.source,self.trace)
        self.assertEqual(result["status"],"ALL_NINE_ARRAY_IMPORTERS_VALID")
        self.assertEqual(result["original_importer_repair_candidates_applied"],9)
        self.assertTrue(result["all_nine_original_array_importers_accepted"])
        self.assertEqual(result["postrepair_exact_original_layer_grids_validated"],9)
        self.assertFalse(result["Unity_Editor_actual_import_execution_verified"])
        for i in range(9):
            image=self.assets/f"array-{i}.png"
            meta=(self.assets/f"array-{i}.png.meta").read_text()
            self.assertEqual(self.original_images[image.name],image.read_bytes())
            self.assertIn("flipbookRows: 1",meta)
            self.assertIn("flipbookColumns: 2",meta)
            self.assertIn(f"guid: {i+100:032x}",meta)
            private_backup=self.backup/"Assets"/f"array-{i}.png.meta"
            self.assertIn("flipbookRows: 0",private_backup.read_text())
        self.assertNotIn(self.trace["objects"][0]["export"]["guid"],json.dumps(result))

    def test_missing_source_layers_in_png_are_not_fabricated_or_meta_fixed(self):
        img=self.assets/"array-0.png"
        Image.new("RGBA",(4,4),(40,50,60,255)).save(img)
        result=execute(self.project,self.backup,self.source,self.trace)
        self.assertEqual(result["original_importer_repair_candidates_applied"],8)
        self.assertEqual(result["counts"]["export_png_lacks_full_original_array_slices"],1)
        self.assertFalse(result["all_nine_original_array_importers_accepted"])
        self.assertIn("flipbookRows: 0",
                      (self.assets/"array-0.png.meta").read_text())
        self.assertEqual(result["postrepair_exact_original_layer_grids_validated"],8)

    def test_correct_source_importer_meta_noop_keeps_export_bytes_unchanged(self):
        for i in range(9):
            path=self.assets/f"array-{i}.png.meta"
            path.write_text(path.read_text().replace("Rows: 0","Rows: 1").replace("Columns: 0","Columns: 2"))
        result=execute(self.project,self.backup,self.source,self.trace)
        self.assertEqual(result["original_importer_repair_candidates_applied"],0)
        self.assertEqual(result["postrepair_exact_original_layer_grids_validated"],9)
        self.assertFalse(self.backup.exists())

    def test_extra_meta_GUID_swap_is_rejected_before_mutations(self):
        (self.assets/"array-0.png.meta").write_text(
            (self.assets/"array-0.png.meta").read_text().replace(
                f"guid: {100:032x}",f"guid: {999:032x}"))
        with self.assertRaisesRegex(InventoryError,"original_array_GUID_missing_from_export"):
            execute(self.project,self.backup,self.source,self.trace)
        self.assertFalse(self.backup.exists())

    def test_wrong_importer_shape_refused_before_edits(self):
        meta=self.assets/"array-3.png.meta"
        meta.write_text(meta.read_text().replace("textureShape: 4","textureShape: 1"))
        with self.assertRaisesRegex(InventoryError,"importer_missing_exact_array_shape_or_grid_fields"):
            execute(self.project,self.backup,self.source,self.trace)
        self.assertFalse(self.backup.exists())

    def test_preexisting_backup_refused(self):
        self.backup.mkdir()
        with self.assertRaisesRegex(InventoryError,"unsafe_disposable_Unity_array_repair_project_or_backup"):
            execute(self.project,self.backup,self.source,self.trace)


if __name__=="__main__":
    unittest.main()
