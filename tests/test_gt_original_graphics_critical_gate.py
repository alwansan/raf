"""GT source-only fail-closed original 9/28/416/50 texture parity evidence acceptance."""
import copy
import unittest
from scripts.gt_original_graphics_critical_gate import gate
from scripts.gt_stage_serialized_owners import InventoryError


class OriginalGraphicsCriticalGateTests(unittest.TestCase):
    def setUp(self):
        self.arrays={
            "status":"ALL_28_ORIGINAL_ARRAY_MATERIAL_REFS_MATCH_REPAIRED_IMPORTERS",
            "original_array_objects_SHA256_authenticated":9,
            "exact_original_class187_array_material_refs":28,
            "distinct_source_array_guids_referenced_by_materials":9,
            "source_zero_pixel_original_array_refs":20,
            "full_array_material_importer_links_verified":True,
            "original_array_export_importer_guids_preserved":True,
            "original_source_game_assets_changed":False,
            "Android_runtime_pixels_verified":False,
        }
        self.external={
            "status":"EXTERNAL_TEXTURE_SOURCE_EXPORT_LINKS_CLASSIFIED",
            "authenticated_owner_tables":82,
            "original_external_texture_slots":416,
            "exact_cross_owner_source_export_texture_links":416,
            "external_links_not_yet_proven":0,
            "mismatched_source_to_export_external_links":0,
            "all_external_links_verified":True,
            "source_or_exported_assets_modified":False,
            "Unity_Editor_or_Android_GPU_pixels_verified":False,
        }
        self.bc3={
            "original_source_populated_layers_expected":50,
            "sampled_original_source_layer0_mips_vs_PNG_cells":50,
            "original_arrays_with_pixels":8,
            "original_source_empty_pixel_arrays":1,
            "all_original_BC3_source_array_PNG_pixels_proven":True,
            "full_original_top_mip_layer_pixel_comparison_requested":True,
            "all_populated_original_BC3_top_mip_layers_match_exported_PNG":True,
            "full_mip_chain_pixel_equivalence_proven":False,
            "Unity_Android_GPU_pixels_verified":False,
            "counts":{
                "slice_major_exact_samples":50,
                "real_source_array_payloads_compared":8,
                "source_zero_pixel_arrays":1,
                "export_png_contains_all_source_layer_cells":9,
                "unambiguous_original_BC3_slice_layout_slice_major":8,
            },
        }

    def test_exact_original_source_receipts_accept_without_android_claim(self):
        result=gate(self.arrays,self.external,self.bc3)
        self.assertEqual(result["status"],"SOURCE_BC3_AND_TEXTURE_CROSS_OWNER_PARITY_VERIFIED")
        self.assertEqual(result["exact_original_external_material_Texture_PPtrs"],416)
        self.assertEqual(result["all_original_source_BC3_top_mip_layers_exact"],50)
        self.assertFalse(result["Unity_Editor_or_Android_Adreno_GPU_proven"])

    def test_external_source_reference_loss_never_green(self):
        self.external["exact_cross_owner_source_export_texture_links"]=415
        with self.assertRaisesRegex(InventoryError,"failed_original_external_texture"):
            gate(self.arrays,self.external,self.bc3)

    def test_disclosed_unverified_gpu_flags_never_green(self):
        self.bc3["Unity_Android_GPU_pixels_verified"]=True
        with self.assertRaisesRegex(InventoryError,"failed_original_original_BC3"):
            gate(self.arrays,self.external,self.bc3)

    def test_material_original_class187_drift_never_green(self):
        self.arrays["exact_original_class187_array_material_refs"]=27
        with self.assertRaisesRegex(InventoryError,"failed_original_array_material"):
            gate(self.arrays,self.external,self.bc3)

    def test_unsampled_BC3_slices_never_green(self):
        self.bc3["sampled_original_source_layer0_mips_vs_PNG_cells"]=24
        with self.assertRaisesRegex(InventoryError,"failed_original_original_BC3"):
            gate(self.arrays,self.external,self.bc3)

    def test_zero_source_pixel_array_does_not_gain_faked_pixels(self):
        self.bc3["original_source_empty_pixel_arrays"]=0
        with self.assertRaisesRegex(InventoryError,"failed_original_original_BC3"):
            gate(self.arrays,self.external,self.bc3)

    def test_strict_type_boolean_not_accepted_as_integer(self):
        self.external["exact_cross_owner_source_export_texture_links"]=True
        with self.assertRaisesRegex(InventoryError,"failed_original_external_texture"):
            gate(self.arrays,self.external,self.bc3)


if __name__=="__main__":
    unittest.main()
