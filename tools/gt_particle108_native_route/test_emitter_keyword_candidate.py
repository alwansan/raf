import unittest
import numpy as np
from tools.gt_particle108_native_route.emitter_keyword_candidate import compose,route_rows,classify,safe_receipt,Reject,BG,SIZE
class KeywordCandidate(unittest.TestCase):
    def test_exact_lattice_and_strict_router(self):
        pairs={(0,0):2,(0,1):0,(1,0):3,(1,1):1}
        a=["HLSLPROGRAM\n#pragma target 5.0\n#pragma vertex gt_vs_main\n#pragma fragment gt_fs_main\nprogram"+str(i)+"\nENDHLSL" for i in range(4)]
        shader,rows=compose(a,("A_TEST","B_TEST"),pairs)
        self.assertIn("!defined(A_TEST) && defined(B_TEST)\nprogram0",shader)
        self.assertIn("#error Unmapped_original_keyword_set",shader)
        self.assertEqual(rows[2]["bits"],[0,0])
        with self.assertRaises(Reject):route_rows(("A_TEST","B_TEST"),{(0,0):0})
    def test_partial_receipt_never_admits_route(self):
        j=dict(index=0,phase="permutation_incomplete",submissions=5,source_declared_switches=2,
               variants=[dict(index=1,phase="reference_properties",failure_category="InvalidOperationException",submissions=1)])
        x=safe_receipt(j,0)
        self.assertFalse(x["strict_editor_receipt"])
        self.assertEqual(x["variants"][0]["phase"],"reference_properties")
        self.assertEqual(x["submissions"],5)
    def test_receipt_rejects_global_override_and_missing_variant(self):
        j=dict(index=0,phase="complete",submissions=14,source_declared_switches=2,source_local_bit_matches=2,source_string_bit_matches=2,
               source_global_override_conflicts=0,completed=True,saved_keywords_match=True,material_properties_match=True,source_keywords_unchanged=True,source_global_keywords_unchanged=True)
        j["variants"]=[dict(index=i,phase="complete",completed=True,submissions=3,routed_bits_match=True,marker_bits_match=True,reference_properties_match=True,routed_properties_match=True,reference_shader_errors=0,marker_shader_errors=0) for i in range(4)]
        self.assertTrue(safe_receipt(j,0)["strict_editor_receipt"])
        j["source_global_override_conflicts"]=1
        self.assertFalse(safe_receipt(j,0)["strict_editor_receipt"])
        j["source_global_override_conflicts"]=0;j["variants"].pop()
        self.assertFalse(safe_receipt(j,0)["strict_editor_receipt"])
    def test_actual_saved_and_route_reference(self):
        clear=np.tile(BG,(SIZE,SIZE,1));rows={}
        for i in range(4):
            pixels=clear.copy();pixels[4:12,4:12,:3]=(.1*i,.6,.4)
            marker=clear.copy();marker[4:12,4:12]=[(i+1)/8,.375,.625,1]
            rows[i]=(pixels,pixels.copy(),marker)
        self.assertTrue(classify(clear,rows[2][0],rows,2)["route_probe_verified"])
        self.assertFalse(classify(clear,rows[1][0],rows,2)["route_probe_verified"])
        rows[3][1][5,5,0]=.9
        self.assertFalse(classify(clear,rows[2][0],rows,2)["route_probe_verified"])
if __name__=="__main__":unittest.main()
