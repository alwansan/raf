"""Synthetic-only original DCL vs translated SPIR-V stage-family regressions."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from scripts import t3_particle108_dcl_spv_family_census as m

def reflected(*,ubos=1,textures=1,samplers=1,ssbos=0,images=0):
    def slots(n):
        return [[0,i] for i in range(n)]
    return {"inputs":[],"outputs":[],"resource_slots":{
        "ubos":slots(ubos),"ssbos":slots(ssbos),
        "textures":slots(textures),"separate_images":[],
        "separate_samplers":slots(samplers),"images":slots(images)}}

def fixture():
    return (
        ("cbuffer",89,(2,8)),
        ("srv",88,(3,)),
        ("sampler",90,(1,)),
    )

class PrivateStageFamilyTests(unittest.TestCase):
    def test_present_source_and_spirv_stage_family_counts(self):
        counts=m._stage_evidence(fixture(),reflected())
        self.assertEqual(counts["source_decl_cbuffer"],1)
        self.assertEqual(counts["source_decl_srv"],1)
        self.assertEqual(counts["source_decl_sampler"],1)
        self.assertEqual(counts["spv_reflected_ubos"],1)
        self.assertEqual(counts["dcl_cb_but_no_spv_ubo"],0)

    def test_original_declaration_without_spv_category_is_signal_not_bug_claim(self):
        counts=m._stage_evidence(fixture(),reflected(ubos=0,textures=0,samplers=0))
        self.assertEqual(counts["dcl_cb_but_no_spv_ubo"],1)
        self.assertEqual(counts["dcl_srv_but_no_spv_image_category"],1)
        self.assertEqual(counts["dcl_sampler_but_no_spv_sampler_category"],1)

    def test_unrelated_spv_cb_does_not_prove_source_mapping(self):
        counts=m._stage_evidence((("srv",88,(4,)),),reflected(ubos=1,textures=1))
        self.assertEqual(counts["spv_ubo_without_dcl_cb"],1)

    def test_combined_images_and_samplers_do_not_false_signal_missing(self):
        counts=m._stage_evidence(fixture(),reflected(ubos=1,textures=1,samplers=0))
        self.assertEqual(counts["dcl_sampler_but_no_spv_sampler_category"],0)

    def test_exact_same_stage_resource_counts_across_all_four_families(self):
        counts=m._stage_evidence(fixture(),reflected(ubos=1,textures=1,samplers=0))
        self.assertEqual(counts["stage_all_four_resource_family_cardinalities_equal"],1)
        for family in ("cbuffer","srv","sampler","uav"):
            self.assertEqual(counts["stage_"+family+"_cardinality_mismatch"],0)
            self.assertEqual(counts["stage_"+family+"_absolute_descriptor_count_delta"],0)

    def test_missing_one_resource_in_same_stage_does_not_hide_behind_presence(self):
        rows=fixture()+(("srv",88,(5,)),)
        counts=m._stage_evidence(rows,reflected(ubos=1,textures=1,samplers=1))
        self.assertEqual(counts["dcl_srv_but_no_spv_image_category"],0)
        self.assertEqual(counts["stage_srv_cardinality_equal"],0)
        self.assertEqual(counts["stage_srv_cardinality_mismatch"],1)
        self.assertEqual(counts["stage_srv_absolute_descriptor_count_delta"],1)
        self.assertEqual(counts["stage_all_four_resource_family_cardinalities_equal"],0)

    def test_cross_stage_counterbalancing_detected_despite_matching_total(self):
        from collections import Counter
        # Stage 1 has two original CBs, one translated UBO; stage 2 has
        # one original CB, two translated UBOs. Global totals both three.
        first=(("cbuffer",89,(2,8)),("cbuffer",89,(3,8)))
        second=(("cbuffer",89,(2,8)),)
        a=m._stage_evidence(first,reflected(ubos=1,textures=0,samplers=0))
        b=m._stage_evidence(second,reflected(ubos=2,textures=0,samplers=0))
        sum_counts=Counter(a)+Counter(b)
        self.assertEqual(sum_counts["source_decl_cbuffer"],3)
        self.assertEqual(sum_counts["spv_reflected_ubos"],3)
        self.assertEqual(sum_counts["stage_cbuffer_cardinality_mismatch"],2)
        self.assertEqual(sum_counts["stage_cbuffer_absolute_descriptor_count_delta"],2)
        self.assertEqual(sum_counts["stage_all_four_resource_family_cardinalities_equal"],0)

    def test_stage_cardinality_not_misreported_as_descriptor_register_provenance(self):
        pairs=[(b"\x01",b"\x00") for _ in range(4)]
        with tempfile.TemporaryDirectory() as d,patch.object(
                m.dx,"_private_stage_layout",return_value=fixture()):
            r=m.classify(pairs,Path(d),
                        translator=lambda _blob,stage,_dir:{
                            "stage":stage,"vulkan11_valid":True},
                        reflector=lambda _path:reflected())
        self.assertEqual(r["counts"]["stage_all_four_resource_family_cardinalities_equal"],8)
        self.assertFalse(r["original_to_SPIRV_descriptor_register_provenance_proven"])
        self.assertTrue(r["per_stage_family_count_equality_is_not_register_identity"])

    def test_duplicate_primary_source_register_rejected(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE_PRIVATE_PRIMARY_REGISTER"):
            m._stage_evidence(fixture()+(("cbuffer",89,(2,12)),),reflected())

    def test_malformed_source_register_shape_rejected(self):
        for layout in ((("srv",88,(-1,)),),(("srv",88,(3.5,)),),
                       (("srv",88,()),),(("cbuffer",89,(1,2,3)),)):
            with self.subTest(layout=layout),self.assertRaises(ValueError):
                m._stage_evidence(layout,reflected())

    def test_bad_spirv_duplicate_descriptor_rejected(self):
        bad=reflected()
        bad["resource_slots"]["ubos"]=[[0,0],[0,0]]
        with self.assertRaises(ValueError):
            m._stage_evidence(fixture(),bad)

    def test_four_keyword_stage_identity_kept_and_public_counts_only(self):
        calls=[]
        def fake_translate(code,stage,out):
            calls.append((code,stage,out.name))
            return {"stage":stage,"vulkan11_valid":True}
        def fake_reflect(path):
            self.assertEqual(path.name,"original.spv")
            return reflected()
        pairs=[(b"\x01",b"\x00") for _ in range(4)]
        with tempfile.TemporaryDirectory() as d,patch.object(
                m.dx,"_private_stage_layout",return_value=fixture()):
            result=m.classify(pairs,Path(d),translator=fake_translate,
                              reflector=fake_reflect)
        self.assertEqual(result["counts"]["exact_original_keyword_vs_fs_pairs_compared"],4)
        self.assertEqual(result["counts"]["exact_original_keyword_stage_programs_compared"],8)
        self.assertEqual(result["counts"]["source_decl_cbuffer"],8)
        self.assertEqual([stage for _,stage,_ in calls],[1,0]*4)
        self.assertFalse(result["original_to_SPIRV_descriptor_register_provenance_proven"])
        self.assertFalse(result["Unity_ShaderLab_or_device_pixels_verified"])
        for secret in ("variant-0-stage-1","register","-1"):
            if secret!="register":
                self.assertNotIn(secret,json.dumps(result))

    def test_translator_stage_mismatch_fails_closed(self):
        pairs=[(b"\x01",b"\x00") for _ in range(4)]
        with tempfile.TemporaryDirectory() as d,patch.object(
                m.dx,"_private_stage_layout",return_value=fixture()):
            with self.assertRaisesRegex(ValueError,"PRIVATE_STAGE_VULKAN_TRANSLATION"):
                m.classify(pairs,Path(d),
                           translator=lambda *_:{"stage":0,"vulkan11_valid":True},
                           reflector=lambda *_:reflected())

    def test_cannot_accept_wrong_original_pair_cardinality(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"INVALID_PRIVATE_FOUR_PAIR_SCOPE"):
                m.classify([(b"\x01",b"\x00")],Path(d))
