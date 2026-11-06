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
                        reflector=lambda _path:reflected(ubos=1,textures=1,samplers=0))
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


class SpirvNamedCandidatesSynthetic(unittest.TestCase):
    """Binary SPV fixtures are synthetic grammar probes, not original Raft code."""

    @staticmethod
    def build(*, names=("cb2","t3","s1"), bindings=(0,1,2),
              omissions=(), duplicate_dec=False, wrong_family=False,
              stage_model=0, spoof_extra=False, second_binding_collision=False,
              array_texture=False):
        import struct
        from scripts import t3_particle108_spirv_opname_candidates as probe
        def op(code,*payload):
            return [(len(payload)+1)<<16 | code,*payload]
        def spv_str(value):
            encoded=value.encode("utf-8")+b"\0"
            encoded+=b"\0"*((4-len(encoded)%4)%4)
            return list(struct.unpack("<"+"I"*(len(encoded)//4),encoded))
        instructions=[]
        instructions+=op(15,stage_model,2,*spv_str("main"))
        instructions+=op(30,10)   # struct -> uniform CB
        instructions+=op(25,11,40,1,0,0,0,1,0) # sampled image
        instructions+=op(26,12)   # separate sampler
        if array_texture:
            instructions+=op(28,13,11,42)
        instructions+=op(32,20,2,10) # pointer Uniform/CB
        instructions+=op(32,21,0,13 if array_texture else 11)
        instructions+=op(32,22,0,12)
        instructions+=op(59,20,30,2)
        instructions+=op(59,21 if not wrong_family else 22,31,0)
        instructions+=op(59,22,32,0)
        for i,(name,binding) in enumerate(zip(names,bindings)):
            vid=30+i
            if i not in omissions:
                instructions+=op(5,vid,*spv_str(name))
            instructions+=op(71,vid,34,0) # DescriptorSet
            instructions+=op(71,vid,33,bindings[0] if
                            second_binding_collision and i==1 else binding)
            if duplicate_dec and i==0:
                instructions+=op(71,vid,33,binding)
        if spoof_extra:
            instructions+=op(59,21,33,0)
            instructions+=op(5,33,*spv_str("t9"))
            instructions+=op(71,33,34,0)
            instructions+=op(71,33,33,9)
        words=[probe.SPV_MAGIC,0x00010300,0,256,0]+instructions
        return struct.pack("<"+"I"*len(words),*words)

    def summary(self, **kwargs):
        from scripts import t3_particle108_spirv_opname_candidates as probe
        return probe.candidate_counts(fixture(),self.build(**kwargs),1)

    def test_exact_debug_names_are_candidate_only_not_register_proof(self):
        report=self.summary()
        self.assertEqual(report["spirv_debug_candidates_matching_original_source_name_keys"],3)
        self.assertEqual(report["original_source_dcl_without_typed_debug_candidate"],0)
        self.assertTrue(report["all_original_resource_names_have_debug_candidates"])
        self.assertFalse(report["original_to_SPIRV_register_provenance_proven"])
        self.assertTrue(report["debug_names_are_not_authoritative_binding_provenance"])
        for private in ('"cb2"','"t3"','"s1"',"private.hlsl"):
            self.assertNotIn(private,json.dumps(report))

    def test_missing_debug_name_not_treated_as_proven(self):
        r=self.summary(omissions=(1,))
        self.assertEqual(r["original_source_dcl_without_typed_debug_candidate"],1)
        self.assertFalse(r["all_original_resource_names_have_debug_candidates"])

    def test_forged_debug_name_cannot_be_authoritative(self):
        r=self.summary(names=("cb2","t9","s1"))
        self.assertEqual(r["spirv_named_candidate_not_in_source_dcl"],1)
        self.assertEqual(r["original_source_dcl_without_typed_debug_candidate"],1)
        self.assertFalse(r["original_to_SPIRV_register_provenance_proven"])

    def test_duplicate_binding_target_not_a_unique_correspondence(self):
        r=self.summary(second_binding_collision=True)
        self.assertEqual(r["duplicate_candidate_descriptor_targets"],1)
        self.assertFalse(r["all_original_resource_names_have_debug_candidates"])

    def test_sampler_named_texture_is_wrong_type(self):
        r=self.summary(wrong_family=True)
        self.assertEqual(r["spirv_debug_named_family_or_type_unsupported"],1)
        self.assertEqual(r["original_source_dcl_without_typed_debug_candidate"],1)

    def test_array_descriptor_stays_unsupported_without_span_metadata(self):
        r=self.summary(array_texture=True)
        self.assertEqual(r["spirv_debug_named_family_or_type_unsupported"],1)
        self.assertFalse(r["all_original_resource_names_have_debug_candidates"])

    def test_extra_spv_debug_resource_is_not_source_contract(self):
        r=self.summary(spoof_extra=True)
        self.assertEqual(r["spirv_named_candidate_not_in_source_dcl"],1)
        self.assertFalse(r["all_original_resource_names_have_debug_candidates"])

    def test_duplicate_descriptor_decoration_fails_closed(self):
        from scripts import t3_particle108_spirv_opname_candidates as probe
        with self.assertRaisesRegex(ValueError,"T3_SPIRV_DUPLICATE_DECORATION"):
            self.summary(duplicate_dec=True)

    def test_spv_entrypoint_wrong_stage_rejected(self):
        with self.assertRaisesRegex(ValueError,"T3_SPIRV_STAGE_ENTRYPOINT"):
            self.summary(stage_model=4)

    def test_truncated_spirv_instruction_rejected(self):
        from scripts import t3_particle108_spirv_opname_candidates as probe
        corrupted=self.build()[:-4]
        with self.assertRaisesRegex(ValueError,"T3_SPIRV_INSTRUCTION_BOUNDS"):
            probe.candidate_counts(fixture(),corrupted,1)

    def test_spirv_header_version_reads_minor_from_correct_bits(self):
        import struct
        from scripts import t3_particle108_spirv_opname_candidates as probe
        original=self.build()
        self.assertEqual(probe.candidate_counts(fixture(),original,1)
                         ["spirv_debug_name_resource_candidates"],3)
        # Minor 7 is not supported by the bounded SPV1.6 parser.
        future=bytearray(original)
        struct.pack_into("<I",future,4,0x00010700)
        with self.assertRaisesRegex(ValueError,"T3_SPIRV_HEADER"):
            probe.candidate_counts(fixture(),bytes(future),1)

    def test_malformed_dxbc_primary_register_rejected(self):
        from scripts import t3_particle108_spirv_opname_candidates as probe
        with self.assertRaisesRegex(ValueError,"T3_DX_SOURCE_PRIMARY_COLLISION"):
            probe.candidate_counts(fixture()+(("cbuffer",89,(2,10)),),
                                   self.build(),1)
