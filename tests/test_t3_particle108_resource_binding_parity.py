"""Synthetic-only 108-use original ParticleShader48 VS/FS SPIR-V descriptor tests."""
import copy
import json
import unittest

from scripts import t3_particle108_resource_binding_parity as t3


def reflect(stage, *,ubo=None,tex=None):
    return {
        "inputs":([{"location":0,"type":"vec4"}] if stage==0 else []),
        "outputs":([{"location":0,"type":"vec4"}] if stage==1 else []),
        "resource_slots":{
            "ubos":([list(ubo)] if ubo is not None else []),
            "textures":([list(tex)] if tex is not None else []),
        },
    }


def fixtures():
    return [
        {
            1:{"source":reflect(1,ubo=(0,0)), "roundtrip":reflect(1,ubo=(0,0))},
            0:{"source":reflect(0,tex=(0,1)), "roundtrip":reflect(0,tex=(0,1))},
        } for _ in range(4)
    ]


class OriginalResourceTests(unittest.TestCase):
    def test_four_original_stage_pairs_complete_resource_parity(self):
        inp=fixtures();before=copy.deepcopy(inp)
        r=t3.classify_stages(inp)
        self.assertEqual(inp,before)
        self.assertEqual(r["status"],t3.STATUS)
        self.assertEqual(r["counts"]["source_stage_reflections"],8)
        self.assertEqual(r["counts"]["roundtrip_stage_reflections"],8)
        self.assertEqual(r["counts"]["stage_full_resource_slot_parity"],8)
        self.assertEqual(r["counts"]["source_VSFS_keyword_pairs_linked"],4)
        self.assertEqual(r["counts"]["roundtrip_VSFS_keyword_pairs_linked"],4)
        self.assertEqual(r["counts"]["source_vertex_binding_layout_stable_across_four_keywords"],1)
        self.assertEqual(r["counts"]["source_full_pair_descriptor_layouts_distinct"],1)
        self.assertFalse(r["source_shader_replaced_or_Unity_Android_pixels_proven"])
        self.assertNotIn("[0, 1]",json.dumps(r))
    def test_resource_slot_relocation_even_same_count_is_drift(self):
        r=fixtures()
        r[0][0]["roundtrip"]["resource_slots"]["textures"]=[[0,3]]
        output=t3.classify_stages(r)["counts"]
        self.assertEqual(output["stage_full_resource_slot_parity"],7)
        self.assertEqual(output["stage_descriptor_slot_drift"],1)
        self.assertEqual(output["removed_descriptor_entries"],1)
        self.assertEqual(output["added_descriptor_entries"],1)
        self.assertEqual(output["descriptor_categories_with_count_drift"],0)
        self.assertEqual(output["descriptor_categories_with_slot_drift"],1)
    def test_stage_resource_count_loss_detected(self):
        r=fixtures()
        r[2][1]["roundtrip"]["resource_slots"]["ubos"]=[]
        output=t3.classify_stages(r)["counts"]
        self.assertEqual(output["descriptor_categories_with_count_drift"],1)
        self.assertEqual(output["removed_descriptor_entries"],1)
        self.assertEqual(output["stage_full_resource_slot_parity"],7)
    def test_shader_keyword_variant_resource_drift_is_counted_not_ignored(self):
        r=fixtures()
        r[3][0]["source"]["resource_slots"]["textures"]=[[0,2]]
        r[3][0]["roundtrip"]["resource_slots"]["textures"]=[[0,2]]
        output=t3.classify_stages(r)["counts"]
        self.assertEqual(output["stage_full_resource_slot_parity"],8)
        self.assertEqual(output["source_fragment_binding_layout_stable_across_four_keywords"],0)
        self.assertEqual(output["source_full_pair_descriptor_layouts_distinct"],2)
        self.assertEqual(output["roundtrip_full_pair_descriptor_layouts_distinct"],2)
    def test_actual_pair_shader_interface_drift_rejected(self):
        r=fixtures()
        r[0][0]["source"]["inputs"]=[{"location":0,"type":"vec3"}]
        with self.assertRaisesRegex(ValueError,"original_source_SPIRV_stage_IO_not_compatible"):
            t3.classify_stages(r)
    def test_roundtrip_pair_interface_drift_still_resource_comparable(self):
        r=fixtures()
        r[0][0]["roundtrip"]["inputs"]=[{"location":0,"type":"vec3"}]
        out=t3.classify_stages(r)["counts"]
        self.assertEqual(out["roundtrip_VSFS_keyword_pairs_linked"],3)
        self.assertEqual(out["stage_full_resource_slot_parity"],8)
    def test_duplicate_private_descriptor_is_never_accepted(self):
        r=reflect(1)
        r["resource_slots"]["textures"]=[[0,0],[0,0]]
        with self.assertRaisesRegex(ValueError,"duplicate_private_stage_resource_binding"):
            t3.canonical_resources(r)
    def test_unsupported_unlocated_or_bool_descriptor_rejected(self):
        for item in ([None,1],[True,0],[0,-1],[0,"3"],[0,4096],[],[0,1,2]):
            r=reflect(1)
            r["resource_slots"]["ubos"]=[item]
            with self.subTest(item=item),self.assertRaises(ValueError):
                t3.canonical_resources(r)
    def test_unknown_category_fails_closed(self):
        r=reflect(1)
        r["resource_slots"]["new_texture_kind"]=[[0,0]]
        with self.assertRaises(ValueError):
            t3.canonical_resources(r)
    def test_nonpositive_pair_count_rejected(self):
        for values in ([],fixtures()[:3],fixtures()+fixtures()[:1]):
            with self.assertRaises(ValueError):
                t3.classify_stages(values)
    def test_missing_stage_or_roundtrip_reflection_rejected(self):
        r=fixtures()
        del r[0][0]["roundtrip"]
        with self.assertRaisesRegex(ValueError,"incomplete_original_and_roundtrip"):
            t3.classify_stages(r)
        r=fixtures();del r[1][0]
        with self.assertRaisesRegex(ValueError,"invalid_original_particle108_four_pair_scope"):
            t3.classify_stages(r)
    def test_private_original_stage_bytes_never_accepted_as_public_reflection(self):
        r=fixtures()
        r[0][0]["source"]="PRIVATE-HLSL-SPIRV-BYTECODE"
        with self.assertRaises(ValueError):
            t3.classify_stages(r)
    def test_strict_source_no_phantom_descriptor_binding(self):
        r=reflect(0)
        self.assertEqual(sum(map(len,t3.canonical_resources(r).values())),0)
        for bad in ({"ubos":None},{"ubos":"MALFORMED"}):
            r=reflect(1);r["resource_slots"]=bad
            with self.assertRaises(ValueError):
                t3.canonical_resources(r)
    def test_actual_original_program_not_inferred_from_clean_resource_report(self):
        r=t3.classify_stages(fixtures())
        self.assertTrue(r["roundtrip_layout_parity_is_NOT_program_numeric_equivalence"])
        self.assertFalse(r["original_private_names_HLSL_DXBC_SPIRV_Guids_published"])
        self.assertFalse(r["original_source_descriptor_set_binding_numbers_published"])


if __name__=="__main__":
    unittest.main()
