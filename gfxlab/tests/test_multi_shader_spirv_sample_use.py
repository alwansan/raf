"""Pure synthetic GFX046 strict SPIR-V sampled-image pairing; no Raft source data."""
import unittest
from gfxlab.tools.multi_shader_spirv_sample_use import resource_variable_ids,spv_sample_use
T={2,4}
S={1,9}
def refl(r, id, name):
    return {"id":id,"name":name,"binding":r}

class TestSourceAuthenticatedPairs(unittest.TestCase):
    def test_private_reflection_names_must_match_source_slots_not_binding(self):
        images=resource_variable_ids(T,[refl(61,10,"t2"),refl(62,11,"t4")],"resource")
        samp=resource_variable_ids(S,[refl(73,12,"s1"),refl(74,13,"s9")],"sampler")
        self.assertEqual(len(images),2)
        self.assertEqual(len(samp),2)
        with self.assertRaisesRegex(ValueError,"INCOMPLETE"):
            resource_variable_ids(T,[refl(61,10,"t2")],"resource")
        with self.assertRaisesRegex(ValueError,"OUTSIDE_SOURCE"):
            resource_variable_ids(T,[refl(61,10,"t7"),refl(62,11,"t4")],"resource")

    def test_direct_pair_real_sample_and_non_sampler_fetch(self):
        dis=b"""
          %10 = OpVariable %ptr UniformConstant
          %12 = OpVariable %ptr UniformConstant
          %20 = OpLoad %image %10
          %22 = OpLoad %sampler %12
          %30 = OpSampledImage %sampled %20 %22
          %33 = OpImageSampleImplicitLod %v4 %30 %uv
          %35 = OpImageSampleExplicitLod %v4 %30 %uv Lod %level
          %40 = OpImageFetch %v4 %20 %coord
        """
        d=spv_sample_use(dis,{"%10":("resource",2)},{"%12":("sampler",1)})
        self.assertEqual(d["sampled_image_constructions"],1)
        self.assertEqual(d["sample_or_gather_operations"],2)
        self.assertEqual(d["sample_or_gather_with_strict_t_s_pair"],2)
        self.assertEqual(d["distinct_source_t_s_pairs_observed_in_translated_samples"],1)
        self.assertEqual(d["non_sampler_fetch_or_read_instructions"],1)
        self.assertTrue(d["translated_sample_pair_proven_for_every_sample_operation"])

    def test_copy_intermediate_still_traced(self):
        d=spv_sample_use(b"""
        %10 = OpVariable %ptr UniformConstant
        %12 = OpVariable %ptr UniformConstant
        %20 = OpLoad %image %10
        %21 = OpCopyObject %image %20
        %22 = OpLoad %sampler %12
        %30 = OpSampledImage %sampled %21 %22
        %31 = OpCopyObject %sampled %30
        %33 = OpImageGather %vec %31 %uv 0
        """,{"%10":("resource",4)},{"%12":("sampler",9)})
        self.assertEqual(d["sample_or_gather_with_strict_t_s_pair"],1)
        self.assertEqual(d["sample_or_gather_unresolved"],0)

    def test_dynamic_access_chain_must_not_misattribute_sample(self):
        d=spv_sample_use(b"""
        %10 = OpVariable %ptr UniformConstant
        %12 = OpVariable %ptr UniformConstant
        %5 = OpAccessChain %ptr %10 %index
        %20 = OpLoad %image %5
        %22 = OpLoad %sampler %12
        %30 = OpSampledImage %sampled %20 %22
        %33 = OpImageSampleImplicitLod %vec %30 %uv
        """,{"%10":("resource",2)},{"%12":("sampler",9)})
        self.assertEqual(d["sampled_image_constructions_unresolved"],1)
        self.assertEqual(d["sample_or_gather_unresolved"],1)
        self.assertFalse(d["translated_sample_pair_proven_for_every_sample_operation"])

    def test_spirv_reflect_missing_variable_rejected(self):
        with self.assertRaisesRegex(ValueError,"NOT_GLOBAL_VARIABLE"):
            spv_sample_use(b"%4 = OpVariable %ptr UniformConstant\n",
                          {"%10":("resource",2)},{})

    def test_no_sample_is_not_success_and_resolve_no_guesses(self):
        d=spv_sample_use(b"%10 = OpVariable %ptr UniformConstant\n",
                         {"%10":("resource",2)}, {})
        self.assertEqual(d["sample_or_gather_operations"],0)
        self.assertFalse(d["translated_sample_pair_proven_for_every_sample_operation"])

    def test_reject_duplicate_reflection_and_invalid_id(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE"):
            resource_variable_ids({2,4},[refl(11,8,"t2"),refl(12,8,"t4")],"resource")
        with self.assertRaisesRegex(ValueError,"ID_MISSING"):
            resource_variable_ids({2},[{"id":"8","name":"t2"}],"resource")

    def test_unavailable_spirv_instruction_rejected(self):
        with self.assertRaisesRegex(ValueError,"DIS_INPUT_INVALID"):
            spv_sample_use(b"",{},{})
        d=spv_sample_use(b"""
        %10 = OpVariable %ptr UniformConstant
        %33 = OpImageSampleImplicitLod %vec %bogus %uv
        """,{"%10":("resource",2)}, {})
        self.assertEqual(d["sample_or_gather_unresolved"],1)

if __name__=="__main__":unittest.main()
