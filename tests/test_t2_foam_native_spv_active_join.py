"""Source-free exact active native DXBC t/s ↔ translated SPV pair join controls."""
import copy
import unittest

from scripts.t2_foam_native_spv_active_join import (
    exact_native_translated_sample_join, numeric_pair,
)


def fixture(count=1, *, sample_calls=None):
    sample_calls=sample_calls or (17 if count==5 else 4)
    rows=[{"source_kind":"cb","original_dxbc_register":0,
           "compiled_image_sampler_or_cb_set":0,"compiled_binding":0}]
    pairs=[]
    for index in range(count):
        rows += [{"source_kind":"image","original_dxbc_register":index,
                  "compiled_image_sampler_or_cb_set":0,
                  "compiled_binding":index+(6 if count==5 else 2)},
                 {"source_kind":"sampler","original_dxbc_register":index,
                  "compiled_image_sampler_or_cb_set":0,
                  "compiled_binding":index+1}]
        pairs.append([index,index])
    mapped={"source_native_dxbc_to_compiled_original_spirv_id_verified":True,
            "full_original_spirv_graph_equal_after_only_descriptor_literals_mask":True,
            "distinct_explicit_profiles_proven":2,
            "source_register_to_default_compiled_descriptors":rows}
    native={"all_source_pairs_actively_used_proved":True,
            "observed_opcode69_sample_calls":sample_calls,
            "unhandled_sample_variant_counts":[],
            "original_source_numeric_pair_set":pairs,
            "observed_unique_opcode69_t_s_pairs":pairs}
    spv={"all_declared_resources_used_verified":True,
         "compiled_sampling_ops":sample_calls,
         "private_identifiers_published":False,
         "used_image_sampler_pairs":[{
             "image_set":0,"image_binding":i+(6 if count==5 else 2),
             "sampler_set":0,"sampler_binding":i+1,
         } for i in range(count)]}
    return mapped,native,spv


