"""Synthetic-only tests, not original Raft Shader keyword source."""
import unittest

from scripts.gt_spectrum_keyword_flag_semantics_control import shader_text, summarize_controls


class SyntheticFlagScopeTests(unittest.TestCase):
    def test_exactly_two_different_pragma_scopes(self):
        global_shader=shader_text("global")
        local_shader=shader_text("local")
        self.assertEqual(global_shader.count("#pragma multi_compile __ GT_SCOPE_PROBE"),1)
        self.assertEqual(local_shader.count("#pragma multi_compile_local __ GT_SCOPE_PROBE"),1)
        self.assertNotEqual(global_shader,local_shader)

    def test_match_local_raw_value_still_provisional(self):
        r=summarize_controls({"global":1,"local":0},0)
        self.assertEqual(r["candidate_scope_by_matching_byte"],"local")
        self.assertFalse(r["source_original_Spectrum_keyword_scope_proven"])
        self.assertFalse(r["game_Shader_or_GUID_modified"])

    def test_match_global_raw_value_still_provisional(self):
        r=summarize_controls({"global":0,"local":1},0)
        self.assertEqual(r["candidate_scope_by_matching_byte"],"global")
        self.assertFalse(r["source_original_Spectrum_keyword_scope_proven"])

    def test_ambiguous_flags_not_accepted_as_scope(self):
        r=summarize_controls({"global":0,"local":0},0)
        self.assertEqual(r["candidate_scope_by_matching_byte"],"undetermined")
        self.assertFalse(r["synthetic_global_local_flag_bytes_distinguishable"])

    def test_unrelated_flag_not_guessed(self):
        r=summarize_controls({"global":1,"local":2},0)
        self.assertEqual(r["matching_synthetic_controls"],0)
        self.assertEqual(r["candidate_scope_by_matching_byte"],"undetermined")

    def test_bad_rows_fail_closed(self):
        for d in ({"global":0}, {"global":0,"local":True},
                  {"global":-1,"local":1},
                  {"global":0,"local":256},
                  {"global":0,"local":0,"other":0}):
            with self.subTest(row=d):
                with self.assertRaises(ValueError):
                    summarize_controls(d,0)

    def test_original_flag_bad_input_rejected(self):
        for value in (-1,256,True,"0"):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    summarize_controls({"global":0,"local":1},value)

    def test_unknown_scope_shader_rejected(self):
        with self.assertRaises(ValueError):
            shader_text("unknown")


if __name__=="__main__":
    unittest.main()
