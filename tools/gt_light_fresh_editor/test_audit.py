import unittest
from tools.gt_light_fresh_editor import audit as a
from tools.gt_light_exact_editor import audit as prior
from tools.gt_light_same_export.audit import Rejected

class FreshControls(unittest.TestCase):
    def stage(self):
        return dict(scene_sha256="a"*64,scene_meta_sha256="b"*64,source_scene_sha256=prior.SOURCE_SHA,
                    selected_objects=42,same_export_scene_copy_exact=True,other_original_assets_staged=0,
                    scene_dependency_closure_claimed=False,import_executed=False)
    def test_fresh_not_historical(self):
        self.assertEqual(a.validate_fresh_stage(self.stage()),(False,False))
        with self.assertRaises(Rejected):prior.validate_stage(self.stage())
        for k,v in (("source_scene_sha256","0"*64),("selected_objects",41),("other_original_assets_staged",1),
                    ("same_export_scene_copy_exact",False),("scene_sha256","bad")):
            x=self.stage();x[k]=v
            with self.assertRaises(Rejected):a.validate_fresh_stage(x)
    def test_trs_parent_scale_translation(self):
        parent=dict(position=[1,2,3],rotation=[0,0,0,1],scale=[2,3,4])
        child=dict(position=[1,1,1],rotation=[0,0,0,1],scale=[1,1,1])
        m=a.product(a.trs(parent),a.trs(child))
        self.assertEqual([m[3],m[7],m[11]],[3,5,7])
        self.assertEqual([m[0],m[5],m[10]],[2,3,4])
    def test_rotation(self):
        from math import sqrt
        n=dict(position=[0,0,0],rotation=[0,sqrt(.5),0,sqrt(.5)],scale=[1,1,1])
        m=a.trs(n)
        self.assertAlmostEqual(m[2],1.)
        self.assertAlmostEqual(m[10],0.)
    def test_world_receipt_fail_closed(self):
        r=dict(run_id="1-2",commitment_sha256="a"*64,private_guard=True,world_rows=3,world_checks=12,
               world_mismatches=0,light_owner_match=True,light_active_match=True,status="PASS")
        self.assertTrue(a.validate_world_receipt(r,"1-2","a"*64))
        for k,v in (("run_id","1-3"),("private_guard",False),("world_checks",11),("world_mismatches",1),("light_owner_match",False)):
            x=dict(r);x[k]=v
            with self.assertRaises(Rejected):a.validate_world_receipt(x,"1-2","a"*64)
if __name__=="__main__":unittest.main()
