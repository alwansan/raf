import unittest
from gfxlab.tools.multi_model_transport import scalar_color,uv_pair,ALLOWED_ROLES,MAX_TOTAL_CHUNKS
class MultiPackingTest(unittest.TestCase):
    def test_tint_original_bounds(self):
        self.assertEqual(scalar_color({"r":1,"g":0.5,"b":0.0,"a":1}),[1,0.5,0,1])
        with self.assertRaises(ValueError):scalar_color({"r":float("nan"),"g":0,"b":0,"a":1})
    def test_tint_not_invented(self):
        self.assertIsNone(scalar_color(None))
    def test_uv_original(self):
        self.assertEqual(uv_pair({"m_Scale":{"x":2,"y":3}},"m_Scale",[1,1]),[2,3])
        with self.assertRaises(ValueError):uv_pair({"m_Offset":{"x":1}},"m_Offset",[0,0])
    def test_bounds(self):
        self.assertLessEqual(MAX_TOTAL_CHUNKS,24)
        self.assertEqual(ALLOWED_ROLES,{"basecolor","normal","metallic"})
if __name__=="__main__":unittest.main()
