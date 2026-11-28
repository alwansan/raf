import unittest
from collections import Counter
from tools.gt_particle108_native_route import probe as p
class NativeRouteTests(unittest.TestCase):
    def test_sample_operands_require_matching_original_sampler(self):
        self.assertEqual(p.slot_usage([(3,1,69),(3,1,72)],{3:"_A"},{1:"sampler_A"}),Counter({"_A":2}))
        with self.assertRaisesRegex(ValueError,"sample_operand_name_pair_mismatch"):
            p.slot_usage([(3,1,69)],{3:"_A"},{1:"sampler_B"})
        with self.assertRaises(ValueError):p.slot_usage([(4,1,69)],{3:"_A"},{1:"sampler_A"})
    def test_keyword_route_and_target_identity_distinguish_unused_or_invalid(self):
        routes={(0,0):0,(1,0):1,(0,1):2,(1,1):3}
        uses={0:Counter({"_Other":1}),1:Counter({"_A":2,"_Other":1,"_Global":3}),2:Counter(),3:Counter({"_A":4})}
        uv=(1.,1.,0.,0.);slots={"_A":((0,42),uv),"_Other":((0,99),uv)}
        src=p.keywords({"m_ShaderKeywords":"ONE EXTRA"})
        dst=p.keywords({"m_ValidKeywords":[],"m_InvalidKeywords":["ONE","EXTRA"]})
        row=p.classify_material(slots,"owner",("owner",42),src,dst,("ONE","TWO"),routes,uses)
        self.assertTrue(row["saved_keyword_route_equal"])
        self.assertFalse(row["exported_valid_keyword_route_equal"])
        self.assertEqual(row["selected_native_sample_instructions"],2)
        self.assertEqual(row["selected_native_valid_export_sample_instructions"],0)
        self.assertEqual(row["outside_saved_material_sample_instructions"],3)
        wrong=p.classify_material(slots,"other",("owner",42),src,dst,("ONE","TWO"),routes,uses)
        self.assertEqual(wrong["selected_native_slots"],0)
        with self.assertRaises(ValueError):p.choose_route({"ONE"},("ONE","TWO"),{(0,0):0})
        with self.assertRaises(ValueError):p.keywords({"m_ValidKeywords":["ONE"],"m_InvalidKeywords":["ONE"]})
if __name__=="__main__":unittest.main()
