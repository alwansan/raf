"""No-source regression for provisional original-spectrum 7Pass keyword router.

Never use original keyword spelling, .shader source, DXBC or Material.
"""
import copy
import hashlib
import unittest

from scripts.b09_stage_original_spectrum import _variant_key
from scripts.gt_spectrum_private_keyword_routed_shaderlab import selector, compose
from scripts.w1_depth_shaderlab import stage_body


KW="_SYNTHETIC_KEYWORD_INDEX4"
METAS=[
    {"m_ShaderHardwareTier":0,
     "m_KeywordIndices":[],
     "m_GlobalKeywordIndices":[],
     "m_LocalKeywordIndices":[]},
    {"m_ShaderHardwareTier":0,
     "m_KeywordIndices":[4],
     "m_GlobalKeywordIndices":[],
     "m_LocalKeywordIndices":[]},
]


def fake_original():
    return {
        "m_Name":"UltimateWater/Spectrum/Water Spectrum",
        "m_KeywordNames":["A","B","C","D",KW],
        "m_SubShaders":[{"m_Passes":[
            {"progVertex":{"variant_source":1},
             "progFragment":{"variant_source":0}} for _ in range(7)]}],
    }


def fake_stage_variants(_program):
    return [(0,0,copy.deepcopy(METAS[0])),(0,1,copy.deepcopy(METAS[1]))]


def fake_manifest(*, swapped=False):
    values=[(False,0),(True,1)]
    if swapped:
        values=list(reversed(values))
    return {
        "stages":[
            {"pass_index":p,
             "variant_pairs":[
                 {"pair_index":i,
                  "variant_key_sha256":hashlib.sha256(
                      _variant_key(METAS[1 if on else 0]).encode()).hexdigest()}
                 for i,(on,j) in enumerate(values)]}
            for p in range(7)],
    }


def _candidate(variant):
    arr=['Shader "UltimateWater/Spectrum/Water Spectrum" {',
         'Properties { _Fake("Fake",Float)=0 }','SubShader {']
    for p in range(7):
        vert=("float4 cb0_0_m0[4];\n"
              "float4 main():SV_Position{return cb0_0_m0[%d];}" % (variant))
        frag=("float4 cb0_0_m0[%d];\n"
              "float4 main():SV_Target{return cb0_0_m0[%d];}"
              % (p+5,variant))
        arr.extend(["Pass {","ZWrite On","HLSLPROGRAM",
                    "#pragma target 5.0",
                    "#pragma vertex main",
                    "#pragma fragment main",
                    stage_body(vert,frag),
                    "ENDHLSL","}"])
    arr.extend(["}","}"])
    return "\n".join(arr)+"\n"


class OriginalSpectrumKeywordRouterTests(unittest.TestCase):
    def test_sha_linked_per_pass_keyword_name_only_from_index4(self):
        name, rows=selector(fake_original(),fake_manifest(),
                            variant_reader=fake_stage_variants)
        self.assertEqual(name,KW)
        self.assertEqual(rows,[{False:0,True:1} for _ in range(7)])

    def test_keyword_pass_hash_not_filename_order(self):
        _, rows=selector(fake_original(),fake_manifest(swapped=True),
                         variant_reader=fake_stage_variants)
        self.assertEqual(rows,[{True:0,False:1} for _ in range(7)])

    def test_all_seven_pass_bodies_have_both_sources_and_only_one_keyword_macro(self):
        candidate, proof=compose(fake_original(),fake_manifest(),
                                 _candidate(0),_candidate(1),
                                 variant_reader=fake_stage_variants)
        self.assertEqual(candidate.count("#pragma multi_compile __ "+KW),7)
        self.assertEqual(candidate.count("#if defined("+KW+")"),7)
        self.assertEqual(candidate.count("HLSLPROGRAM"),7)
        self.assertEqual(candidate.count("ENDHLSL"),7)
        self.assertIn("GT_PRIVATE_VS_cb0_0_m0",candidate)
        self.assertIn("GT_PRIVATE_PS_cb0_0_m0",candidate)
        self.assertEqual(proof["source_program_variant_stage_references"],28)
        self.assertEqual(proof["source_original_keyword_index"],4)
        self.assertTrue(proof["source_original_VS_FS_pair_hashes_authenticated"])
        self.assertFalse(proof["original_shader_keyword_flags_pragma_scope_proven"])
        self.assertFalse(proof["Unity_Android_2021_import_or_GPU_proven"])

    def test_source_unknown_keyword_not_guessed(self):
        p=fake_original()
        p["m_KeywordNames"][4]="a keyword space"
        with self.assertRaisesRegex(ValueError,"keyword_name_unsupported"):
            selector(p,fake_manifest(),variant_reader=fake_stage_variants)

    def test_keyword_index_outside_exact_source_bit_refused(self):
        def wrong(_):
            arr=fake_stage_variants({})
            arr[1][2]["m_KeywordIndices"]=[3]
            return arr
        with self.assertRaisesRegex(ValueError,"other_bits_unmodelled"):
            selector(fake_original(),fake_manifest(),variant_reader=wrong)

    def test_unmatched_original_packet_hash_rejected(self):
        m=fake_manifest()
        m["stages"][4]["variant_pairs"][1]["variant_key_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"hash_and_slot_drift"):
            selector(fake_original(),m,variant_reader=fake_stage_variants)

    def test_incomplete_original_shaderlab_disallowed(self):
        with self.assertRaises(ValueError):
            compose(fake_original(),fake_manifest(),
                    _candidate(0).replace("HLSLPROGRAM","CGPROGRAM",1),
                    _candidate(1),variant_reader=fake_stage_variants)

    def test_different_render_states_not_patched_or_assumed_equal(self):
        with self.assertRaisesRegex(ValueError,"source_envelopes_not_equal"):
            compose(fake_original(),fake_manifest(),
                    _candidate(0),_candidate(1).replace("ZWrite On","ZWrite Off",1),
                    variant_reader=fake_stage_variants)


if __name__=="__main__":
    unittest.main()
