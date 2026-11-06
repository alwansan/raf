"""T3 original Particle108 one Pass real D3D11 linkage, source-free guards.

Synthetic fixtures only. No original copyrighted shader source/programs.
"""
import json
import unittest

from scripts import t3_original_particle108_dxbc_feasibility as target
from scripts import t3_original_renderer_shader_impact as original
from test_t3_original_particle_shader_state import state


def population():
    ids=[("resources.assets",i+31) for i in range(6)]
    report={
        "status":original.STATUS,
        "six_original_scenes_sha_verified":True,
        "original_particle_Shader48_ranked_material_slot_use_no_identity":[108,34,34,20,16,3],
        "original_particle_highest_Shader48_unique":True,
        "original_particle_highest_Shader48_nonparticle_renderer_slots":0,
        "original_particle_highest_Shader48_original_pass_count":1,
    }
    return dict(zip(ids,target.RANKS)),report


def meta(blob,keywords=None):
    return {"m_BlobIndex":blob,"m_ShaderHardwareTier":0,
            "m_KeywordIndices":[] if keywords is None else list(keywords)}


def parsed(vert=None,frag=None,s=None):
    return {"m_Name":"SYNTHETIC_PRIVATE_SHADER_NAME_NOT_TO_LEAK",
            "m_SubShaders":[{"m_Passes":[{
                "m_Type":0,"m_State":state() if s is None else s,
                "progVertex":{"m_SubPrograms":[meta(0)] if vert is None else vert,
                              "m_PlayerSubPrograms":[]},
                "progFragment":{"m_SubPrograms":[meta(1)] if frag is None else frag,
                                "m_PlayerSubPrograms":[]},
            }]}]}


def fake_link(m,_records,stage):
    if m["m_BlobIndex"] != (0 if stage==1 else 1):
        raise ValueError("wrong_original_stage_link")
    return (b"synthetic-vs-stage" if stage==1 else b"synthetic-fs-stage"),{}


class Original108ParticleDXBC(unittest.TestCase):
    def test_unique_original_particle_source_identity_selected(self):
        ids,r=population()
        self.assertEqual(target.select(ids,r),("resources.assets",31))

    def test_rank_or_source_sha_drift_rejected(self):
        ids,r=population()
        r["six_original_scenes_sha_verified"]=False
        with self.assertRaisesRegex(ValueError,"untrusted_original_108"):
            target.select(ids,r)
        ids,r=population()
        ids[("resources.assets",31)]=107
        with self.assertRaisesRegex(ValueError,"untrusted_original_108"):
            target.select(ids,r)
        ids,r=population()
        r["original_particle_highest_Shader48_nonparticle_renderer_slots"]=1
        with self.assertRaisesRegex(ValueError,"untrusted_original_108"):
            target.select(ids,r)

    def test_linked_one_pass_vertex_fragment_permutation(self):
        d=target.inspect(parsed(),[(0,b"private-synthetic-entry")],link=fake_link)
        self.assertEqual(d["status"],target.STATUS)
        self.assertEqual(d["original_source_108_particle_Shader48_slots"],108)
        self.assertEqual(d["genuine_D3D11_vertex_stage_variant_records"],1)
        self.assertEqual(d["genuine_D3D11_fragment_stage_variant_records"],1)
        self.assertEqual(d["distinct_original_linked_D3D11_programs"],2)
        self.assertEqual(d["matched_vertex_fragment_permutation_pairs"],1)
        self.assertEqual(d["normal_passes_with_matched_permutation_pair"],1)
        self.assertTrue(d["original_all_compiled_vertex_fragment_stages_available"])
        self.assertFalse(d["authored_Android_ShaderLab_or_SPIRV_equivalence_proven"])
        dumped=json.dumps(d)
        self.assertNotIn("SYNTHETIC_PRIVATE_SHADER_NAME",dumped)
        self.assertNotIn("private-synthetic-entry",dumped)

    def test_two_keyword_variants_match_exact_order_and_metadata(self):
        shader=parsed(vert=[meta(0,[1]),meta(0,[2])],
                      frag=[meta(1,[2]),meta(1,[1])])
        d=target.inspect(shader,[(0,b"p")],link=fake_link)
        self.assertEqual(d["matched_vertex_fragment_permutation_pairs"],2)
        self.assertEqual(d["stage_variants_with_keywords"],4)
        self.assertEqual(d["unmatched_fragment_permutations"],0)
        self.assertEqual(d["unmatched_vertex_permutations"],0)

    def test_unpaired_keyword_is_never_claimed_matched(self):
        shader=parsed(vert=[meta(0,[1])],frag=[meta(1,[2])])
        d=target.inspect(shader,[(0,b"p")],link=fake_link)
        self.assertEqual(d["matched_vertex_fragment_permutation_pairs"],0)
        self.assertFalse(d["original_all_compiled_vertex_fragment_stages_available"])
        self.assertEqual(d["normal_passes_without_matched_permutation_pair"],1)
        self.assertEqual(d["unmatched_vertex_permutations"],1)
        self.assertEqual(d["unmatched_fragment_permutations"],1)

    def test_no_d3d11_explicit_no_code_not_shaderlab_success(self):
        d=target.inspect(parsed(),None)
        self.assertEqual(d["status"],target.NO_D3D11)
        self.assertEqual(d["genuine_D3D11_vertex_stage_variant_records"],0)
        self.assertFalse(d["original_all_compiled_vertex_fragment_stages_available"])
        self.assertFalse(d["actual_Unity_Android_Adreno_pixels_verified"])

    def test_duplicate_permutation_and_wrong_stage_link_fail_closed(self):
        s=parsed(vert=[meta(0),meta(0)])
        with self.assertRaisesRegex(ValueError,"duplicated_original_stage"):
            target.inspect(s,[(0,b"p")],link=fake_link)
        s=parsed(frag=[meta(0)])
        with self.assertRaisesRegex(ValueError,"wrong_original_stage_link"):
            target.inspect(s,[(0,b"p")],link=fake_link)

    def test_missing_normal_pass_or_fragment_rejected(self):
        s=parsed()
        s["m_SubShaders"][0]["m_Passes"][0]["m_Type"]=1
        with self.assertRaisesRegex(ValueError,"non_normal"):
            target.inspect(s,[(0,b"p")],link=fake_link)
        s=parsed()
        del s["m_SubShaders"][0]["m_Passes"][0]["progFragment"]
        with self.assertRaisesRegex(ValueError,"missing_normal_pass"):
            target.inspect(s,[(0,b"p")],link=fake_link)

    def test_empty_or_malformed_program_table_is_inconclusive(self):
        for table in ([],{"records":[]},[0],True):
            with self.subTest(table=repr(table)):
                with self.assertRaises((ValueError,TypeError,KeyError)):
                    target.inspect(parsed(),table,link=fake_link)


if __name__=="__main__":
    unittest.main()
