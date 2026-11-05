"""T3 pure exact-name Unity built-in source coverage tests (fictional shaders)."""
import json
import unittest
from scripts import t3_top_original_shader_builtin_coverage as m

COUNTS=[921,219,121,108,70,34,34,30,20,16,10,10,10,8,6,5,4,3,2,1,1]
assert len(COUNTS)==21 and sum(COUNTS)==1633


class OriginalBuiltinNameCoverage(unittest.TestCase):
    def fixture(self):
        weights={("sharedassets0.assets",i):n for i,n in enumerate(COUNTS,1)}
        names={("sharedassets0.assets",i):"Synthetic/Shader"+str(i) for i in range(1,22)}
        builtin={"Synthetic/Shader1","Synthetic/Shader3","Synthetic/Shader21"}
        return weights,names,builtin

    def call(self,data=None,verify=False):
        use,names,builtin=data or self.fixture()
        return m.compare(use,names,builtin,sha_verified=verify)

    def test_exact_source_top_shader_name_match_is_not_compiled_equivalence(self):
        result=self.call()
        self.assertEqual(result["status"],"SYNTHETIC_NAME_CLASSIFICATION_ONLY")
        self.assertEqual(result["original_source_Shader48_targets_exact_name_in_Unity_archive"],3)
        self.assertEqual(result["original_scene_renderer_slot_uses_exact_name_in_Unity_archive"],1043)
        self.assertTrue(result["highest_original_921_source_shader_name_in_Unity2021_builtins"])
        self.assertTrue(result["native_builtin_restorer_actual_application_not_verified"])
        self.assertTrue(result["exact_name_match_not_evidence_original_compiled_program_equivalence"])
        self.assertFalse(result["pinned_Unity2021_runtime_shader_archive_SHA_verified"])

    def test_no_top_shader_921_match_when_only_other_shader_names(self):
        data=list(self.fixture())
        data[2].remove("Synthetic/Shader1")
        result=self.call(data)
        self.assertFalse(result["highest_original_921_source_shader_name_in_Unity2021_builtins"])
        self.assertEqual(result["top_source_slot_uses_without_2021_builtin_name_match_no_identity"][0],921)

    def test_case_mismatch_does_not_fake_name_match(self):
        data=list(self.fixture())
        data[2].remove("Synthetic/Shader1")
        data[2].add("synthetic/shader1")
        self.assertFalse(self.call(data)["highest_original_921_source_shader_name_in_Unity2021_builtins"])

    def test_original_incomplete_shader_source_scope_refused(self):
        data=list(self.fixture())
        data[0].pop(("sharedassets0.assets",1))
        with self.assertRaisesRegex(ValueError,"untrusted_original"):
            self.call(data)

    def test_original_source_untrusted_owner_or_PathID_rejected(self):
        data=list(self.fixture())
        data[0][("outside",1)]=data[0].pop(("sharedassets0.assets",1))
        data[1][("outside",1)]=data[1].pop(("sharedassets0.assets",1))
        with self.assertRaisesRegex(ValueError,"malformed_authenticated"):
            self.call(data)

    def test_bogus_original_shader_name_rejected(self):
        for bad in (None,True,0,"","Synthetic\x00Name"):
            data=list(self.fixture())
            data[1][("sharedassets0.assets",1)]=bad
            with self.subTest(bad=repr(bad)),self.assertRaisesRegex(ValueError,"malformed_original"):
                self.call(data)

    def test_wrong_vendor_archive_name_input_rejected(self):
        data=list(self.fixture())
        data[2].add(None)
        with self.assertRaisesRegex(ValueError,"malformed_verifiable"):
            self.call(data)

    def test_no_single_original_dominant_921_shader_cannot_be_assumed(self):
        data=list(self.fixture())
        a,b=("sharedassets0.assets",1),("sharedassets0.assets",2)
        data[0][a]=820
        data[0][b]=320
        with self.assertRaisesRegex(ValueError,"expected_single_original_921"):
            self.call(data)

    def test_original_private_shader_names_pathids_guids_not_published(self):
        data=list(self.fixture())
        result=json.dumps(self.call(data),sort_keys=True)
        for private in ("Synthetic/Shader1","sharedassets0.assets",'"path_id"', "m_Name","m_PathID","GUID"):
            # The report contains only counters and fixed description keys.
            if private=="GUID":
                continue
            self.assertNotIn(private,result)

    def test_sha_verified_flag_does_not_claim_native_application(self):
        result=self.call(verify=True)
        self.assertEqual(result["status"],m.STATUS)
        self.assertTrue(result["pinned_Unity2021_runtime_shader_archive_SHA_verified"])
        self.assertFalse(result["names_or_raw_original_IDs_Guids_programs_published"])
        self.assertTrue(result["Unity_2021_Android_import_or_Adreno_pixels_not_verified"])


if __name__=="__main__":
    unittest.main()
