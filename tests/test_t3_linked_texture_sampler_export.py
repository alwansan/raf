"""T3 authentic linked sampler scope/trace tests; synthetic only."""
import unittest
from collections import Counter

from scripts import t3_linked_texture_sampler_export as m

class LinkedImporterScope(unittest.TestCase):
    def originals(self):
        original={(m.OWNER,i):{} for i in range(1,42)}
        for n in range(89):
            material=(m.OWNER,n%41+1)
            original[material]["LOCAL_"+str(n)]=((0,n+1),(1.,1.,0.,0.))
        for n in range(25):
            material=(m.OWNER,n%41+1)
            fileid=1 if n<22 else 2
            original[material]["EXTERNAL_"+str(n)]=((fileid,n+1 if n<22 else n-21),(1.,1.,0.,0.))
        for n in range(113):
            original[(m.OWNER,n%41+1)]["NULL_"+str(n)]=((0,0),(1.,1.,0.,0.))
        return original
    def paths(self):
        return ["archive:/Raft_Data/sharedassets0.assets","archive:/Raft_Data/sharedassets1.assets"]
    def names(self):
        return Counter({"sharedassets0.assets":1,"sharedassets1.assets":1})
    def traced(self):
        w1={"schema_version":1,"export_instance":"a"*32,"objects":[
            {"class_id":21,"source":{"owner":m.OWNER,"path_id":1},
             "export":{"file_id":2100000,"guid":"b"*32,"type":2}}]}
        b02={"schema_version":1,"export_instance":"a"*32,"objects":[
            {"class_id":28,"source":{"owner":"sharedassets0.assets","path_id":1},
             "export":{"file_id":2800001,"guid":"c"*32,"type":3}},
            {"class_id":28,"source":{"owner":"Raft_Data/sharedassets1.assets","path_id":1},
             "export":{"file_id":2800002,"guid":"d"*32,"type":3}},
        ]}
        return w1,b02
    def fake_report(self, count=2):
        return {"linked_textures_compared":count,
                "field_mismatches":{k:0 for k in m.FIELDS},
                "unresolved_importer_defaults":{k:0 for k in m.FIELDS}}
    def test_selected_exact_114_bound_occurrences(self):
        keys,counts=m.source_targets(self.originals(),self.paths(),self.names())
        self.assertEqual(counts["source_texenv_bound_occurrences"],114)
        self.assertEqual(counts["original_external_texture_slots"],25)
        self.assertEqual(counts["original_local_texture_slots"],89)
        self.assertEqual(len(keys),114)
    def test_wrong_external_fileid_rejected(self):
        o=self.originals()
        o[(m.OWNER,1)]["EXTERNAL_0"]=((3,1),(1.,1.,0.,0.))
        with self.assertRaisesRegex(ValueError,"outside_dependency_table"):
            m.source_targets(o,self.paths(),self.names())
    def test_unnamed_external_provider_rejected(self):
        with self.assertRaises(ValueError):
            m.source_targets(self.originals(),["archive:/Unknown.asset","archive:/sharedassets1.assets"],self.names())
    def test_source_missing_local_bound_target_rejected(self):
        o=self.originals()
        o[(m.OWNER,1)]["LOCAL_0"]=((0,0),(1.,1.,0.,0.))
        with self.assertRaisesRegex(ValueError,"bound_texture_counts_changed"):
            m.source_targets(o,self.paths(),self.names())
    def test_traced_only_selected_exact_object_ids(self):
        w1,b02=self.traced()
        result=m.subset_same_export({("sharedassets0.assets",1),("sharedassets1.assets",1)},w1,b02)
        self.assertEqual(len(result["objects"]),2)
        self.assertEqual(result["export_instance"],"a"*32)
    def test_mixed_two_export_instances_refused(self):
        w1,b02=self.traced()
        b02["export_instance"]="f"*32
        with self.assertRaisesRegex(ValueError,"Different exporter"):
            m.subset_same_export({("sharedassets0.assets",1)},w1,b02)
    def test_foreign_folder_bearing_same_basename_refused(self):
        w1,b02=self.traced()
        b02["objects"][0]["source"]["owner"]="OutsideGame/sharedassets0.assets"
        with self.assertRaisesRegex(ValueError,"unrecognized_untrusted"):
            m.subset_same_export({("sharedassets0.assets",1)},w1,b02)
    def test_missing_exact_texture_target_trace_is_not_match(self):
        w1,b02=self.traced()
        b02["objects"].pop(0)
        with self.assertRaisesRegex(ValueError,"missing_exact"):
            m.subset_same_export({("sharedassets0.assets",1)},w1,b02)
    def test_duplicate_selected_exported_texture_rejected(self):
        w1,b02=self.traced()
        b02["objects"].append(b02["objects"][0].copy())
        with self.assertRaisesRegex(ValueError,"duplicated"):
            m.subset_same_export({("sharedassets0.assets",1)},w1,b02)
    def test_b15_unresolved_default_not_called_faithful(self):
        result=self.fake_report()
        result["unresolved_importer_defaults"]["m_FilterMode"]=1
        public=m.output_aggregate(result,{"unique_linked_source_Texture2D_candidates":2})
        self.assertEqual(public["status"],"SCOPED_SAMPLER_DEFAULTS_UNRESOLVED")
        self.assertFalse(public["original_pixel_content_or_device_shader_verified"])
    def test_actual_six_field_drift_not_silently_passed(self):
        result=self.fake_report()
        result["field_mismatches"]["m_WrapU"]=1
        public=m.output_aggregate(result,{"unique_linked_source_Texture2D_candidates":2})
        self.assertEqual(public["status"],"SCOPED_SAMPLER_MISMATCH")
        self.assertEqual(public["sampler_fields_with_drift"],1)
    def test_all_six_real_meta_fields_equal_is_scoped(self):
        result=m.output_aggregate(self.fake_report(),{"unique_linked_source_Texture2D_candidates":2})
        self.assertEqual(result["status"],"SCOPED_SAMPLER_FIELDS_MATCH")
        self.assertFalse(result["original_pixel_content_or_device_shader_verified"])
    def test_report_drops_private_unknown_fields(self):
        r=self.fake_report()
        r["source_texture_object_guids"]=["e"*32]
        out=str(m.output_aggregate(r,{"unique_linked_source_Texture2D_candidates":2}))
        self.assertNotIn("e"*32,out)
    def test_classified_importer_failure_never_leaks_raw_private_paths(self):
        err=m.StageFailure("actual_TextureImporter_guid_asset_mapping",
                          ValueError("private-original-name/pathid123"))
        self.assertEqual(err.reason,"unclassified_safe_reason")
        self.assertNotIn("private-original-name",str(err))
        known=m.StageFailure("actual_TextureImporter_guid_asset_mapping",
                             ValueError("missing exact exported TextureImporter GUID target"))
        self.assertEqual(known.reason,"missing exact exported TextureImporter GUID target")
        self.assertEqual(known.category,"ValueError")

    def test_missing_importer_documents_cannot_pass(self):
        with self.assertRaisesRegex(ValueError,"not_all_linked"):
            m.output_aggregate(self.fake_report(count=1),{"unique_linked_source_Texture2D_candidates":2})
if __name__=="__main__":unittest.main()
