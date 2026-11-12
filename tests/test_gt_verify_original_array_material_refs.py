"""GT original nine array Material reference closure, with actual repaired importer grids."""
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from PIL import Image
from scripts.gt_repair_array_flipbook_importers import execute
from scripts.gt_verify_original_array_material_refs import check


class AuthenticArrayMaterialRefsTests(unittest.TestCase):
    def setUp(self):
        self.temp=TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.project=self.root/"ExportedProject"
        self.assets=self.project/"Assets"
        self.assets.mkdir(parents=True)
        self.source={}
        self.trace={"schema_version":1,"export_instance":"a"*32,"objects":[]}
        self.links=[]
        for idx in range(9):
            key=("sharedassets0.assets",idx+1)
            self.source[key]={"width":4,"height":4,"depth":2,
                              "original_stream_size":0 if idx==8 else 32}
            guid=f"{idx+100:032x}"
            Image.new("RGBA",(8,4),(50,60,70,255)).save(self.assets/f"array-{idx}.png")
            (self.assets/f"array-{idx}.png.meta").write_text(
                f"guid: {guid}\nTextureImporter:\n"
                "  textureShape: 4\n  flipbookRows: 0\n  flipbookColumns: 0\n")
            self.trace["objects"].append({
                "class_id":187,
                "source":{"owner":key[0],"path_id":key[1]},
                "export":{"file_id":18700000,"guid":guid,"type":3},
            })
        self.links=[f"{i%9+100:032x}" for i in range(28)]
        self.write_mat()

    def write_mat(self):
        body="%YAML 1.1\n%TAG !u! tag:unity3d.com,2011:\n--- !u!21 &2100000\nMaterial:\n  m_SavedProperties:\n    m_TexEnvs:\n"
        for i,g in enumerate(self.links):
            body+=f"    - _Array{i}:\n        m_Texture: {{fileID: 18700000, guid: {g}, type: 3}}\n        m_Scale: {{x: 1, y: 1}}\n        m_Offset: {{x: 0, y: 0}}\n"
        body+="    m_Ints: []\n"
        (self.assets/"material.mat").write_text(body)
        (self.assets/"material.mat.meta").write_text("guid: "+"a"*32+"\nNativeFormatImporter:\n")

    def test_exact_28_class187_links_after_nine_source_grid_repairs(self):
        before=check(self.project,self.source,self.trace)
        self.assertFalse(before["full_array_material_importer_links_verified"])
        execute(self.project,self.root/"backup",self.source,self.trace)
        after=check(self.project,self.source,self.trace)
        self.assertTrue(after["full_array_material_importer_links_verified"])
        self.assertEqual(after["total_original_array_derived_material_refs"],28)
        self.assertEqual(after["distinct_source_array_guids_referenced_by_materials"],9)
        self.assertEqual(after["exact_original_class187_array_material_refs"],28)
        self.assertEqual(after["source_zero_pixel_original_array_refs"],3)
        self.assertFalse(after["source_zero_pixel_array_runtime_generated_content_verified"])
        self.assertFalse(after["Unity_Editor_texture_array_imported_asset_class_verified"])

    def test_array_ref_converted_to_texture2d_does_not_pass(self):
        execute(self.project,self.root/"backup",self.source,self.trace)
        mat=self.assets/"material.mat"
        mat.write_text(mat.read_text().replace("fileID: 18700000","fileID: 2800000",1))
        after=check(self.project,self.source,self.trace)
        self.assertEqual(after["counts"]["wrong_original_class187_importer_pointer"],1)
        self.assertFalse(after["full_array_material_importer_links_verified"])

    def test_exact_number_of_original_array_references_is_not_guessed(self):
        execute(self.project,self.root/"backup",self.source,self.trace)
        self.links.pop()
        self.write_mat()
        after=check(self.project,self.source,self.trace)
        self.assertEqual(after["total_original_array_derived_material_refs"],27)
        self.assertFalse(after["full_array_material_importer_links_verified"])


if __name__=="__main__":
    unittest.main()
