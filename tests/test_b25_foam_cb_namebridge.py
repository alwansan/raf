"""B25 original Foam private CB name-index bridge synthetic fail-closed controls."""
import copy
import hashlib
import unittest
from scripts.b24_original_foam_stage_translation import TARGET
from scripts.b25_foam_cb_namebridge import inspect_parsed, original_name_registry

def program(stage, pass_index):
    layout = ((160,2,0),(176,0,1),(368,0,1)) if stage == 1 else ((160,2,0),)
    buffers, refs = [], []
    for slot, (size, vectors, matrices) in enumerate(layout):
        if pass_index == 1 and slot == 0:
            vectors = 1
        buffers.append(dict(m_Size=size, m_IsPartialCB=True, m_NameIndex=slot,
                            m_VectorParams=[0]*vectors, m_MatrixParams=[0]*matrices))
        refs.append(dict(m_NameIndex=slot, m_Index=slot, m_ArraySize=1))
    return dict(m_PlayerSubPrograms=[[dict(m_BlobIndex=1,m_KeywordIndices=[])]],
                m_ParameterBlobIndices=[[0]],
                m_CommonParameters=dict(m_ConstantBuffers=buffers,m_ConstantBufferBindings=refs))

def fixture():
    result=[]
    for index in (0,1):
        result.append(dict(m_Type=0,
            m_NameIndices=[["FoamCB0",0],["FoamCB1",1],["FoamCB2",2]],
            progVertex=program(1,index),progFragment=program(0,index)))
    return dict(m_Name=TARGET,m_SubShaders=[dict(m_Passes=result)])

class FoamNameTests(unittest.TestCase):
    def test_four_stages_resolve_eight_original_cb_name_slots(self):
        x=inspect_parsed(fixture())
        self.assertEqual(x["original_passes"],2)
        self.assertEqual(x["authenticated_stage_count"],4)
        self.assertEqual(x["matched_constant_buffer_bindings"],8)
        self.assertFalse(x["private_name_values_published"])
        self.assertFalse(x["shaderlab_cb_rebinding_installed"])
        sha=hashlib.sha256(b"FoamCB0").hexdigest()
        self.assertEqual(x["passes"][0]["stages"][0]["constant_buffers"][0]["name_sha256"],sha)
        self.assertEqual(x["passes"][1]["stages"][0]["constant_buffers"][0]["vector_member_count"],1)

    def test_original_dict_pair_schema(self):
        self.assertEqual(original_name_registry([{"first":"FoamCB0","second":12}]),{12:"FoamCB0"})

    def test_reject_duplicate_name_index(self):
        with self.assertRaisesRegex(ValueError,"ambiguous name index"):
            original_name_registry([["CB0",0],["CB1",0]])

    def test_reject_duplicate_names(self):
        with self.assertRaisesRegex(ValueError,"duplicate CB name"):
            original_name_registry([["CB0",0],["CB0",1]])

    def test_reject_unsafe_name(self):
        for value in ("bad name", "1name", "evil]\n", "", "x"*257):
            with self.assertRaises(ValueError):
                original_name_registry([[value,0]])

    def test_reject_bad_row(self):
        for row in (["one"], {"x":"FoamCB0","y":0}, "name", [None,0]):
            with self.assertRaises(ValueError):
                original_name_registry([row])

    def test_reject_bad_registry_bounds(self):
        for rows in ([], "text", [("CB",0)]*8193):
            with self.assertRaises(ValueError):
                original_name_registry(rows)

    def test_wrong_pass_count(self):
        x=fixture()
        x["m_SubShaders"][0]["m_Passes"].pop()
        with self.assertRaisesRegex(ValueError,"two-pass count"):
            inspect_parsed(x)

    def test_missing_original_index_rejected(self):
        x=fixture()
        x["m_SubShaders"][0]["m_Passes"][0]["m_NameIndices"]=[["other",3]]
        with self.assertRaisesRegex(ValueError,"name index"):
            inspect_parsed(x)

    def test_nonmatching_original_binding_index_rejected(self):
        x=fixture()
        x["m_SubShaders"][0]["m_Passes"][0]["progVertex"]["m_CommonParameters"]["m_ConstantBufferBindings"][0]["m_NameIndex"]=1
        with self.assertRaises(ValueError):
            inspect_parsed(x)

    def test_incorrect_original_pass1_partial_vector_count_rejected(self):
        x=fixture()
        x["m_SubShaders"][0]["m_Passes"][1]["progFragment"]["m_CommonParameters"]["m_ConstantBuffers"][0]["m_VectorParams"]=[0,0]
        with self.assertRaisesRegex(ValueError,"partial-CB"):
            inspect_parsed(x)

    def test_incorrect_stage_identity_rejected(self):
        x=fixture()
        x["m_Name"]="Fake/Foam"
        with self.assertRaisesRegex(ValueError,"identity"):
            inspect_parsed(x)

    def test_original_second_pass_may_have_distinct_name_by_index(self):
        x=fixture()
        x["m_SubShaders"][0]["m_Passes"][1]["m_NameIndices"][0][0]="DistinctCB"
        r=inspect_parsed(x)
        a=r["passes"][0]["stages"][0]["constant_buffers"][0]["name_sha256"]
        b=r["passes"][1]["stages"][0]["constant_buffers"][0]["name_sha256"]
        self.assertNotEqual(a,b)

if __name__=="__main__":
    unittest.main()
