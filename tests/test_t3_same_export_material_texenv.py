"""Source-free negative controls for T3 exact-export Material/Texture lineage join."""
from __future__ import annotations
import unittest
from scripts import t3_same_export_material_texenv as m

class T3TraceContract(unittest.TestCase):
    def w1(self):
        return {"schema_version":1,"export_instance":"a"*32,
                "objects":[{"class_id":21,"source":{"owner":"synthetic","path_id":1},
                            "export":{"file_id":1,"guid":"b"*32,"type":2}}]}
    def tex(self):
        return {"schema_version":1,"export_instance":"a"*32,
                "objects":[{"class_id":28,"source":{"owner":"synthetic","path_id":2},
                            "export":{"file_id":2,"guid":"c"*32,"type":2}}]}
    def good_counters(self):
        return {k:0 for k in m.COUNTERS} | {k:False for k in m.FLAGS} | {
            "materials_compared":41,"source_texture_slots":227,"slots_compared":227,
            "uv_transform_slots_compared":227,"source_slots_faithful_with_resolved_scope":True,
            "all_uv_transforms_verified":True}

    def test_same_instance_keeps_both_native_classes(self):
        result=m.combine_same_export(self.w1(),self.tex())
        self.assertEqual([x["class_id"] for x in result["objects"]],[21,28])
        self.assertEqual(result["export_instance"],"a"*32)
    def test_mismatched_real_exports_fail_closed(self):
        tex=self.tex()
        tex["export_instance"]="d"*32
        with self.assertRaises(ValueError):
            m.combine_same_export(self.w1(),tex)
    def test_no_texture_trace_fails_closed(self):
        tex=self.tex()
        tex["objects"]=[]
        with self.assertRaises(ValueError):
            m.combine_same_export(self.w1(),tex)
    def test_unknown_w1_object_type_fails_closed(self):
        w1=self.w1()
        w1["objects"][0]["class_id"]=108
        with self.assertRaises(ValueError):
            m.combine_same_export(w1,self.tex())
    def test_malformed_instance_rejected(self):
        w1=self.w1()
        w1["export_instance"]="not-a-real-uuid"
        with self.assertRaises(ValueError):
            m.combine_same_export(w1,self.tex())
    def test_material_scope_missing_fails_closed(self):
        c=self.good_counters()
        c["materials_compared"]=40
        with self.assertRaises(ValueError):
            m.aggregate(c)
    def test_unknown_counter_fails_closed(self):
        c=self.good_counters()
        del c["wrong_internal_targets"]
        with self.assertRaises(ValueError):
            m.aggregate(c)
    def test_matching_parity_is_scoped_not_android_confirmation(self):
        result=m.aggregate(self.good_counters())
        self.assertEqual(result["status"],"SCOPED_TEXTURE_UV_MATCH")
        self.assertFalse(result["all_external_texture_targets_proven"])
        self.assertFalse(result["android_device_or_pixel_proven"])
        self.assertFalse(result["full_game_source_coverage_verified"])
    def test_uv_drift_remains_detectable(self):
        c=self.good_counters()
        c["uv_transform_value_mismatches"]=1
        c["all_uv_transforms_verified"]=False
        c["source_slots_faithful_with_resolved_scope"]=False
        self.assertEqual(m.aggregate(c)["status"],"SCOPED_TEXTURE_UV_MISMATCH")
    def test_scope_incomplete_missing_texture_slot_detected(self):
        c=self.good_counters()
        c["slots_compared"]=226
        self.assertEqual(m.aggregate(c)["status"],"SCOPED_TEXTURE_UV_MISMATCH")
    def test_no_raw_future_fields_copied(self):
        c=self.good_counters()
        c["private_material_names"]=["DoNotLeak"]
        self.assertNotIn("private_material_names",m.aggregate(c))
if __name__=="__main__":
    unittest.main()
