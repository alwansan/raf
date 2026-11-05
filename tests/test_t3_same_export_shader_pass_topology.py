"""Source-free T3 Shader48 to same-export ShaderLab per-pass structural deficit."""
import copy
import unittest

from scripts import t3_same_export_shader_pass_topology as m

class SameExportShaderTopology(unittest.TestCase):
    def fixture(self):
        src={}
        trace={"schema_version":1,"export_instance":"a"*32,"objects":[]}
        outputs={}
        # Original ten, 9 custom, 1 builtin: 4+5*4+3*3+5=38
        nums=[4,4,4,4,4,4,3,3,3,5]
        self.assertEqual(sum(nums),38)
        for i,n in enumerate(nums):
            key=("resources.assets" if i==0 else "sharedassets0.assets",i+1)
            src[key]={"pass_count":n,"subshader_pass_counts":[n]}
            dest={"file_id":4800000,"guid":f"{i:032x}","type":3}
            if i==0:
                dest={"file_id":46,"guid":"0000000000000000f000000000000000","type":0}
            else:
                outputs[dest["guid"]]={"pass_count":1,
                                      "programmed_pass_count":1,
                                      "subshader_pass_counts":[1]}
            trace["objects"].append({"class_id":48,"source":{"owner":key[0],"path_id":key[1]},"export":dest})
        trace["objects"].append({"class_id":21,"source":{"owner":"sharedassets6.assets","path_id":999},
                                 "export":{"file_id":2100999,"guid":"b"*32,"type":2}})
        return src,trace,outputs
    def call(self,data=None,verified=True):
        original,trace,outputs=data or self.fixture()
        return m.compare(original,trace,outputs,real_links_proven=verified)
    def test_original_38_vs_custom_9_exact_join_reports_structural_deficit(self):
        result=self.call()
        self.assertEqual(result["status"],"SCOPED_SHADERLAB_PASS_TOPOLOGY_DEFICIT")
        self.assertEqual(result["counts"]["original_ten_shader_passes"],38)
        self.assertEqual(result["counts"]["original_builtin_transport_passes"],4)
        self.assertEqual(result["counts"]["original_custom_Shader_pass_records"],34)
        self.assertEqual(result["counts"]["exported_custom_ShaderLab_passes"],9)
        self.assertEqual(result["counts"]["missing_original_passes_in_custom_ShaderLab"],25)
        self.assertFalse(result["original_compiled_variant_program_equivalence_verified"])
    def test_absent_same_export_material_shader_verification_is_rejected(self):
        with self.assertRaisesRegex(ValueError,"links_unproven"):self.call(verified=False)
    def test_missing_export_ShaderLab_meta_target_rejected(self):
        values=list(self.fixture())
        values[2].pop(next(iter(values[2])))
        with self.assertRaisesRegex(ValueError,"meta_file_count_mismatch"):self.call(values)
    def test_shader_source_type_alias_not_permitted(self):
        values=list(self.fixture())
        values[1]["objects"][0]["source"]["owner"]="wrong-owner"
        with self.assertRaisesRegex(ValueError,"same_export_Shader_targets_not_ten"):self.call(values)
    def test_duplicate_custom_export_guid_cannot_claim_two_shaders(self):
        values=list(self.fixture())
        values[1]["objects"][2]["export"]=values[1]["objects"][1]["export"].copy()
        with self.assertRaisesRegex(ValueError,"collide_in_export"):self.call(values)
    def test_custom_exported_extra_passes_are_not_silenced(self):
        values=list(self.fixture())
        for v in values[2].values():
            v["pass_count"]=5
            v["programmed_pass_count"]=5
            v["subshader_pass_counts"]=[5]
        result=self.call(values)
        self.assertEqual(result["counts"]["custom_shaders_with_extra_passes"],8)
        self.assertGreater(result["counts"]["extra_exported_custom_ShaderLab_passes"],0)
    def test_source_pass_sum_mismatch_fails_closed(self):
        values=list(self.fixture())
        values[0][("resources.assets",1)]["pass_count"]=3
        values[0][("resources.assets",1)]["subshader_pass_counts"]=[3]
        with self.assertRaisesRegex(ValueError,"count_changed"):self.call(values)
    def test_invalid_exported_pass_profile_rejected(self):
        values=list(self.fixture())
        target=next(iter(values[2].values()))
        target["pass_count"]=2
        with self.assertRaisesRegex(ValueError,"invalid_actual_ShaderLab_profile"):self.call(values)
    def test_safe_failure_stage_never_exposes_original_private_exception(self):
        problem=m.SafeStageFailure("original_Shader48_parsed_pass_topology","LookupError")
        self.assertEqual(problem.stage,"original_Shader48_parsed_pass_topology")
        self.assertEqual(problem.category,"LookupError")
        self.assertNotIn("private",str(problem))

    def test_private_names_ids_guid_not_in_result(self):
        result=str(self.call())
        self.assertNotIn("0000000000000000f000000000000000",result)
        self.assertNotIn("m_ParsedForm",result)
        self.assertNotIn("path_id",result)
if __name__=="__main__":unittest.main()
