"""T3 synthetic authenticated-original-Shader48 to actual postvendor GUID join guards.

All original SourceShader48 identities, source IDs, and actual Shader GUIDs in
fixtures are synthetic; no private original Raft resources are loaded here.
"""
import json
import unittest

from scripts import t3_source_renderer_shader_to_postvendor_export as s
from scripts import t3_original_renderer_shader_impact as original

USE=[921,219,121,108,70,34,34,30,20,16,10,10,10,8,6,5,4,3,2,1,1]
assert len(USE)==21 and sum(USE)==1633


class RendererShaderRealExportBridge(unittest.TestCase):
    def fixture(self):
        use={("sharedassets0.assets",i):count for i,count in enumerate(USE,1)}
        w1={"schema_version":1,"export_instance":"a"*32,"objects":[]}
        profiles={}
        for i,count in enumerate(USE,1):
            guid=f"{i:032x}"
            w1["objects"].append({
                "class_id":48,
                "source":{"owner":"sharedassets0.assets","path_id":i},
                "export":{"file_id":4800000,"guid":guid,"type":3},
            })
            profiles[guid]={
                "dummy":i<=19,
                "unbalanced":False,
                "programmed":1,
                "partial_subshader_coverage":False,
            }
        report={
            "status":original.STATUS,
            "counts":{"original_slots_to_verified_Shader48":1633},
            "original_nonnull_renderer_material_slots":1635,
        }
        return use,w1,profiles,report

    def call(self,data=None):
        source,w1,profiles,report=data or self.fixture()
        return s.join(source,w1,profiles,verified_source_report=report)

    def test_921_source_renderer_slots_can_be_proven_still_dummy(self):
        result=self.call()
        self.assertEqual(result["status"],s.STATUS)
        self.assertEqual(result["true_original_typed_Shader48_targets_used_by_scenes"],21)
        self.assertEqual(result["original_typed_Shader48_renderer_material_slots"],1633)
        self.assertEqual(result["original_Shader48_source_to_export_pointer_IDs_verified"],21)
        self.assertEqual(result["highest_source_921_slot_Shader_export_status"],"STILL_DUMMY_AFTER_VENDOR_RESTORERS")
        self.assertEqual(result["top_ten_scene_slot_uses_still_Dummy_no_identity"][0],921)
        self.assertTrue(result["exported_original_Renderer_material_assignment_parity_not_verified"])
        self.assertTrue(result["actual_Unity_import_or_Android_Adreno_pixels_not_verified"])

    def test_original_high_impact_shader_can_be_genuine_vendor_non_dummy(self):
        data=list(self.fixture())
        first=data[1]["objects"][0]["export"]["guid"]
        data[2][first]["dummy"]=False
        result=self.call(data)
        self.assertEqual(result["highest_source_921_slot_Shader_export_status"],
                         "NON_DUMMY_AFTER_VENDOR_RESTORERS_NOT_AUTHORED_EQUIVALENCE")
        self.assertEqual(result["top_ten_scene_slot_uses_still_Dummy_no_identity"][0],219)
        self.assertEqual(result["top_ten_scene_slot_uses_nonDummy_vendor_no_identity"][0],921)
        self.assertTrue(result["source_original_compiled_shader_subprogram_equivalence_not_verified"])

    def test_builtin_export_redirect_kept_separate_from_custom_program(self):
        data=list(self.fixture())
        data[1]["objects"][0]["export"]={
            "file_id":46,"guid":"0000000000000000f000000000000000","type":0}
        result=self.call(data)
        self.assertEqual(result["highest_source_921_slot_Shader_export_status"],
                         "UNITY_BUILTIN_EXPORT_TARGET")
        self.assertEqual(result["original_scene_slot_use_by_actual_postvendor_shader_status"][
                        "scene_renderer_material_slots_to_unity_builtin"],921)
        self.assertEqual(result["source_Shader48_unique_targets_by_actual_postvendor_status"][
                        "source_Shader48_targets_with_unity_builtin"],1)

    def test_builtin_transport_rejects_null_fileid_or_all_zero_guid_for_any_original(self):
        valid="0000000000000000f000000000000000"
        bad_cases=((0,valid),(0,"0"*32),(46,"0"*32),(-1,valid))
        for idx in (0,20):
            for file_id,guid in bad_cases:
                data=list(self.fixture())
                data[1]["objects"][idx]["export"]={
                    "file_id":file_id,"guid":guid,"type":0}
                with self.subTest(source_row=idx,file_id=file_id,zero_guid=guid=="0"*32):
                    with self.assertRaisesRegex(ValueError,"unresolved_or_wrong_actual"):
                        self.call(data)

    def test_source_B03_provenance_cannot_be_substituted_by_unchecked_rows(self):
        data=list(self.fixture())
        data[3]["status"]="SYNTHETIC_OR_UNAUTHENTICATED_SOURCE_ONLY"
        with self.assertRaisesRegex(ValueError,"untrusted_original"):
            self.call(data)

    def test_source_scope_unknown_original_ownership_cannot_be_promoted(self):
        data=list(self.fixture())
        key=list(data[0])[0]
        data[0][("globalgamemanagers.assets",key[1])]=data[0].pop(key)
        with self.assertRaisesRegex(ValueError,"untrusted_authenticated_original_Shader48"):
            self.call(data)

    def test_synthetic_source_incorrect_921_aggregate_refused(self):
        data=list(self.fixture())
        key=next(iter(data[0]))
        data[0][key]+=1
        with self.assertRaisesRegex(ValueError,"untrusted_original"):
            self.call(data)

    def test_missing_source_Shader48_export_trace_refused(self):
        data=list(self.fixture())
        data[1]["objects"].pop()
        with self.assertRaisesRegex(ValueError,"missing_original_to_actual"):
            self.call(data)

    def test_same_source_Shader48_duplicate_export_trace_refused(self):
        data=list(self.fixture())
        data[1]["objects"].append(dict(data[1]["objects"][0]))
        with self.assertRaisesRegex(ValueError,"duplicate_same_instance"):
            self.call(data)

    def test_multiple_real_original_shaders_guid_collision_refused(self):
        data=list(self.fixture())
        data[1]["objects"][1]["export"]=data[1]["objects"][0]["export"].copy()
        with self.assertRaisesRegex(ValueError,"collide_export_GUID"):
            self.call(data)

    def test_real_shader_export_meta_guid_missing_never_fabricated(self):
        data=list(self.fixture())
        bad=data[1]["objects"][0]["export"]["guid"]
        data[2].pop(bad)
        with self.assertRaisesRegex(ValueError,"unresolved_or_wrong_actual"):
            self.call(data)

    def test_unbalanced_or_incomplete_program_is_not_hidden_by_nondummy(self):
        data=list(self.fixture())
        guid=data[1]["objects"][0]["export"]["guid"]
        data[2][guid]["dummy"]=False
        data[2][guid]["unbalanced"]=True
        data[2][guid]["programmed"]=0
        data[2][guid]["partial_subshader_coverage"]=True
        result=self.call(data)
        counts=result["original_scene_slot_use_by_actual_postvendor_shader_status"]
        self.assertEqual(counts["source_scene_slots_to_unbalanced_ShaderLab"],921)
        self.assertEqual(counts["source_scene_slots_to_ShaderLab_without_complete_program"],921)
        self.assertEqual(counts["source_scene_slots_to_incomplete_SubShader_coverage"],921)

    def test_false_same_instance_token_fails_closed(self):
        data=list(self.fixture())
        data[1]["export_instance"]=""
        with self.assertRaisesRegex(ValueError,"untrusted_original"):
            self.call(data)

    def test_report_contains_only_counts_no_original_private_shader_identifiers(self):
        result=json.dumps(self.call(),sort_keys=True)
        for token in ("sharedassets0.assets","m_PathID",'"path_id"',
                      '"guid"', "0000000000000000f000000000000000",
                      "shader_source","sceneRendererName"):
            self.assertNotIn(token,result)
        self.assertFalse(json.loads(result)["private_original_Shader_names_IDs_Guids_exposed"])


if __name__=="__main__":
    unittest.main()
