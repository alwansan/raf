"""GT independently decode original 2D arrays, reject guessed mip/slice order."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import struct
import unittest
from PIL import Image

from scripts.gt_stage_serialized_owners import InventoryError
from scripts.gt_validate_bc3_array_slice_order import inspect,compare_frames


def solid(rgb565):
    return b"\xff\xff"+bytes(6)+struct.pack("<HHI",rgb565,rgb565,0)


class ArrayPixelFrame:
    type=SimpleNamespace(name="Texture2DArray")
    def __init__(self,idx):
        self.path_id=idx+1
    def read(self):
        return SimpleNamespace(images=[
            Image.new("RGBA",(4,4),(255,0,0,255)),
            Image.new("RGBA",(4,4),(0,255,0,255))
        ])


class OriginalArrayIndependentDecoderTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        self.source_root=self.root/"Raft_Data"
        self.source_root.mkdir()
        self.stage=self.root/"array-private"
        self.stage.mkdir()
        self.raw=solid(0xf800)*2+solid(0x07e0)*2
        self.original={}
        rows=[]
        for i in range(9):
            key=("sharedassets0.assets",i+1)
            self.original[key]={
                "width":4,"height":4,"depth":2,"source_mipmap_count":2,
                "source_format_enum":100,
                "original_stream_size":0 if i==8 else len(self.raw)}
            name=f"array-{i}.original-gpu-bytes" if i<8 else None
            if name:(self.stage/name).write_bytes(self.raw)
            rows.append({"depth":2,"width":4,"height":4,"mipmap_count":2,
                         "source_format_enum":100,"relative_payload":name,
                         "payload_bytes":0 if i==8 else len(self.raw),
                         "sha256":None if i==8 else hashlib.sha256(self.raw).hexdigest()})
        (self.stage/"private-array-import-manifest.json").write_text(json.dumps({
            "schema":"GT_PRIVATE_ORIGINAL_ARRAY_IMPORT_INPUT_V1","arrays":rows}))
        (self.source_root/"sharedassets0.assets").write_bytes(b"fake")
        self.loader=lambda path:SimpleNamespace(objects=[
            ArrayPixelFrame(i) for i in range(9)])

    def test_independent_UnityPy_layer_decodes_agree_with_full_original_slice_major_layout(self):
        r=inspect(self.source_root,self.original,self.stage,loader=self.loader)
        self.assertEqual(r["source_arrays_with_decoded_BC3_pixels"],8)
        self.assertEqual(r["original_zero_pixel_source_array_objects"],1)
        self.assertEqual(r["layout_selected_from_independent_UnityPy_source_decoder"],"slice_major")
        self.assertEqual(r["counts"]["original_source_array_slice_major_full_match"],8)
        self.assertEqual(r["counts"]["original_source_array_mip_major_full_match"],0)
        self.assertFalse(r["Android_GPU_pixel_colors_verified"])

    def test_unsupported_original_array_image_is_rejected_not_painted(self):
        def wrong_frames(path):
            class Invalid:
                type=SimpleNamespace(name="Texture2DArray")
                path_id=1
                def read(self):
                    return SimpleNamespace(images=[])
            return SimpleNamespace(objects=[Invalid()])
        with self.assertRaisesRegex(InventoryError,"layers_missing"):
            inspect(self.source_root,self.original,self.stage,loader=wrong_frames)

    def test_corrupted_original_private_BC3_data_sha256_rejected(self):
        (self.stage/"array-0.original-gpu-bytes").write_bytes(b"x"*len(self.raw))
        with self.assertRaisesRegex(InventoryError,"corrupt_original_array_BC3_private_stage"):
            inspect(self.source_root,self.original,self.stage,loader=self.loader)

    def test_wrong_source_pixel_order_is_not_given_false_positive(self):
        frames=[Image.new("RGBA",(4,4),(255,0,0,255)),
                Image.new("RGBA",(4,4),(0,255,0,255))]
        a=compare_frames(self.raw,frames,4,4,2,2)
        self.assertEqual(a["slice_major"]["exact_source_pixel_matches"],2)
        self.assertLess(a["mip_major"]["exact_source_pixel_matches"],2)


if __name__=="__main__":
    unittest.main()
