import unittest
from gfxlab.tools.shears_texture_readiness import pairs,classify_standard,STANDARD_SEMANTICS

class ShearsTextureReadinessTests(unittest.TestCase):
    def test_typetree_material_pair(self):
        r=pairs([{"m_First":"_MainTex","m_Second":{"m_Texture":{"m_FileID":0,"m_PathID":3}}}])
        self.assertEqual(len(r),1)
        self.assertEqual(r[0][0],"_MainTex")
    def test_public_known_semantics_only(self):
        self.assertEqual(classify_standard("_MainTex"),"basecolor")
        self.assertEqual(classify_standard("_BumpMap"),"normal")
        self.assertEqual(classify_standard("_EmissionMap"),"emission")
        self.assertEqual(classify_standard("private-nonsense"),"unknown")
    def test_no_invented_texture(self):
        self.assertEqual(pairs([["_MainTex",{"m_Texture":{"m_FileID":0,"m_PathID":0}}]])[0][0],"_MainTex")
    def test_duplicates_rejected(self):
        with self.assertRaises(ValueError):
            pairs([["_MainTex",1],["_MainTex",2]])
    def test_malformed_rejected(self):
        for row in ["bad", [{"nonsense":123}], [1]]:
            with self.assertRaises(ValueError):
                pairs(row)
if __name__=="__main__":
    unittest.main()
