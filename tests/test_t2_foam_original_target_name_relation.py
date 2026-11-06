import unittest
from scripts.t2_foam_original_target_name_relation import safe_name_comparison, shader_name


class TargetNameRelationTests(unittest.TestCase):
    def test_one_exact_and_one_different(self):
        r=safe_name_comparison("Foam",[
            (("owner",1),"Foam",False),(("owner",2),"Other",False)])
        self.assertEqual(r["target_exact_Foam_name_matches"],1)
        self.assertEqual(r["typed_external_Shader_targets"],2)
        self.assertFalse(r["name_match_is_Unity_GUID_runtime_identity"])

    def test_independent_negative_both_parsed(self):
        r=safe_name_comparison("Foam",[
            (("owner",1),"A",False),(("owner",2),"B",False)])
        self.assertEqual((r["target_exact_Foam_name_matches"],
                          r["target_original_shader_name_unreadable"]), (0,0))
        self.assertFalse(r["Android_Adreno_water_pixels_verified"])

    def test_unreadable_name_means_unknown(self):
        r=safe_name_comparison("Foam",[(("owner",1),None,False)])
        self.assertEqual(r["target_original_shader_name_unreadable"],1)

    def test_invalid_foam_names(self):
        for name in ("",None,"a\x00b",42,"z"*513):
            with self.subTest(name=str(name)[:7]),self.assertRaises(ValueError):
                safe_name_comparison(name,[(("owner",1),"X",False)])

    def test_duplicate_external_target_rejected(self):
        with self.assertRaises(ValueError):
            safe_name_comparison("Foam",[
                (("owner",1),"Foam",False),(("owner",1),"X",False)])

    def test_invalid_pathid(self):
        for pathid in (0,-1,True,"1",None):
            with self.subTest(pathid=pathid),self.assertRaises(ValueError):
                safe_name_comparison("Foam",[(("owner",pathid),"X",False)])

    def test_invalid_original_target_name(self):
        for name in ("","a\x00b",42,"z"*513):
            with self.subTest(name=str(name)[:7]),self.assertRaises(ValueError):
                safe_name_comparison("Foam",[(("owner",1),name,False)])

    def test_raw_equality_boolean_only(self):
        with self.assertRaises(ValueError):
            safe_name_comparison("Foam",[(("owner",1),"Foam",1)])

    def test_unbounded_target_count(self):
        with self.assertRaises(ValueError):
            safe_name_comparison("Foam",[])
        with self.assertRaises(ValueError):
            safe_name_comparison("Foam",[
                (("owner",x),"Other",False) for x in range(1,18)])

    def test_original_parsed_shader_tree_only(self):
        self.assertEqual(shader_name({"m_ParsedForm":{"m_Name":"Foam"}}),"Foam")
        self.assertIsNone(shader_name({"m_Name":"Foam"}))
        self.assertIsNone(shader_name({"m_ParsedForm":{"m_Name":""}}))
        self.assertIsNone(shader_name({"m_ParsedForm":{"m_Name":"a\x00b"}}))
        self.assertIsNone(shader_name(None))

if __name__=="__main__":
    unittest.main()
