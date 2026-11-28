import unittest
from tools.gt_skybox_actual_abi import audit as a
class Controls(unittest.TestCase):
    def test_exact_map(self):
        self.assertTrue(a.map_profile({"x":4},{"x":4})["exact_map"])
    def test_name_not_offset(self):
        self.assertFalse(a.map_profile({"x":4},{"x":8})["exact_map"])
    def test_extra(self):
        self.assertEqual(a.map_profile({"x":4},{"x":4,"y":8})["extra"],1)
    def test_missing_owner(self):
        r=a.map_profile({("old","x"):4},{("new","x"):4})
        self.assertEqual((r["exact"],r["missing"],r["extra"]),(0,1,1))
    def test_stride(self):
        def r(stride):return {"ubos":[{"name":"B","type":"T"}],"types":{"T":{"members":[{"name":"x","offset":0,"type":"mat4","matrix_stride":stride}]}}}
        self.assertFalse(a.map_profile(a.members(r(16)),a.members(r(32)))["exact_map"])
    def test_duplicate(self):
        r={"ubos":[{"name":"B","type":"T"}],"types":{"T":{"members":[{"name":"x","offset":0},{"name":"x","offset":4}]}}}
        with self.assertRaises(ValueError):a.members(r)
    def test_serialized_member(self):
        p={"m_CommonParameters":{"m_ConstantBuffers":[{"m_NameIndex":0,"m_VectorParams":[{"m_NameIndex":1,"m_Index":16}]}],
           "m_ConstantBufferBindings":[{"m_NameIndex":0,"m_Index":2}],"m_TextureParams":[{"m_NameIndex":2}]}}
        m,t,b,v=a.metadata_members(p,(None,0,{}),[],{0:"B",1:"x",2:"Tex"})
        self.assertEqual(m,{("B","x"):16});self.assertEqual(t,{"Tex"});self.assertEqual(b,{"B":2});self.assertFalse(v)
    def test_serialized_wrong_offset(self):
        p={"m_CommonParameters":{"m_ConstantBuffers":[{"m_NameIndex":0,"m_VectorParams":[{"m_NameIndex":1,"m_Index":32}]}]}}
        m,_,_,_=a.metadata_members(p,(None,0,{}),[],{0:"B",1:"x"})
        self.assertFalse(a.map_profile({("B","x"):16},m)["exact_map"])
if __name__=="__main__":unittest.main()
