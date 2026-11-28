import unittest
import numpy as np
from tools.gt_particle108_native_route.emitter_vertex_lanes import classify,coverage,shader,Reject,CLEAR,MARKER
class VertexLanes(unittest.TestCase):
    def test_physical_and_defaults_independent(self):
        cpu=np.array([[.1,.2,.3,0],[.4,.5,.6,0],[.7,.8,.9,0],[.2,.3,.4,0]])
        p=np.array([[.1,.2,.3,1],[.4,.5,.6,1]])
        r=classify(cpu,3,15,p)
        self.assertTrue(r["physical_values_match"] and r["used_missing_defaults_match"])
        p[0,3]=0
        self.assertFalse(classify(cpu,3,15,p)["used_missing_defaults_match"])
        p[0,0]=.9
        self.assertFalse(classify(cpu,3,15,p)["physical_values_match"])
    def test_missing_uv_component_fill_and_unused(self):
        cpu=np.zeros((4,4));p=np.array([[0,0,0,1]])
        self.assertTrue(classify(cpu,2,15,p)["used_missing_defaults_match"])
        self.assertEqual(classify(cpu,2,3,p)["used_lanes_missing"],0)
    def test_marker_requires_visible_and_clear(self):
        p=np.tile(CLEAR,(256,1));p[:32]=MARKER
        self.assertEqual(coverage(p).sum(),32)
        p[50]=0
        with self.assertRaises(Reject):coverage(p)
    def test_shader_original_float_semantics_only(self):
        req=[dict(semantic=s,index=0,mask=15,used_mask=15,component_type=3) for s in ("POSITION","COLOR","TEXCOORD")]
        self.assertIn("float4 a2:TEXCOORD0",shader(req))
        req[0]["component_type"]=1
        with self.assertRaises(Reject):shader(req)
if __name__=="__main__":unittest.main()
