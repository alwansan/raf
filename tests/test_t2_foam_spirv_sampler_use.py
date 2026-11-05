"""T2 original Foam compiled sampled texture/sampler pairing: synthetic SSA controls."""
import unittest

from scripts.t2_foam_spirv_sampler_use import trace_sampled_pairs


def module(body="", image_binding=6, sampler_binding=1):
    return """
; private SPIR-V test (not game source)
OpDecorate %tex DescriptorSet 0
OpDecorate %tex Binding %d
OpDecorate %%sampler DescriptorSet 0
OpDecorate %%sampler Binding %d
%%tex = OpVariable %%ptrimg UniformConstant
%%sampler = OpVariable %%ptrsampler UniformConstant
%%loaded_tex = OpLoad %%img %%tex
%%loaded_sampler = OpLoad %%samp %%sampler
%%combined = OpSampledImage %%sampled %%loaded_tex %%loaded_sampler
%s
""" % (image_binding, sampler_binding, body)


class UsedSamplerPairsTests(unittest.TestCase):
    def run_parse(self, src, images=((0, 6),), samplers=((0, 1),)):
        return trace_sampled_pairs(src, images, samplers)

    def test_actual_sampled_image_call_records_exact_numeric_pair(self):
        r = self.run_parse(module("%out = OpImageSampleImplicitLod %v4float %combined %uv"))
        self.assertEqual(r["compiled_sampling_ops"], 1)
        self.assertEqual(r["used_image_sampler_pairs"], [
            {"image_set": 0, "image_binding": 6,
             "sampler_set": 0, "sampler_binding": 1}])
        self.assertTrue(r["all_declared_resources_used_verified"])
        self.assertFalse(r["original_source_texture_to_compiled_pair_identity_verified"])
        self.assertFalse(r["unity_material_upload_or_sampler_state_verified"])

    def test_copy_alias_chain_is_followed(self):
        r = self.run_parse(module("""
%image_copy = OpCopyObject %img %loaded_tex
%sampler_copy = OpCopyObject %samp %loaded_sampler
%combined2 = OpSampledImage %sampled %image_copy %sampler_copy
%combined3 = OpCopyObject %sampled %combined2
%out = OpImageSampleExplicitLod %v4float %combined3 %uv Lod %zero
"""))
        self.assertEqual(r["compiled_sampling_ops"], 1)
        self.assertEqual(r["distinct_used_pair_count"], 1)

    def test_dead_combined_object_not_a_use_edge(self):
        r = self.run_parse(module("%irrelevant = OpImageFetch %v4float %loaded_tex %xy"))
        self.assertEqual(r["compiled_sampling_ops"], 0)
        self.assertEqual(r["distinct_used_pair_count"], 0)
        self.assertFalse(r["all_declared_resources_used_verified"])

    def test_multiple_samples_same_pair_deduplicated(self):
        r = self.run_parse(module("""
%out1 = OpImageSampleImplicitLod %v4float %combined %uv
%out2 = OpImageSampleExplicitLod %v4float %combined %uv Lod %level
"""))
        self.assertEqual(r["compiled_sampling_ops"], 2)
        self.assertEqual(r["distinct_used_pair_count"], 1)

    def test_two_real_pairs_not_count_only(self):
        src = module("%out = OpImageSampleImplicitLod %v4float %combined %uv")
        src += """
OpDecorate %tex2 DescriptorSet 0
OpDecorate %tex2 Binding 7
OpDecorate %sampler2 DescriptorSet 0
OpDecorate %sampler2 Binding 2
%tex2 = OpVariable %ptrimg UniformConstant
%sampler2 = OpVariable %ptrsampler UniformConstant
%i2 = OpLoad %img %tex2
%s2 = OpLoad %samp %sampler2
%c2 = OpSampledImage %sampled %i2 %s2
%o2 = OpImageSampleImplicitLod %v4float %c2 %uv
"""
        r = self.run_parse(src, ((0, 6), (0, 7)), ((0, 1), (0, 2)))
        self.assertEqual(r["distinct_used_pair_count"], 2)
        self.assertEqual(r["used_image_count"], 2)
        self.assertEqual(r["used_sampler_count"], 2)

    def test_unknown_sampled_image_provenance_fails_closed(self):
        for suffix in (
            "%out = OpImageSampleImplicitLod %v4float %never_defined %uv",
            "%out = OpImageSampleImplicitLod %v4float %loaded_tex %uv",
        ):
            with self.subTest(suffix=suffix), self.assertRaises(ValueError):
                self.run_parse(module(suffix))

    def test_dynamic_or_phi_resource_ambiguous(self):
        src = module("""
%dynamic_ptr = OpAccessChain %ptrimg %tex %index
%dynamic_image = OpLoad %img %dynamic_ptr
%opaque = OpSampledImage %sampled %dynamic_image %loaded_sampler
%out = OpImageSampleImplicitLod %v4float %opaque %uv
""")
        with self.assertRaises(ValueError):
            self.run_parse(src)

    def test_missing_or_duplicate_numeric_descriptor_decorations_fail(self):
        src = module("%out = OpImageSampleImplicitLod %v4float %combined %uv")
        with self.assertRaises(ValueError):
            self.run_parse(src + "\nOpDecorate %tex Binding 6\n")
        with self.assertRaises(ValueError):
            self.run_parse(src.replace("OpDecorate %tex Binding 6", ""))

    def test_mismatched_actual_pair_rejected(self):
        with self.assertRaises(ValueError):
            self.run_parse(module("%out = OpImageSampleImplicitLod %v4float %combined %uv",
                                  image_binding=9))

    def test_private_names_cannot_spoof_instr(self):
        src = module("""OpName %x "OpDecorate %tex Binding 10"
OpName %y "OpImageSampleImplicitLod %v4float %combined %uv"
%out = OpImageSampleImplicitLod %v4float %combined %uv""")
        self.assertEqual(self.run_parse(src)["compiled_sampling_ops"], 1)

    def test_cyclic_copy_object_rejected(self):
        src = module("""
%cyclic1 = OpCopyObject %sampled %cyclic2
%cyclic2 = OpCopyObject %sampled %cyclic1
%out = OpImageSampleImplicitLod %v4float %cyclic1 %uv
""")
        with self.assertRaises(ValueError):
            self.run_parse(src)

    def test_expected_slot_input_must_be_typed_and_nonoverlapping(self):
        for images, samplers in (
            ([(True, 6)], [(0, 1)]),
            ([(0, 6), (0, 6)], [(0, 1)]),
            ([(0, 6)], [(0, 6)]),
            ([(0, 256)], [(0, 1)]),
        ):
            with self.subTest(images=images, samplers=samplers), self.assertRaises(
                    ValueError):
                self.run_parse(module(), images, samplers)

    def test_empty_vertex_stage_has_zero_pairs(self):
        r = self.run_parse("; header only\nOpEntryPoint Vertex %main \"main\"\n", (), ())
        self.assertEqual(r["compiled_sampling_ops"], 0)
        self.assertTrue(r["all_declared_resources_used_verified"])


if __name__ == "__main__":
    unittest.main()