class AuthenticSampleJoinTests(unittest.TestCase):
    def test_native_21_sample_calls_six_source_pairs_synthetic_two_passes(self):
        x=exact_native_translated_sample_join(*fixture(5),5)
        y=exact_native_translated_sample_join(*fixture(1),1)
        self.assertEqual(x["native_sample_calls"]+y["native_sample_calls"],21)
        self.assertEqual(x["source_active_pair_count"]+y["source_active_pair_count"],6)
        self.assertTrue(x["source_to_translated_active_sample_pair_identity_verified"])
        self.assertEqual(x["translated_to_original_native_register_pairs"],
                         [[0,0],[1,1],[2,2],[3,3],[4,4]])
        self.assertFalse(x["unity_material_upload_sampler_state_verified"])
        self.assertFalse(x["shaderlab_or_adreno_pixels_verified"])

    def test_equal_counts_wrong_compiled_sampler_pair_fails(self):
        m,n,s=fixture(5)
        s["used_image_sampler_pairs"][0]["sampler_binding"]=2
        with self.assertRaises(ValueError):
            exact_native_translated_sample_join(m,n,s,5)

    def test_equal_counts_wrong_original_native_sampler_pair_fails(self):
        m,n,s=fixture(5)
        n["observed_unique_opcode69_t_s_pairs"][0]=[0,1]
        with self.assertRaises(ValueError):
            exact_native_translated_sample_join(m,n,s,5)

    def test_equal_total_calls_not_a_proven_identity_when_used_count_wrong(self):
        m,n,s=fixture(5)
        s["used_image_sampler_pairs"].pop()
        with self.assertRaises(ValueError):
            exact_native_translated_sample_join(m,n,s,5)

    def test_different_native_and_compiled_sample_counts_fail(self):
        m,n,s=fixture(1)
        n["observed_opcode69_sample_calls"]=5
        with self.assertRaises(ValueError):
            exact_native_translated_sample_join(m,n,s,1)

    def test_missing_explicit_original_provenance_flags_rejected(self):
        for key in ("source_native_dxbc_to_compiled_original_spirv_id_verified",
                    "full_original_spirv_graph_equal_after_only_descriptor_literals_mask",
                    "distinct_explicit_profiles_proven"):
            m,n,s=fixture(1)
            m[key]=False
            with self.subTest(key=key),self.assertRaises(ValueError):
                exact_native_translated_sample_join(m,n,s,1)

    def test_duplicate_native_source_pair_rejected(self):
        m,n,s=fixture(5)
        n["original_source_numeric_pair_set"][1]=[0,0]
        with self.assertRaises(ValueError):
            exact_native_translated_sample_join(m,n,s,5)

    def test_duplicate_source_register_and_compiled_descriptor_alias_rejected(self):
        for field in ("original_dxbc_register","compiled_binding"):
            m,n,s=fixture(5)
            m["source_register_to_default_compiled_descriptors"][3][field]=(
                m["source_register_to_default_compiled_descriptors"][1][field])
            with self.subTest(field=field),self.assertRaises(ValueError):
                exact_native_translated_sample_join(m,n,s,5)

    def test_translated_resource_variable_set_mismatch_rejected(self):
        m,n,s=fixture(1)
        s["used_image_sampler_pairs"][0]["image_set"]=3
        with self.assertRaises(ValueError):
            exact_native_translated_sample_join(m,n,s,1)

    def test_unknown_compiled_sampler_descriptor_pair_rejected(self):
        m,n,s=fixture(1)
        s["used_image_sampler_pairs"][0]["sampler_binding"]=99
        with self.assertRaises(ValueError):
            exact_native_translated_sample_join(m,n,s,1)

    def test_unsupported_original_native_sample_opcode_is_not_a_proof(self):
        m,n,s=fixture(1)
        n["unhandled_sample_variant_counts"]=[{"opcode":70,"count":1}]
        with self.assertRaises(ValueError):
            exact_native_translated_sample_join(m,n,s,1)

    def test_different_original_vs_compiled_active_resource_coverage_rejected(self):
        for field in ("all_source_pairs_actively_used_proved","all_declared_resources_used_verified"):
            m,n,s=fixture(1)
            if field in n:
                n[field]=False
            else:
                s[field]=False
            with self.subTest(field=field),self.assertRaises(ValueError):
                exact_native_translated_sample_join(m,n,s,1)

    def test_private_name_injection_rejected(self):
        m,n,s=fixture(1)
        s["used_image_sampler_pairs"][0]["PrivateShaderName"]="never"
        with self.assertRaises(ValueError):
            exact_native_translated_sample_join(m,n,s,1)

    def test_bool_float_or_negative_source_register_denied(self):
        for x in (True,0.0,-1,65536):
            with self.subTest(x=x),self.assertRaises(ValueError):
                numeric_pair([x,0])

    def test_duplicate_translated_source_binding_rejected(self):
        m,n,s=fixture(5)
        m["source_register_to_default_compiled_descriptors"][3]["compiled_binding"]=6
        with self.assertRaises(ValueError):
            exact_native_translated_sample_join(m,n,s,5)

    def test_numeric_source_stage_scope_required_not_global(self):
        # Both genuine Foam passes contain source pair t0/s0. Each stage
        # remains independently scoped with different compiled image binding.
        m,n,s=fixture(1)
        res=exact_native_translated_sample_join(m,n,s,1)
        self.assertTrue(res["source_to_translated_active_sample_pair_identity_verified"])
        m2,n2,s2=fixture(5)
        res2=exact_native_translated_sample_join(m2,n2,s2,5)
        self.assertTrue(res2["source_to_translated_active_sample_pair_identity_verified"])
        self.assertNotEqual(s["used_image_sampler_pairs"][0]["image_binding"],
                            s2["used_image_sampler_pairs"][0]["image_binding"])


if __name__=="__main__":
    unittest.main()
