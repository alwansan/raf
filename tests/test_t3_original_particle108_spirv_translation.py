"""Synthetic-only four original Particle108 DXBC pair -> SPIR-V CPU diagnostic.

No real shader source, GUIDs, code, names, or private program hashes.
"""
import json
from pathlib import Path
import tempfile
import unittest

from scripts import t3_original_particle108_spirv_translation as t3


def meta(index, kw=0):
    return {"m_BlobIndex":index,
            "m_ShaderHardwareTier":0,
            "m_KeywordIndices":[kw],
            "m_GlobalKeywordIndices":[],
            "m_LocalKeywordIndices":[]}


def parsed():
    v=[meta(0,k) for k in range(4)]
    f=[meta(1,k) for k in (3,1,0,2)]
    return {"m_Name":"SYNTHETIC_PRIVATE_SHADER_NEVER_PUBLISH",
            "m_SubShaders":[{"m_Passes":[{
                "m_Type":0,
                "progVertex":{"m_SubPrograms":v,"m_PlayerSubPrograms":[]},
                "progFragment":{"m_SubPrograms":f,"m_PlayerSubPrograms":[]},
            }]}]}


def table():
    return [(0,b"synthetic-original-private-DXBC") for _ in range(16)]


def fake_link(metadata,table_rows,stage):
    assert len(table_rows)==16
    if metadata["m_BlobIndex"]!=(0 if stage==1 else 1):
        raise ValueError("mismatched_original_shader_compiled_stage")
    return (b"private-code-"+bytes((stage,metadata["m_KeywordIndices"][0])),{})


def translate(code,stage,path):
    assert code.startswith(b"private-code")
    assert path.is_dir()
    return {"stage":stage,"vulkan11_valid":True,"hlsl_recovered":True,
            "roundtrip_vulkan11_valid":True,
            "dxbc_sha256":"synthetic-secret-hash",
            "hlsl_sha256":"synthetic-private-program-hash"}


def reflect(path):
    stage=int(path.parent.name.rsplit("-stage-",1)[1])
    value={"inputs":[],"outputs":[],"resource_slots":{}}
    if stage==1:
        value["outputs"]=[{"location":0,"type":"vec4"}]
    else:
        value["inputs"]=[{"location":0,"type":"vec4"}]
        value["resource_slots"]={"textures":[[0,1]]}
    return value


