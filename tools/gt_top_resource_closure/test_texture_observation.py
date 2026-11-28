from pathlib import Path
import tempfile
import unittest
from PIL import Image
from tools.gt_top_resource_closure import stage, texture_observation as o
from scripts.gt_particle108_source_pixel_parity import compare_pixels

ROOT = Path(__file__).resolve().parents[2]

class TextureObservationTests(unittest.TestCase):
    def test_capture_serializes_actual_texture_class(self):
        result = stage.render((ROOT/"android-port/Experiments/ExportLineage/RaftExportLineage.cs").read_bytes()).decode()
        self.assertNotIn('json.WriteNumber("class_id", 28);', result)
        self.assertIn("asset.ClassID is not (28 or 84 or 89 or 117 or 187)", result)
        self.assertIn('json.WriteNumber("class_id", asset.ClassID);', result)

    def test_source_declared_unpack_and_wrong_channel(self):
        source = Image.new("RGBA", (1,1), (17,128,200,255))
        correct = Image.new("RGBA", (1,1), (255,128,127,17))
        tree = dict(m_TextureFormat=12,m_ColorSpace=0,m_LightmapFormat=3)
        obs = o.semantic_observation(tree,source,correct,compare_pixels(source,correct))
        self.assertFalse(obs["raw_RGBA_match"])
        self.assertTrue(obs["source_declared_transform_match"])
        wrong = Image.new("RGBA", (1,1), (255,128,127,18))
        self.assertFalse(o.semantic_observation(tree,source,wrong,compare_pixels(source,wrong))["source_declared_transform_match"])
        tree["m_LightmapFormat"]=0
        self.assertFalse(o.semantic_observation(tree,source,correct,compare_pixels(source,correct))["source_declared_transform_tested"])

    def test_array_source_distinguishes_unknown_and_empty(self):
        tree=dict(m_Width=2,m_Height=3,m_Depth=2,m_MipCount=1,m_Format=100,
                  m_StreamData={"size":0},m_ImageData=[])
        self.assertTrue(o.array_source(tree)["explicit_empty_stream_and_inline"])
        del tree["m_ImageData"]
        self.assertTrue(o.array_source(tree)["payload_presence_unknown"])
        self.assertFalse(o.array_source(tree)["explicit_empty_stream_and_inline"])

    def test_array_grid_and_wrong_file_id(self):
        with tempfile.TemporaryDirectory() as d:
            path=Path(d)/"array.png"
            Image.new("RGBA",(4,3)).save(path)
            source={"width":2,"height":3,"depth":2}
            meta="TextureImporter:\n  textureShape: 4\n  flipbookRows: 1\n  flipbookColumns: 2\n"
            obs=o.array_png_observation(source,path,meta,18700000,3)
            self.assertTrue(obs["importer_grid_matches"])
            self.assertFalse(obs["layer_pixel_values_verified"])
            self.assertFalse(o.array_png_observation(source,path,meta.replace("Columns: 2","Columns: 1"),18700000,3)["importer_grid_matches"])
            with self.assertRaisesRegex(ValueError,"wrong_importer_fileID"):
                o.array_png_observation(source,path,meta,2800000,3)

if __name__=="__main__":
    unittest.main()
