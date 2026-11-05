"""T3 921-original-Shader48 D3D11 stage linkage: strict source-free controls."""
import json
import unittest

from scripts import t3_original_top_shader_dxbc_feasibility as target
from scripts import t3_original_renderer_shader_impact as source


def stage_program(rows):
    return {"m_SubPrograms": rows, "m_PlayerSubPrograms": []}


def meta(index, keyword=None, tier=0):
    return {
        "m_BlobIndex": index, "m_ShaderHardwareTier": tier,
        "m_KeywordIndices": [] if keyword is None else [keyword],
    }


def pass0(vert=None, frag=None):
    return {
        "m_Type": 0,
        "progVertex": stage_program([meta(0)] if vert is None else vert),
        "progFragment": stage_program([meta(1)] if frag is None else frag),
    }


def parsed(passes):
    return {"m_SubShaders": [{"m_Passes": passes}]}


def link(metadata, _table, stage):
    if metadata["m_BlobIndex"] != (0 if stage == 1 else 1):
        raise ValueError("synthetic_wrong_original_program_stage")
    return (b"original-vertex" if stage == 1 else b"original-fragment"), {}


def original_population():
    keys = [("sharedassets0.assets", i+1) for i in range(21)]
    counts = [921, 47] + [35]*19
    assert sum(counts) == 1633
    private = dict(zip(keys, counts))
    report = {
        "status": source.STATUS,
        "six_original_scenes_sha_verified": True,
        "original_distinct_typed_Shader48_targets": 21,
        "counts": {"original_slots_to_verified_Shader48": 1633},
    }
    return keys, private, report


class OriginalShaderD3D11(unittest.TestCase):
    def test_true_high_use_identity_is_selected_only_from_original_source(self):
        keys, private, report = original_population()
        self.assertEqual(target.selected_high_use(private, report), keys[0])

    def test_high_use_target_missing_or_forged_source_rejected(self):
        keys, private, report = original_population()
        report["six_original_scenes_sha_verified"] = False
        with self.assertRaisesRegex(ValueError, "unauthenticated"):
            target.selected_high_use(private, report)
        report["six_original_scenes_sha_verified"] = True
        private[keys[0]] = 920
        with self.assertRaisesRegex(ValueError, "mismatch"):
            target.selected_high_use(private, report)

    def test_stage_linkage_counts_are_not_shaderlab_or_gpu_proof(self):
        result = target.summarize(parsed([pass0()]), [(0,b"record")], link=link)
        self.assertEqual(result["original_source_Shader48_pass_count"], 1)
        self.assertEqual(result["normal_passes"], 1)
        self.assertEqual(result["genuine_D3D11_vertex_stage_variant_records"], 1)
        self.assertEqual(result["genuine_D3D11_fragment_stage_variant_records"], 1)
        self.assertEqual(result["matched_vertex_fragment_permutation_pairs"], 1)
        self.assertEqual(result["normal_passes_with_matched_permutation_pair"], 1)
        self.assertEqual(result["distinct_original_linked_D3D11_programs"], 2)
        self.assertFalse(result["full_authored_ShaderLab_program_or_variant_equivalence_proven"])
        self.assertFalse(result["native_Android_Adreno_gpu_execution_verified"])

    def test_non_normal_pass_explicitly_unverified(self):
        p = {"m_Type": 1}
        result = target.summarize(parsed([p, pass0()]), [(0,b"a")], link=link)
        self.assertEqual(result["original_source_Shader48_pass_count"], 2)
        self.assertEqual(result["non_normal_passes_not_stage_linked"], 1)
        self.assertEqual(result["normal_passes_with_matched_permutation_pair"], 1)

    def test_multiple_subshader_passes_are_separately_counted(self):
        p = parsed([pass0()])
        p["m_SubShaders"].append({"m_Passes": [pass0(), {"m_Type": 2}]})
        result = target.summarize(p, [(0,b"a")], link=link)
        self.assertEqual(result["original_source_Shader48_SubShader_count"], 2)
        self.assertEqual(result["original_source_Shader48_pass_count"], 3)
        self.assertEqual(result["original_source_pass_counts_per_SubShader"], [1,2])

    def test_missing_original_fragment_stage_fails_closed(self):
        p = pass0()
        del p["progFragment"]
        with self.assertRaisesRegex(ValueError,"missing_normal_pass"):
            target.summarize(parsed([p]), [(0,b"a")], link=link)

    def test_wrong_compiled_stage_rejected_by_linker(self):
        def bad_link(_meta, _table, stage):
            raise ValueError("Original pass-stage/bytecode mismatch")
        with self.assertRaisesRegex(ValueError, "mismatch"):
            target.summarize(parsed([pass0()]), [(0,b"a")], link=bad_link)

    def test_duplicate_keyword_permutation_fails_closed(self):
        p = pass0(vert=[meta(0), meta(0)], frag=[meta(1)])
        with self.assertRaisesRegex(ValueError,"duplicated_original_stage"):
            target.summarize(parsed([p]), [(0,b"a")], link=link)

    def test_unpaired_keyword_variants_not_treated_as_matched(self):
        p = pass0(vert=[meta(0,keyword=1)],frag=[meta(1,keyword=2)])
        result = target.summarize(parsed([p]), [(0,b"a")], link=link)
        self.assertEqual(result["normal_passes_without_matched_permutation_pair"], 1)
        self.assertEqual(result["matched_vertex_fragment_permutation_pairs"],0)
        self.assertEqual(result["unmatched_vertex_permutations"],1)
        self.assertEqual(result["unmatched_fragment_permutations"],1)

    def test_no_passes_or_empty_compiled_table_fails(self):
        with self.assertRaisesRegex(ValueError,"no_passes"):
            target.summarize(parsed([]), [(0,b"a")], link=link)
        with self.assertRaisesRegex(ValueError,"empty_original_D3D11"):
            target.summarize(parsed([pass0()]), [], link=link)

    def test_full_report_keeps_original_names_bytecode_and_ids_private(self):
        p = pass0(vert=[meta(0,keyword=19)],frag=[meta(1,keyword=19)])
        r = target.summarize(parsed([p]), [(0,b"private")], link=link)
        txt = json.dumps(r)
        for forbidden in ("shadername", "original-vertex", "original-fragment", "sharedassets0.assets",
                          "m_BlobIndex", "m_KeywordIndices", "private"):
            self.assertNotIn(forbidden,txt)
        self.assertEqual(r["stage_variants_with_keywords"],2)

    def test_no_original_program_or_stage_data_is_manufactured(self):
        def empty(_metadata, _table, _stage):
            return b"",{}
        with self.assertRaisesRegex(ValueError,"missing_genuine_original"):
            target.summarize(parsed([pass0()]), [(0,b"a")], link=empty)

if __name__=="__main__":
    unittest.main()
