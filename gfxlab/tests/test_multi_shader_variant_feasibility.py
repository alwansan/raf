import unittest
from gfxlab.tools.multi_shader_variant_feasibility import stage_inventory, inventory
class TestShaderVariants(unittest.TestCase):
    def test_variant_inventory_no_shader_claim(self):
        x=stage_inventory({"m_SubPrograms":[
          {"m_BlobIndex":2,"m_GlobalKeywords":["foo"],"m_Parameters":{}},
          {"m_BlobIndex":3}]})
        self.assertEqual(x["variant_count"],2)
        self.assertEqual(x["blob_indices_present"],2)
        self.assertEqual(x["keyword_metadata_variants"],1)
    def test_missing_variants_not_synthesized(self):
        self.assertEqual(stage_inventory({"m_SubPrograms":[]})["variant_count"],0)
        self.assertEqual(stage_inventory(None)["variant_count"],0)
        with self.assertRaises(ValueError):
            stage_inventory({"m_SubPrograms":[None]})
    def test_invalid_subshader_rejected(self):
        with self.assertRaises(ValueError):
            inventory({"m_ParsedForm":{"m_SubShaders":[{"m_Passes":None}]}})

    def test_unity2021_serialized_v3_player_subprogram_layout(self):
        x=stage_inventory({"m_SubPrograms":[],"m_PlayerSubPrograms":[
            {"m_SubPrograms":[{"m_BlobIndex":3,"m_GpuProgramType":16}]},
            [{"m_BlobIndex":4,"m_Keywords":["SAFE_NON_PRIVATE_TEST"]}]]})
        self.assertEqual(x["legacy_variant_count"],0)
        self.assertEqual(x["player_variant_count"],2)
        self.assertEqual(x["variant_count"],2)
        self.assertTrue(x["player_metadata_field_present"])
        self.assertEqual(x["blob_indices_present"],2)
