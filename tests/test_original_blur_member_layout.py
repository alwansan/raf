import copy
import unittest
from scripts.probe_original_blur_member_layout import observe

class MemberLayout(unittest.TestCase):
    def common(self):
        return {"m_ConstantBufferBindings": [{"m_NameIndex": 7, "m_Index": 0}],
                "m_ConstantBuffers": [{"m_NameIndex": 7, "m_Size": 80, "m_IsPartialCB": False,
                  "m_MatrixParams": [{"m_Index": 0, "m_ArraySize": 0, "m_Type": 0, "m_RowCount": 4}],
                  "m_VectorParams": [{"m_Index": 64, "m_ArraySize": 0, "m_Type": 0, "m_Dim": 4}],
                  "m_StructParams": []}]}
    def test_numeric_layout_is_not_claimed_as_verified(self):
        row = observe(self.common())[0]
        self.assertEqual([x["candidate_byte_end"] for x in row["members"]], [64,80])
        self.assertFalse(row["candidate_byte_offset_model_verified"])
        self.assertNotIn("m_NameIndex", str(row))
        self.assertEqual(row["candidate_overlapping_adjacent_members"], 0)
    def test_outside_allocation_remains_observation(self):
        value = self.common()
        value["m_ConstantBuffers"][0]["m_Size"] = 64
        self.assertFalse(observe(value)[0]["members"][1]["candidate_within_allocation"])
    def test_overlap_recorded(self):
        value = self.common()
        value["m_ConstantBuffers"][0]["m_VectorParams"][0]["m_Index"] = 48
        self.assertEqual(observe(value)[0]["candidate_overlapping_adjacent_members"], 1)
    def test_unknown_and_ambiguous_schema_rejected(self):
        for mutate in (lambda c: c["m_ConstantBufferBindings"].append(copy.deepcopy(c["m_ConstantBufferBindings"][0])),
                       lambda c: c["m_ConstantBuffers"][0]["m_VectorParams"][0].update(m_Dim=5),
                       lambda c: c["m_ConstantBuffers"][0]["m_VectorParams"][0].update(m_ArraySize=-1),
                       lambda c: c["m_ConstantBuffers"][0]["m_VectorParams"][0].update(m_Index=True)):
            value = self.common()
            mutate(value)
            with self.assertRaises(ValueError):
                observe(value)

if __name__ == "__main__":
    unittest.main()
