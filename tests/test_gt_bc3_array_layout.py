"""GT immutable Unity BC3 array-byte geometry tests and original empty-layer fidelity."""
import unittest

from scripts.gt_stage_serialized_owners import InventoryError
from scripts.gt_bc3_array_layout import mip_bytes,array_payload_bytes,original_layout_report


def sample():
    depths=[2,5,5,6,6,6,6,8,8]
    arrays={}
    for idx,depth in enumerate(depths):
        fmt=100 if idx<5 else 101
        arrays[idx]={
            "width":1024,"height":1024,"depth":depth,
            "source_format_enum":fmt,"source_mipmap_count":11,
            "original_stream_size":0 if idx==0 else
                array_payload_bytes(1024,1024,depth,11,fmt),
        }
    return arrays


class BC3ArrayByteExtentTest(unittest.TestCase):
    def test_expected_bc3_blocks_and_single_layer_mipchain(self):
        self.assertEqual(mip_bytes(4,4,0),16)
        self.assertEqual(mip_bytes(1,1,0),16)
        self.assertEqual(mip_bytes(1024,1024,0),1024*1024)
        self.assertEqual(array_payload_bytes(1024,1024,1,11,100),1398128)
        self.assertEqual(array_payload_bytes(1024,1024,1,11,101),1398128)

    def test_reconstruct_exact_fifty_payload_layers_without_fabricating_other_two(self):
        d=original_layout_report(sample())
        self.assertEqual(d["source_arrays"],9)
        self.assertEqual(d["source_total_logical_layers"],52)
        self.assertEqual(d["source_layers_with_original_stream_bytes"],50)
        self.assertEqual(d["source_layers_without_original_stream_bytes"],2)
        self.assertEqual(d["original_GPU_compressed_BC3_stream_bytes"],69906400)
        self.assertEqual(d["bytes_if_every_original_array_layer_had_payload"],72702656)
        self.assertFalse(d["source_array_layer_and_mip_order_proven"])
        self.assertFalse(d["Android_transcode_and_device_pixels_verified"])

    def test_single_bad_stream_size_cannot_silently_pass_even_if_total_matches(self):
        x=sample()
        x[1]["original_stream_size"]+=16
        x[2]["original_stream_size"]-=16
        with self.assertRaisesRegex(InventoryError,"full_mipmap_byte_extent_mismatch"):
            original_layout_report(x)

    def test_unknown_source_graphics_format_cannot_be_decoded_as_dxt5(self):
        x=sample()
        x[3]["source_format_enum"]=25
        with self.assertRaisesRegex(InventoryError,"unsupported_original_array_GraphicsFormat"):
            original_layout_report(x)

    def test_source_mip_dimensions_out_of_range(self):
        with self.assertRaisesRegex(InventoryError,"excessive_mip_count"):
            array_payload_bytes(1024,1024,4,13,100)

    def test_wrong_array_count_rejected(self):
        x=sample()
        del x[0]
        with self.assertRaisesRegex(InventoryError,"expected_nine_original_texture_arrays"):
            original_layout_report(x)

    def test_no_negative_or_zero_dimension_can_claim_valid_bc3(self):
        for invalid in (0,-1,16385):
            with self.assertRaises(InventoryError):
                array_payload_bytes(invalid,1024,5,11,100)


if __name__=="__main__":
    unittest.main()
