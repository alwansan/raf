import unittest
from tools.gt_top_resource_closure import selected_probe_context as q
class ProbeContextTests(unittest.TestCase):
    def test_source_row_selection_and_exact_names(self):
        rows=[dict(role="fs",kind="unresolved",name="_Other"+str(i),mode=i+2) for i in range(40)]
        rows[22]["name"]="unity_SpecCube0_BoxMax"
        rows[24]["name"]="unity_SpecCube0_BoxMax_fake"
        rows[37].update(name="unity_SpecCube0",kind="texture_dimensions")
        a=q.select_rows(rows)
        self.assertEqual([r["source_ordinal"] for r in a if r["previous_nonfinite"]],list(q.TARGET))
        self.assertEqual(a[0]["semantic"],"reflection_box_max")
        self.assertEqual(a[-1]["semantic"],"reflection_cube")
        self.assertNotIn(24,[r["source_ordinal"] for r in a])
        rows[22]["role"]="vs"
        with self.assertRaises(ValueError):q.select_rows(rows)
    def test_pointer_state_never_claims_resolution(self):
        self.assertEqual(q.pointer_state({"m_FileID":1,"m_PathID":123}),"nonnull")
        self.assertEqual(q.pointer_state({"m_FileID":0,"m_PathID":0}),"null")
        self.assertEqual(q.pointer_state({"m_PathID":1}),"unknown")
        self.assertEqual(q.pointer_state(None),"absent")
    def test_exact_semantic_mapping(self):
        self.assertEqual(q.semantic("unity_SpecCube1_BoxMin"),"reflection_box_min")
        self.assertEqual(q.semantic("unity_ProbeVolumeMin"),"light_volume_min")
        self.assertEqual(q.semantic("unity_ProbeVolumeSizeInv"),"light_volume_size_inverse")
        self.assertEqual(q.semantic("unity_ProbeVolumeSizeInv2"),"other_unresolved")
if __name__=="__main__":unittest.main()
