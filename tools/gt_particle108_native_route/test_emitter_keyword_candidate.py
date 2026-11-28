import unittest
import numpy as np
from tools.gt_particle108_native_route.emitter_keyword_candidate import compose,route_rows,classify,Reject,BG,SIZE
class KeywordCandidate(unittest.TestCase):
    def test_exact_lattice_and_strict_router(self):
        pairs={(0,0):2,(0,1):0,(1,0):3,(1,1):1}
        a=["HLSLPROGRAM\n#pragma target 5.0\n#pragma vertex gt_vs_main\n#pragma fragment gt_fs_main\nprogram"+str(i)+"\nENDHLSL" for i in range(4)]
        shader,rows=compose(a,("A_TEST","B_TEST"),pairs)
        self.assertIn("!defined(A_TEST) && defined(B_TEST)\nprogram0",shader)
        self.assertIn("#error Unmapped_original_keyword_set",shader)
        self.assertEqual(rows[2]["bits"],[0,0])
        with self.assertRaises(Reject):route_rows(("A_TEST","B_TEST"),{(0,0):0})
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
