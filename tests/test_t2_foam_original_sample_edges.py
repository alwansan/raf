"""Synthetic executable DXBC instruction-use controls for exact original Foam t/s."""
import unittest

from scripts.t2_foam_original_sample_edges import (
    original_dx_sample_pair, token_instruction_usage,
)


def sample_words(texture=2, sampler=3):
    # Existing B Blur inherited source-free valid SAMPLE operand fixture.
    dest = 2 | (15 << 4) | (1 << 20)
    coord = 2 | (1 << 2) | (228 << 4) | (1 << 20)
    tex = 2 | (1 << 2) | (228 << 4) | (7 << 12) | (1 << 20)
    sam = (6 << 12) | (1 << 20)
    return [69 | (9 << 24), dest, 0, coord, 1, tex, texture, sam, sampler]


def source_rows(*pairs):
    return [{"original_texture_index":t, "original_sampler_index":s}
            for t,s in pairs]


def native_words(instructions, stage=0):
    flat = [word for inst in instructions for word in inst]
    return [(stage << 16) | (5 << 4), 2 + len(flat), *flat]


class NativeOriginalSampleUseTests(unittest.TestCase):
    def test_real_sample_operand_pair_validated_independently(self):
        self.assertEqual(original_dx_sample_pair(
            sample_words(2, 3), [{"m_Index":2,"m_SamplerIndex":3}]), (2,3))

    def test_real_sample_instruction_set_matches_source_pair(self):
        a = token_instruction_usage(
            native_words([sample_words(0,0), sample_words(2,3)]),
            0, source_rows((0,0),(2,3)))
        self.assertEqual(a["observed_opcode69_sample_calls"],2)
        self.assertEqual(a["observed_unique_opcode69_t_s_pairs"], [[0,0],[2,3]])
        self.assertTrue(a["all_source_pairs_actively_used_proved"])
        self.assertFalse(a["native_dxbc_to_spirv_compiled_binding_identity_verified"])
        self.assertFalse(a["device_shaderlab_or_pixels_verified"])

    def test_empty_vertex_stage_has_empty_coverage(self):
        a=token_instruction_usage(native_words([],stage=1),1,[])
        self.assertTrue(a["all_source_pairs_actively_used_proved"])
        self.assertEqual(a["observed_opcode69_sample_calls"],0)

    def test_duplicate_sample_calls_not_miscounted_as_distinct_pairs(self):
        a=token_instruction_usage(
            native_words([sample_words(2,3),sample_words(2,3)]),
            0,source_rows((2,3)))
        self.assertEqual(a["observed_opcode69_sample_calls"],2)
        self.assertEqual(a["observed_unique_opcode69_t_s_pairs"],[[2,3]])

    def test_native_sampler_mismatch_rejected(self):
        with self.assertRaises(ValueError):
            token_instruction_usage(native_words([sample_words(2,3)]),
                                    0,source_rows((2,4)))

    def test_native_sample_wrong_texture_register_rejected(self):
        with self.assertRaises(ValueError):
            token_instruction_usage(native_words([sample_words(2,3)]),
                                    0,source_rows((1,3)))

    def test_fewer_actually_sampled_pairs_never_infer_complete_use(self):
        a=token_instruction_usage(native_words([sample_words(2,3)]),
                                  0,source_rows((2,3),(4,5)))
        self.assertFalse(a["all_source_pairs_actively_used_proved"])
        self.assertEqual(a["observed_unique_opcode69_t_s_pairs"], [[2,3]])

    def test_other_sample_variant_explicitly_unknown(self):
        a=token_instruction_usage(
            native_words([sample_words(2,3),[70|(1<<24)]]),
            0,source_rows((2,3)))
        self.assertFalse(a["all_source_pairs_actively_used_proved"])
        self.assertEqual(a["unhandled_sample_variant_counts"],
                         [{"opcode":70,"count":1}])

    def test_all_unhandled_variants_counted_without_forged_pairs(self):
        a=token_instruction_usage(native_words([[x|(1<<24)] for x in (70,71,72,73,74)]),
                                  0,source_rows((2,3)))
        self.assertEqual(a["observed_opcode69_sample_calls"],0)
        self.assertEqual(len(a["unhandled_sample_variant_counts"]),5)
        self.assertFalse(a["all_source_pairs_actively_used_proved"])

    def test_unknown_opcode_not_treated_as_texture_sample(self):
        a=token_instruction_usage(native_words([[1|(1<<24)]]),0,[])
        self.assertTrue(a["all_source_pairs_actively_used_proved"])
        self.assertEqual(a["observed_opcode69_sample_calls"],0)

    def test_bad_sample_truncated_and_wrong_arity_fails_closed(self):
        for instr in (sample_words()[:-1], sample_words()+[0]):
            with self.subTest(n=len(instr)),self.assertRaises(ValueError):
                token_instruction_usage(native_words([instr]),0,source_rows((2,3)))

    def test_invalid_native_dxbc_header_or_length_rejected(self):
        for words in (
            [0,2],
            [(2<<16)|(5<<4),2],
            native_words([sample_words()],stage=1),
            [0|(5<<4),999,69|(9<<24)],
        ):
            with self.subTest(words=words[:2]),self.assertRaises(ValueError):
                token_instruction_usage(words,0,source_rows((2,3)))

    def test_incomplete_native_instruction_boundary_refused(self):
        words=native_words([[69|(9<<24),2,0,0]])
        with self.assertRaises(ValueError):
            token_instruction_usage(words,0,source_rows((2,3)))

    def test_private_source_does_not_leak_symbols(self):
        a=token_instruction_usage(native_words([sample_words(2,3)]),0,
                                  source_rows((2,3)))
        self.assertFalse(a["private_source_names_or_shader_bytes_disclosed"])
        self.assertNotIn("PrivateShaderName",repr(a))

    def test_invalid_bound_or_noninteger_binary_token_rejected(self):
        for words in ([0,2.0], [0,2**32], [True,2]):
            with self.assertRaises(ValueError):
                token_instruction_usage(words,0,[])

    def test_out_of_range_sample_register_rejected(self):
        with self.assertRaises(ValueError):
            original_dx_sample_pair(sample_words(256,3),
                                    [{"m_Index":256,"m_SamplerIndex":3}])


if __name__=="__main__":
    unittest.main()
