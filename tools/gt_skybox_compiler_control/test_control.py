import unittest
from tools.gt_skybox_compiler_control import control as c
def fixture():
    v=[(None,0,{"m_KeywordIndices":[],"m_BlobIndex":0})]
    return {"m_KeywordNames":[],"m_KeywordFlags":[],"m_SubShaders":[{"m_Passes":[{"m_Type":0,"progVertex":v,"progFragment":[]}]}]}
def rows(p):return p
class Control(unittest.TestCase):
    def test_only_pragma(self):
        src=b"HLSLPROGRAM\n#pragma use_dxc vulkan\nfloat4 original;\nENDHLSL\n"
        self.assertEqual(c.remove_dxc(src),b"HLSLPROGRAM\nfloat4 original;\nENDHLSL\n")
    def test_pragma_missing(self):
        with self.assertRaises(ValueError):c.remove_dxc(b"float4 original;")
    def test_duplicate_pragma(self):
        with self.assertRaises(ValueError):c.remove_dxc(c.DXC_LINE*2)
    def test_other_dxc(self):
        with self.assertRaises(ValueError):c.remove_dxc(c.DXC_LINE+b"#pragma use_dxc\n")
    def test_non_standalone(self):
        with self.assertRaises(ValueError):c.remove_dxc(b"x"+c.DXC_LINE)
    def test_fallback(self):
        tab,fall,n=c.validate_route_tables(fixture(),rows)
        self.assertTrue(fall);self.assertEqual(tab["progVertex"],tab["progFragment"]);self.assertEqual(n,0)
    def test_active_route(self):
        f=fixture();f["m_SubShaders"][0]["m_Passes"][0]["progVertex"][0][2]["m_KeywordIndices"]=[0]
        with self.assertRaises(ValueError):c.validate_route_tables(f,rows)
    def test_duplicate_route(self):
        f=fixture();v=f["m_SubShaders"][0]["m_Passes"][0]["progVertex"];v.append(v[0])
        with self.assertRaises(ValueError):c.validate_route_tables(f,rows)
    def test_unexpected_stage(self):
        f=fixture();p=f["m_SubShaders"][0]["m_Passes"][0];p["progGeometry"]=p["progVertex"]
        with self.assertRaises(ValueError):c.validate_route_tables(f,rows)
    def test_non_normal(self):
        f=fixture();f["m_SubShaders"][0]["m_Passes"][0]["m_Type"]=1
        with self.assertRaises(ValueError):c.validate_route_tables(f,rows)
if __name__=="__main__":unittest.main()
