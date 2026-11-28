"""Authored controls: owner/offset classification and strict stage/resource contract."""
import unittest
from tools.gt_skybox_offset_differential import audit as a
from tools.gt_light_same_export.audit import Rejected

def source(name="AUTHORED",offset=16):
    return {"name":"$Globals","source_slot":0,"members":[{"name":name,"index":offset}],"structs":[]}

def reflect(*blocks):
    return {"ubos":[{"name":name,"type":str(i)} for i,(name,_) in enumerate(blocks)],
            "types":{str(i):{"members":[{"name":n,"offset":off} for n,off in fields]}
                     for i,(_,fields) in enumerate(blocks)}}

class OffsetControls(unittest.TestCase):
    def test_exact_offset(self):
        x=a.profile(reflect(("gt_vs_raft921_cb0_Globals",[("AUTHORED",16)])),[source()],"vs")
        self.assertEqual((x["exact_owner_offset"],x["missing_from_owner"]),(1,0))

    def test_wrong_offset(self):
        x=a.profile(reflect(("gt_vs_raft921_cb0_Globals",[("AUTHORED",32)])),[source()],"vs")
        self.assertEqual(x["wrong_owner_offset"],1)

    def test_moved_member_is_not_offset_match(self):
        x=a.profile(reflect(("Other",[("AUTHORED",16)])),[source()],"vs")
        self.assertEqual((x["found_in_other_block"],x["exact_owner_offset"],x["found_in_other_block_same_offset"]),(1,0,1))

    def test_missing(self):
        x=a.profile(reflect(("Other",[])),[source()],"vs")
        self.assertEqual(x["absent_from_all_blocks"],1)

    def test_duplicate_block_rejected(self):
        with self.assertRaises(Rejected):
            a.profile(reflect(("Other",[]),("Other",[])),[source()],"vs")

    def test_duplicate_field_rejected(self):
        with self.assertRaises(Rejected):
            a.profile(reflect(("Other",[("AUTHORED",0),("AUTHORED",4)])),[source()],"vs")

    def test_original_shared_global_names(self):
        x=a.shared_global_members([[source(offset=0)],[source(offset=16)]])
        self.assertEqual(x["shared_global_names_different_offsets"],1)

    def test_resource_name_and_type_parity(self):
        x={"separate_images":[{"name":"AUTHORED","type":"texture2D"}]}
        self.assertEqual(a.resource_parity(x,x),1)
        for bad in ({"separate_images":[{"name":"OTHER","type":"texture2D"}]},
                    {"separate_images":[{"name":"AUTHORED","type":"textureCube"}]},{}):
            with self.assertRaises(Rejected): a.resource_parity(bad,x)

    def test_duplicate_resource_rejected(self):
        x={"separate_images":[{"name":"AUTHORED","type":"texture2D"}]*2}
        with self.assertRaises(Rejected): a.resources(x)

    def test_exclusive_stage_source(self):
        s=a.isolated_body("AUTHORED_VERTEX","AUTHORED_FRAGMENT")
        self.assertIn("defined(SHADER_STAGE_VERTEX) && !defined(SHADER_STAGE_FRAGMENT)",s)
        self.assertIn("defined(SHADER_STAGE_FRAGMENT) && !defined(SHADER_STAGE_VERTEX)",s)
        self.assertIn("#error GT_SKYBOX_STAGE_SELECTION",s)
        self.assertEqual(s.count("AUTHORED_VERTEX"),1)
        self.assertEqual(s.count("AUTHORED_FRAGMENT"),1)

    def test_unsafe_stage_body_rejected(self):
        with self.assertRaises(Rejected): a.isolated_body("","#error GT_SKYBOX_STAGE_SELECTION")

if __name__=="__main__":
    unittest.main()
