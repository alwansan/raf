"""Synthetic original Shader source-only texture string private-hash controls."""
import copy
import re
import unittest

from scripts.t2_foam_managed_literal_targets import prepare_private_hashes,sha


def profile():
    return {
        "_private_authored_textures":{"authored_name"},
        "_private_stage_rows":[
            {"pass":0,"stage_code":1,"_source_names":[],"source_rows":0},
            {"pass":0,"stage_code":0,"_source_names":[
                "authored_name","nonprop_1","nonprop_2","nonprop_3","nonprop_4"
            ],"source_rows":5},
            {"pass":1,"stage_code":1,"_source_names":[],"source_rows":0},
            {"pass":1,"stage_code":0,"_source_names":["authored_name"],"source_rows":1},
        ],
        "original_texture_name_to_shader_texture_property_matches":2,
        "original_source_texture_rows":6,
    }


class OriginalFoamPrivateHashControls(unittest.TestCase):
    def test_four_non_authored_and_one_author_property_sha_only(self):
        v=prepare_private_hashes(profile())
        self.assertEqual(v["schema_version"],1)
        self.assertEqual(len(v["non_authored_sha256"]),4)
        self.assertEqual(len(v["authored_texture_sha256"]),1)
        self.assertEqual(len(set(v["non_authored_sha256"])),4)
        self.assertEqual(v["original_source_texture_occurrences"],6)
        self.assertEqual(v["original_distinct_source_texture_names"],5)
        self.assertFalse(v["runtime_upload_proven"])
        self.assertNotIn("authored_name",str(v))
        self.assertNotIn("nonprop_1",str(v))
        self.assertTrue(all(re.fullmatch("[a-f0-9]{64}",h)
                            for h in v["non_authored_sha256"]))

    def test_source_fingerprint_sha_uses_exact_utf8(self):
        self.assertNotEqual(sha("private"),sha("Private"))
        self.assertEqual(len(sha("one")),64)

    def test_name_input_invalid_or_nontext_refused(self):
        for bad in ("",None,0,True,"A"*257,"no\x00yes"):
            with self.subTest(bad=bad),self.assertRaises(ValueError):
                sha(bad)

    def test_refuse_wrong_number_authored_proven_source_matches(self):
        q=profile()
        q["original_texture_name_to_shader_texture_property_matches"]=1
        with self.assertRaises(ValueError):
            prepare_private_hashes(q)

    def test_refuse_fabricated_six_authored_properties(self):
        q=profile()
        q["_private_authored_textures"]=set(q["_private_stage_rows"][1]["_source_names"])
        with self.assertRaises(ValueError):
            prepare_private_hashes(q)

    def test_refuse_unverified_alternate_pass1_property(self):
        q=profile()
        q["_private_stage_rows"][3]["_source_names"]=["nonprop_1"]
        with self.assertRaises(ValueError):
            prepare_private_hashes(q)

    def test_refuse_same_resource_name_repeated_within_one_pass(self):
        q=profile()
        q["_private_stage_rows"][1]["_source_names"][3]="nonprop_1"
        with self.assertRaises(ValueError):
            prepare_private_hashes(q)

    def test_refuse_extra_vertex_texture_assumption(self):
        q=profile()
        q["_private_stage_rows"][0]["_source_names"]=["secret"]
        with self.assertRaises(ValueError):
            prepare_private_hashes(q)

    def test_refuse_dropped_real_original_four_stage_key(self):
        q=profile()
        q["_private_stage_rows"].pop(0)
        with self.assertRaises(ValueError):
            prepare_private_hashes(q)

    def test_refuse_ambiguous_stage_duplicate(self):
        q=profile()
        q["_private_stage_rows"][2]["pass"]=0
        with self.assertRaises(ValueError):
            prepare_private_hashes(q)

    def test_refuse_wrong_total_source_texture_cardinality(self):
        q=profile()
        q["original_source_texture_rows"]=5
        with self.assertRaises(ValueError):
            prepare_private_hashes(q)

    def test_refuse_invalid_container_instead_of_faking_private_source(self):
        for q in ({},None,[],{"_private_authored_textures":[]}):
            with self.subTest(q=q),self.assertRaises(ValueError):
                prepare_private_hashes(q)

    def test_preserve_scope_separate_source_register_zero_in_both_passes(self):
        q=profile()
        report=prepare_private_hashes(q)
        self.assertNotIn("source_to_material_upload_verified",report)
        self.assertTrue(report["native_to_spirv_six_active_descriptor_pairs_proven_prior"])
        self.assertFalse(report["runtime_upload_proven"])


if __name__=="__main__":
    unittest.main()
