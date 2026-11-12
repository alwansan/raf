"""GT source BC3 array to true exported PNG flipbook color parity synthetic controls."""
import struct
import unittest
import json
import hashlib
import tempfile
from pathlib import Path

from scripts.gt_compare_original_bc3_to_flipbook_pixels import (
    dds_bc3,mip_range,evaluate,inspect,
)


def bc3_solid(rgb565):
    return bytes([255,255])+bytes(6)+struct.pack("<HHI",rgb565,rgb565,0)


class ExactBC3FlipbookParityTests(unittest.TestCase):
    def test_unambiguous_layer_major_compressed_source_images(self):
        from PIL import Image
        red=bc3_solid(0xF800)
        green=bc3_solid(0x07E0)
        raw=red+red+green+green  # layer0 mip0,mip1; layer1 mip0,mip1
        atlas=Image.new("RGBA",(8,4))
        atlas.paste(Image.new("RGBA",(4,4),(255,0,0,255)),(0,0))
        atlas.paste(Image.new("RGBA",(4,4),(0,255,0,255)),(4,0))
        original=evaluate(raw,atlas,2,2,4,4,2,"slice_major")
        guessed=evaluate(raw,atlas,2,2,4,4,2,"mip_major")
        self.assertEqual(original["exact_raw_orientation_match"],2)
        self.assertLess(guessed.get("exact_raw_orientation_match",0),2)

    def test_unambiguous_mip_major_compressed_source_images(self):
        from PIL import Image
        red=bc3_solid(0xF800)
        green=bc3_solid(0x07E0)
        raw=red+green+red+green
        atlas=Image.new("RGBA",(8,4))
        atlas.paste(Image.new("RGBA",(4,4),(255,0,0,255)),(0,0))
        atlas.paste(Image.new("RGBA",(4,4),(0,255,0,255)),(4,0))
        self.assertEqual(evaluate(raw,atlas,2,2,4,4,2,"mip_major")["exact_raw_orientation_match"],2)
        self.assertEqual(evaluate(raw,atlas,2,2,4,4,2,"slice_major").get("exact_raw_orientation_match",0),1)

    def test_raw_bc3_single_mip_cpu_decoder_never_invents_raw_bytes(self):
        actual=dds_bc3(bc3_solid(0xF800),4,4)
        self.assertEqual(actual.getpixel((0,0)),(255,0,0,255))
        self.assertEqual(actual.getpixel((3,3)),(255,0,0,255))
        with self.assertRaises(ValueError):
            dds_bc3(b"invalid",4,4)

    def test_actual_export_single_png_cell_cannot_claim_missing_original_array_layers(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            stage=root/"private"
            stage.mkdir()
            project=root/"ExportedProject"
            assets=project/"Assets"
            assets.mkdir(parents=True)
            records=[]
            red=bc3_solid(0xF800)
            green=bc3_solid(0x07E0)
            raw=red+red+green+green
            for i in range(9):
                guid=f"{i+100:032x}"
                image=assets/f"array-{i}.png"
                Image.new("RGBA",(4,4),(255,0,0,255)).save(image)
                (assets/f"array-{i}.png.meta").write_text(
                    f"guid: {guid}\\nTextureImporter:\\n  textureShape: 4\\n"
                    "  flipbookRows: 1\\n  flipbookColumns: 1\\n")
                if i==8:
                    data_path=None
                    stream_size=0
                    sha=None
                else:
                    data_path=f"array-{i}.original-gpu-bytes"
                    (stage/data_path).write_bytes(raw)
                    stream_size=len(raw)
                    sha=hashlib.sha256(raw).hexdigest()
                records.append({"target_export_guid":guid,
                    "target_fileID":18700000,"target_export_type":3,
                    "depth":2,"width":4,"height":4,"mipmap_count":2,
                    "source_format_enum":100,"relative_payload":data_path,
                    "sha256":sha,"payload_bytes":stream_size})
            (stage/"private-array-import-manifest.json").write_text(json.dumps({
                "schema":"GT_PRIVATE_ORIGINAL_ARRAY_IMPORT_INPUT_V1","arrays":records}))
            report=inspect(stage,project)
            count=report["counts"]
            self.assertEqual(report["original_arrays_with_pixels"],8)
            self.assertEqual(report["original_source_empty_pixel_arrays"],1)
            self.assertEqual(count["export_png_contains_one_source_layer_cell"],9)
            self.assertEqual(count["single_tile_pixel_probes_without_slice_order_proof"],8)
            self.assertEqual(report["original_BC3_layout_unambiguously_matched_array_count"],0)
            self.assertFalse(report["all_original_BC3_source_array_PNG_pixels_proven"])
            self.assertFalse(report["full_mip_chain_pixel_equivalence_proven"])
            self.assertEqual(report["sampled_original_source_layer0_mips_vs_PNG_cells"],8)
            self.assertNotIn(guid,json.dumps(report))
            self.assertNotIn("array-0.png",json.dumps(report))

    def test_mip_slice_range_formula_rejects_out_of_scope(self):
        self.assertEqual(mip_range(4,4,2,2,0,0,"slice_major"),(0,16))
        self.assertEqual(mip_range(4,4,2,2,1,0,"slice_major"),(32,16))
        self.assertEqual(mip_range(4,4,2,2,1,0,"mip_major"),(16,16))
        with self.assertRaises(Exception):
            mip_range(4,4,2,2,2,0,"slice_major")


if __name__=="__main__":
    unittest.main()