class Particle108SPIRVSourceOnly(unittest.TestCase):
    def test_four_full_private_pairs_keyword_join_not_array_position(self):
        pairs=t3.exact_four_pairs(parsed(),table(),linker=fake_link)
        self.assertEqual(len(pairs),4)
        self.assertEqual([f[1][-1] for f in pairs],[0,1,2,3])
        self.assertEqual([v[-1] for v,_ in pairs],[0,1,2,3])

    def test_reject_keyword_drift_instead_of_guessing_fragment(self):
        p=parsed()
        p["m_SubShaders"][0]["m_Passes"][0]["progFragment"]["m_SubPrograms"][-1]["m_KeywordIndices"]=[8]
        with self.assertRaisesRegex(ValueError,"keyword_bucket_mismatch"):
            t3.exact_four_pairs(p,table(),linker=fake_link)

    def test_duplicate_keyword_or_wrong_vertex_stage_refused(self):
        p=parsed()
        p["m_SubShaders"][0]["m_Passes"][0]["progVertex"]["m_SubPrograms"][-1]["m_KeywordIndices"]=[0]
        with self.assertRaisesRegex(ValueError,"duplicate_original"):
            t3.exact_four_pairs(p,table(),linker=fake_link)
        with self.assertRaisesRegex(ValueError,"compiled_stage"):
            t3.exact_four_pairs(parsed(),table(),linker=lambda m,t,kind:fake_link({**m,"m_BlobIndex":1},t,kind))

    def test_wrong_pass_or_short_table_fails_closed(self):
        p=parsed()
        p["m_SubShaders"][0]["m_Passes"][0]["m_Type"]=1
        with self.assertRaisesRegex(ValueError,"non_normal"):
            t3.exact_four_pairs(p,table(),linker=fake_link)
        with self.assertRaisesRegex(ValueError,"program_table"):
            t3.exact_four_pairs(parsed(),table()[:15],linker=fake_link)
        p=parsed()
        del p["m_SubShaders"][0]["m_Passes"][0]["progFragment"]
        with self.assertRaisesRegex(ValueError,"missing_original"):
            t3.exact_four_pairs(p,table(),linker=fake_link)

    def test_all_eight_stages_vulkan_spirv_and_roundtrip_reflection(self):
        pairs=t3.exact_four_pairs(parsed(),table(),linker=fake_link)
        with tempfile.TemporaryDirectory() as d:
            r=t3.evaluate(pairs,Path(d),translator=translate,reflector=reflect)
        c=r["counts"]
        for key in ("stage_translation_attempts","source_stage_spirv_vulkan11_valid",
                    "stage_hlsl_recovered","stage_hlsl_roundtrip_spirv_vulkan11_valid",
                    "original_stage_reflections","roundtrip_stage_reflections",
                    "stage_original_roundtrip_reflection_pairs_compared",
                    "stage_original_roundtrip_io_equal",
                    "stage_original_roundtrip_resource_slot_shapes_equal",
                    "stage_original_roundtrip_io_drift_classified",
                    "io_drift_inputs_identical","io_drift_outputs_identical"):
            self.assertEqual(c[key],8,key)
        for key in ("source_vs_fs_interfaces_compared","source_vs_fs_interfaces_compatible",
                    "roundtrip_vs_fs_interfaces_compared","roundtrip_vs_fs_interfaces_compatible",
                    "pairs_with_both_source_stages_spirv_vulkan11_valid",
                    "pairs_with_both_roundtrip_stages_spirv_vulkan11_valid"):
            self.assertEqual(c[key],4,key)
        self.assertEqual(r["status"],t3.STATUS)
        self.assertFalse(r["native_Unity_Android_Adreno_pixels_verified"])
        self.assertFalse(r["full_Unity_HLSL_ShaderLab_original_semantics_verified"])
        public=json.dumps(r,sort_keys=True)
        for private in ("synthetic-secret-hash","synthetic-private-program-hash",
                        "SYNTHETIC_PRIVATE_SHADER","private-code","textures",
                        "synthetic-original-private-DXBC"):
            self.assertNotIn(private,public)

    def test_failed_fragment_translation_does_not_claim_pair_success(self):
        def partial(code,stage,path):
            return {"stage":stage,"vulkan11_valid":stage==1,
                    "hlsl_recovered":False,"roundtrip_vulkan11_valid":False,
                    "private_bytes":"do-not-publish"}
        with tempfile.TemporaryDirectory() as d:
            r=t3.evaluate(t3.exact_four_pairs(parsed(),table(),linker=fake_link),
                          Path(d),translator=partial,reflector=reflect)
        c=r["counts"]
        self.assertEqual(c["stage_translation_attempts"],8)
        self.assertEqual(c["source_stage_spirv_vulkan11_valid"],4)
        self.assertEqual(c["pairs_with_both_source_stages_spirv_vulkan11_valid"],0)
        self.assertEqual(c["source_vs_fs_interfaces_compared"],0)
        self.assertNotIn("do-not-publish",json.dumps(r))

    def test_cross_stage_drift_reject_invalid_translator_flags(self):
        def malformed(_code,stage,_path):
            return {"stage":stage,"vulkan11_valid":False,
                    "hlsl_recovered":False,"roundtrip_vulkan11_valid":True}
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"translator_result"):
                t3.evaluate(t3.exact_four_pairs(parsed(),table(),linker=fake_link),
                            Path(d),translator=malformed,reflector=reflect)

    def test_stage_io_mismatch_is_counted_not_success(self):
        def bad_reflection(path):
            row=reflect(path)
            if "roundtrip" in path.name and row["outputs"]:
                row["outputs"]=[{"location":1,"type":"vec4"}]
            return row
        with tempfile.TemporaryDirectory() as d:
            r=t3.evaluate(t3.exact_four_pairs(parsed(),table(),linker=fake_link),
                          Path(d),translator=translate,reflector=bad_reflection)
        self.assertEqual(r["counts"]["stage_original_roundtrip_io_equal"],4)
        self.assertEqual(r["counts"]["roundtrip_vs_fs_interfaces_compared"],4)
        self.assertEqual(r["counts"]["roundtrip_vs_fs_interfaces_compatible"],0)
        self.assertEqual(r["counts"]["source_vs_fs_interfaces_compatible"],4)
        self.assertEqual(r["counts"]["io_drift_outputs_location_only_remap_candidate"],4)
        self.assertEqual(r["counts"]["io_drift_outputs_type_multiset_equal"],8)
        self.assertEqual(r["counts"]["io_drift_outputs_same_location_type_changes"],0)

    def test_original_to_roundtrip_type_change_is_not_location_only(self):
        def bad_type(path):
            row=reflect(path)
            if "roundtrip" in path.name and row["outputs"]:
                row["outputs"]=[{"location":0,"type":"vec3"}]
            return row
        with tempfile.TemporaryDirectory() as d:
            r=t3.evaluate(t3.exact_four_pairs(parsed(),table(),linker=fake_link),
                          Path(d),translator=translate,reflector=bad_type)
        self.assertEqual(r["counts"]["io_drift_outputs_same_location_type_changes"],4)
        self.assertEqual(r["counts"]["io_drift_outputs_location_only_remap_candidate"],0)
        self.assertEqual(r["counts"]["io_drift_outputs_type_multiset_equal"],4)
        self.assertEqual(r["counts"]["source_vs_fs_interfaces_compatible"],4)
        self.assertEqual(r["counts"]["roundtrip_vs_fs_interfaces_compatible"],0)

    def test_private_io_classifier_must_only_emit_bounded_numeric_counts(self):
        def bad_classifier(_a,_b):
            return {"inputs_identical":1,"PRIVATE_STAGE_LABEL":"sensitive"}
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"classifier_shape"):
                t3.evaluate(t3.exact_four_pairs(parsed(),table(),linker=fake_link),
                            Path(d),translator=translate,reflector=reflect,
                            io_classifier=bad_classifier)
        def negative_classifier(a,b):
            from scripts.t3_stage_io_drift import classify_stage_io
            result=classify_stage_io(a,b)
            result["outputs_removed_locations"]=-1
            return result
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaisesRegex(ValueError,"numeric_count"):
                t3.evaluate(t3.exact_four_pairs(parsed(),table(),linker=fake_link),
                            Path(d),translator=translate,reflector=reflect,
                            io_classifier=negative_classifier)

    def test_invalid_reflection_private_identity_cannot_escape(self):
        def bad(_path):
            return {"inputs":[{"location":0,"type":"vec4","name":"PRIVATE_LABEL"}],
                    "outputs":[],"resource_slots":{}}
        with tempfile.TemporaryDirectory() as d:
            r=t3.evaluate(t3.exact_four_pairs(parsed(),table(),linker=fake_link),
                          Path(d),translator=translate,reflector=bad)
        self.assertEqual(r["counts"]["original_stage_reflections"],0)
        self.assertEqual(r["counts"]["original_stage_reflection_failures"],8)
        self.assertNotIn("PRIVATE_LABEL",json.dumps(r))

if __name__=="__main__":
    unittest.main()
