"""T3 source-free smoke34 D3D11 variant feasibility counter protections."""
import json
import unittest

from scripts import t3_original_smoke34_dxbc_program_inventory as m
from test_t3_original_particle_shader_state import parsed


def linked_summary(*_args):
    counts = {k:0 for k in m.COUNTERS}
    counts.update({
        "genuine_D3D11_vertex_stage_variant_records": 3,
        "genuine_D3D11_fragment_stage_variant_records": 3,
        "distinct_original_linked_D3D11_programs": 6,
        "matched_vertex_fragment_permutation_pairs": 2,
        "normal_passes_with_matched_permutation_pair": 1,
        "normal_passes_without_matched_permutation_pair": 0,
        "unmatched_vertex_permutations": 1,
        "unmatched_fragment_permutations": 1,
        "stage_variants_with_keywords": 4,
    })
    return {
        "status": m.graph.STATUS,
        "original_source_Shader48_SubShader_count": 1,
        "original_source_Shader48_pass_count": 1,
        "normal_passes": 1,
        "non_normal_passes_not_stage_linked": 0,
        "shader_name_private": "NEVER_PUBLISH",
        "original_program_hashes_private": "NEVER_PUBLISH",
        **counts
    }


class OriginalSmoke34D3D11SourceTests(unittest.TestCase):
    def test_real_source_state_but_no_d3d11_platform_is_not_feasibility_pass(self):
        report=m.classify(None,parsed())
        self.assertEqual(report["status"],m.MISSING)
        self.assertFalse(report["original_D3D11_platform_present"])
        self.assertFalse(report["source_original_D3D11_vertex_fragment_pair_available"])
        self.assertFalse(report["native_game_device_smoke_pixels_verified"])

    def test_matched_stage_variant_reports_counts_only(self):
        report=m.classify([(0,b"synthetic_dx_program")],parsed(),
                          summarizer=linked_summary)
        self.assertEqual(report["status"],m.STATUS)
        self.assertTrue(report["source_original_D3D11_vertex_fragment_pair_available"])
        self.assertEqual(report["matched_vertex_fragment_permutation_pairs"],2)
        self.assertEqual(report["original_D3D11_platform_table_records"],1)
        self.assertFalse(report["same_source_programs_compiled_for_Android_verified"])
        out=json.dumps(report)
        for s in ("NEVER_PUBLISH","synthetic_dx_program","original_program_hashes_private"):
            self.assertNotIn(s,out)

    def test_invalid_or_empty_program_table_rejected(self):
        for table in ([],[(0,b"")],[(True,b"x")],[(-1,b"x")],[(0,"DXBC")]):
            with self.subTest(table=table),self.assertRaises(ValueError):
                m.classify(table,parsed(),summarizer=linked_summary)

    def test_bad_private_linker_summary_fails_closed(self):
        def fake(*args):
            return dict(linked_summary(*args), normal_passes=2)
        with self.assertRaises(ValueError):
            m.classify([(0,b"x")],parsed(),summarizer=fake)

    def test_bool_instead_of_count_rejected(self):
        def fake(*args):
            return dict(linked_summary(*args),
                        matched_vertex_fragment_permutation_pairs=True)
        with self.assertRaises(ValueError):
            m.classify([(0,b"x")],parsed(),summarizer=fake)

    def test_non_normal_source_or_second_pass_rejected(self):
        p=parsed()
        p["m_SubShaders"][0]["m_Passes"][0]["m_Type"]=1
        with self.assertRaises(ValueError):
            m.classify(None,p)
        p=parsed()
        p["m_SubShaders"][0]["m_Passes"].append(p["m_SubShaders"][0]["m_Passes"][0])
        with self.assertRaises(ValueError):
            m.classify(None,p)

    def test_no_gpu_device_acceptance_from_complete_original_D3D11(self):
        r=m.classify([(0,b"x")],parsed(),summarizer=linked_summary)
        self.assertTrue(r["original_source_RGB_ColorMask_verified"])
        self.assertTrue(r["original_source_AlphaDependent_color_and_alpha_verified"])
        self.assertFalse(r["authored_original_ShaderLab_recovery_verified"])
        self.assertFalse(r["native_game_device_smoke_pixels_verified"])


if __name__ == "__main__":
    unittest.main()
