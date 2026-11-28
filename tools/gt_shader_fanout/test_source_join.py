import copy
import unittest
from tools.gt_shader_fanout import source_join as j

def fixture():
    def guid(i):return f"{i:032x}"
    # Source 921 + 20 positive weights, exact 1633 typed slots.
    weights=[921,100]+[32]*18+[36]
    q=[dict(original_owner="private",original_shader_path_id=i+1,
            original_scene_renderer_material_slots=n,exported_Shader_GUID=guid(i+1),
            program_status="dummy" if i<3 else "vendor_non_dummy")
       for i,n in enumerate(weights)]
    s=dict(status=j.priority.STATUS,source_original_6_scene_sha_authenticated=True,
           same_instance_original_Shader48_export_trace_verified=True,private_priority_queue_complete=True,
           same_instance_original_source_count=21,original_typed_renderer_material_slots=1633,
           still_dummy_distinct_original_Shader48_targets=3,still_dummy_original_renderer_material_slots=1053)
    def group(n,m):return dict(material_documents=m,renderer_slots=n,scene_slots=n,prefab_slots=0,
                               other_slots=0,renderer_objects=n,exclusive_dummy_renderer_objects=n)
    ranked=[(guid(2),group(20,3)),(guid(100),group(11,2)),(guid(1),group(5,1))]
    e=dict(status=j.audit.STATUS,dummy_shader_guid_targets=3,counts=dict(slot_dummy=36,material_dummy=6),
           snapshot_commitment_sha256="fixture")
    return q,s,e,ranked

class Tests(unittest.TestCase):
    def test_exact_guid_intersection_and_different_rank(self):
        q,s,e,r=fixture();d=j.join(q,s,e,r)
        self.assertEqual(d["exact_guid_intersection"],2)
        self.assertEqual(d["joint_anonymous_priority"][0]["source_rank"],2)
        self.assertEqual(d["source_slots_without_export_material_fanout"],32)
        self.assertEqual(d["export_dummy_slots_outside_selected_source_scope"],11)
        self.assertFalse(d["source_top_dummy_is_actual_export_top"])
        self.assertNotIn("private",str(d).replace("private_ids_paths_or_payload_published",""))
    def test_source_collision_rejected(self):
        q,s,e,r=fixture();q[1]["exported_Shader_GUID"]=q[0]["exported_Shader_GUID"]
        with self.assertRaises(ValueError):j.join(q,s,e,r)
    def test_duplicate_actual_guid_rejected(self):
        q,s,e,r=fixture();r[1]=(r[0][0],r[1][1])
        with self.assertRaises(ValueError):j.join(q,s,e,r)
    def test_non_dummy_class_conflict_rejected(self):
        q,s,e,r=fixture();r[1]=(q[4]["exported_Shader_GUID"],r[1][1])
        with self.assertRaises(ValueError):j.join(q,s,e,r)
    def test_source_count_and_export_count_rejected(self):
        q,s,e,r=fixture();s["still_dummy_original_renderer_material_slots"]=1
        with self.assertRaises(ValueError):j.join(q,s,e,r)
        q,s,e,r=fixture();e["counts"]["slot_dummy"]=37
        with self.assertRaises(ValueError):j.join(q,s,e,r)
    def test_unauthenticated_queue_rejected(self):
        q,s,e,r=fixture();s["private_priority_queue_complete"]=False
        with self.assertRaises(ValueError):j.join(q,s,e,r)
    def test_no_slot_equality_claim(self):
        q,s,e,r=fixture();d=j.join(q,s,e,r)
        self.assertFalse(d["source_to_export_renderer_assignment_parity"])
        self.assertFalse(d["white_mesh_pixels_verified"])
if __name__=="__main__":unittest.main()
