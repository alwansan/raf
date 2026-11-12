"""GT authentic source array → exported 2021 TextureImporter flipbook identity tests."""
import json
from pathlib import Path
import struct
import tempfile
import unittest

from scripts.gt_validate_texture2darray_flipbook import audit,index_exported_array_meta
from scripts.gt_stage_serialized_owners import InventoryError

DEPTHS=[2,5,5,6,6,6,6,8,8]


def fixture(folder, *, wrong_grid=False, bad_ihdr=False, wrong_shape=False):
    assets=folder/"Assets"
    assets.mkdir()
    originals={}
    trace={"schema_version":1,"export_instance":"f"*32,"objects":[]}
    for i,depth in enumerate(DEPTHS):
        key=("sharedassets0.assets",i+1)
        originals[key]={"width":1024,"height":1024,"depth":depth,
                         "original_stream_size":0 if i==0 else 1024}
        cols=depth if i<3 else depth//2
        rows=1 if i<3 else 2
        if wrong_grid and i==1:
            cols+=1
        guid=f"{i+101:032x}"
        png=assets/f"array-{i}.png"
        width,height=cols*1024,rows*1024
        header=(b"invalid PNG" if bad_ihdr and i==2 else
                b"\x89PNG\r\n\x1a\n"+struct.pack(">I",13)+b"IHDR"+
                struct.pack(">II",width,height))
        png.write_bytes(header)
        (assets/f"array-{i}.png.meta").write_text(
            f"guid: {guid}\nTextureImporter:\n  textureShape: "+
            ("1" if wrong_shape and i==3 else "4")+
            f"\n  flipbookRows: {rows}\n  flipbookColumns: {cols}\n")
        trace["objects"].append({
          "class_id":187,"source":{"owner":key[0],"path_id":key[1]},
          "export":{"file_id":18700000,"guid":guid,"type":3},
        })
    return originals,trace


class OriginalArrayFlipbookIdentityTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.original,self.trace=fixture(self.root)
        self.meta=index_exported_array_meta(self.root)

    def test_all_nine_array_source_metas_and_importer_grids_match(self):
        d=audit(self.original,self.trace,self.meta)
        self.assertEqual(d["status"],"NINE_SOURCE_ARRAY_FLIPBOOK_GEOMETRY_MATCH")
        self.assertEqual(d["counts"]["source_logical_layers_imported_as_flipbook"],52)
        self.assertEqual(d["counts"]["original_source_empty_pixel_array_flipbook_geometry"],1)
        self.assertEqual(d["counts"]["exact_array_class_GUID_flipbook_geometry_verified"],9)
        self.assertFalse(d["Unity_Editor_reimport_as_Texture2DArray_verified"])
        self.assertNotIn("sharedassets",json.dumps(d))
        self.assertNotIn(self.trace["objects"][0]["export"]["guid"],json.dumps(d))

    def test_wrong_source_layer_grid_is_rejected(self):
        meta=self.root/"Assets/array-1.png.meta"
        s=meta.read_text().replace("flipbookColumns: 5","flipbookColumns: 6")
        meta.write_text(s)
        d=audit(self.original,self.trace,index_exported_array_meta(self.root))
        self.assertFalse(d["all_array_sources_importer_grid_and_png_geometry_match"])
        self.assertEqual(d["counts"]["invalid_original_array_flipbook_grid"],1)

    def test_valid_full_png_atlas_with_wrong_importer_cells_reports_safe_repair_opportunity(self):
        meta=self.root/"Assets/array-1.png.meta"
        meta.write_text(meta.read_text().replace("flipbookColumns: 5","flipbookColumns: 2"))
        d=audit(self.original,self.trace,index_exported_array_meta(self.root))
        self.assertEqual(d["counts"]["PNG_has_all_original_layers_in_cell_grid"],9)
        self.assertEqual(d["counts"]["importer_grid_needs_source_verified_correction"],1)
        self.assertEqual(d["counts"]["flipbook_cell_count_disagrees_with_original_depth"],1)
        self.assertFalse(d["all_array_sources_importer_grid_and_png_geometry_match"])

    def test_single_cell_png_does_not_prove_complete_original_array_layers(self):
        import struct
        png=self.root/"Assets/array-1.png"
        data=bytearray(png.read_bytes())
        data[16:24]=struct.pack(">II",1024,1024)
        png.write_bytes(bytes(data))
        d=audit(self.original,self.trace,index_exported_array_meta(self.root))
        self.assertEqual(d["counts"]["export_PNG_only_one_source_sized_cell"],1)
        self.assertFalse(d["all_array_sources_importer_grid_and_png_geometry_match"])

    def test_wrong_array_target_native_fileID_is_rejected(self):
        self.trace["objects"][0]["export"]["file_id"]=2800000
        with self.assertRaisesRegex(InventoryError,"invalid_original_class187_export_pointer"):
            audit(self.original,self.trace,self.meta)

    def test_importer_2d_shape_is_rejected(self):
        meta=self.root/"Assets/array-3.png.meta"
        meta.write_text(meta.read_text().replace("textureShape: 4","textureShape: 1"))
        d=audit(self.original,self.trace,index_exported_array_meta(self.root))
        self.assertEqual(d["counts"]["wrong_importer_texture_shape"],1)
        self.assertFalse(d["all_array_sources_importer_grid_and_png_geometry_match"])

    def test_bad_or_truncated_png_header_fails_closed(self):
        (self.root/"Assets/array-2.png").write_bytes(b"not a real PNG")
        with self.assertRaisesRegex(InventoryError,"invalid_exported_array_PNG_IHDR"):
            audit(self.original,self.trace,index_exported_array_meta(self.root))

    def test_export_metadata_GUID_missing_not_accepted_as_array(self):
        self.trace["objects"][2]["export"]["guid"]="d"*32
        with self.assertRaisesRegex(InventoryError,"original_array_exported_meta_missing"):
            audit(self.original,self.trace,self.meta)


if __name__=="__main__":
    unittest.main()
