"""Authored negative controls only; actual source context is measured separately."""
import unittest
from tools.gt_particle108_native_route import emitter_scene_context as s

class SceneContextTest(unittest.TestCase):
    def setUp(self):
        self.routes = {(0,0):0,(0,1):1,(1,0):2,(1,1):3}

    def test_all_wrong_routes_rejected(self):
        self.assertEqual(s.reject_wrong_routes(self.routes), 12)
        with self.assertRaises(s.Reject):
            s.exact_variant(self.routes, (1,0), 0)

    def test_missing_and_invalid_routes_rejected(self):
        with self.assertRaises(s.Reject):
            s.exact_variant({(0,0):0}, (0,0), 0)
        for bits in ((1,None), (True,0), (0,0,0)):
            with self.assertRaises(s.Reject):
                s.exact_variant(self.routes, bits, 0)

    def test_depth_order_is_not_depth_texture(self):
        camera = {"m_Enabled":1, "m_CullingMask":{"m_Bits":-1}, "m_Depth":1}
        self.assertEqual(s.camera_candidate(camera,1,3), ("eligible_layer","unknown"))
        camera["m_DepthTextureMode"] = 1
        self.assertEqual(s.camera_candidate(camera,1,3), ("eligible_layer","depth_requested"))
        camera["m_DepthTextureMode"] = 0
        self.assertEqual(s.camera_candidate(camera,1,3), ("eligible_layer","no_depth_bit"))

    def test_camera_layer_and_activity_controls(self):
        camera = {"m_Enabled":1, "m_CullingMask":{"m_Bits":4}, "m_DepthTextureMode":1}
        self.assertEqual(s.camera_candidate(camera,1,1), ("excluded_layer","not_applicable"))
        self.assertEqual(s.camera_candidate(camera,0,2), ("inactive","not_applicable"))
        self.assertEqual(s.camera_candidate(camera,None,2), ("unclassified","unknown"))

    def test_local_pointer_fails_closed(self):
        self.assertEqual(s.local({"m_FileID":0,"m_PathID":7}), 7)
        for pointer in ({"m_FileID":1,"m_PathID":7},{"m_FileID":0,"m_PathID":0}):
            with self.assertRaises(s.Reject):
                s.local(pointer)

    def test_quality_missing_is_unknown(self):
        self.assertFalse(s.quality_context({})["quality_schema_known"])
        x = s.quality_context({"m_QualitySettings":[{"softParticles":1},{"softParticles":0},{}]})
        self.assertEqual((x["quality_levels"],x["quality_soft_on"],x["quality_soft_off"],x["quality_soft_unknown"]),(3,1,1,1))

    def test_parent_activity_and_reciprocity(self):
        def ptr(n):return {"m_FileID":0,"m_PathID":n}
        docs = {1:("GameObject",{"m_Component":[{"component":ptr(2)}],"m_IsActive":1}),
                2:("Transform",{"m_GameObject":ptr(1),"m_Father":ptr(4),"m_Children":[]}),
                3:("GameObject",{"m_Component":[{"component":ptr(4)}],"m_IsActive":0}),
                4:("Transform",{"m_GameObject":ptr(3),"m_Father":ptr(0),"m_Children":[ptr(2)]})}
        def kind(n):return docs[n][0]
        def read(n,k):
            self.assertEqual(kind(n),k)
            return docs[n][1]
        self.assertEqual(s.hierarchy(1,read,kind),(0,2))
        docs[4][1]["m_Children"]=[]
        with self.assertRaises(s.Reject):
            s.hierarchy(1,read,kind)

if __name__ == "__main__":
    unittest.main()
