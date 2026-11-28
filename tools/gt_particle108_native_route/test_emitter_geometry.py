import unittest
from tools.gt_particle108_native_route.emitter_geometry import audit_refs,valid_bake,fixture,Reject,import_observation
class GeometryTests(unittest.TestCase):
    def test_bound_pointers(self):
        audit_refs({"a":{"fileID":1},"b":{"fileID":2,"guid":"a"*32,"type":2}}, {1},{(2,"a"*32)})
    def test_dangling_local(self):
        with self.assertRaises(Reject):audit_refs({"fileID":9},{1},set())
    def test_dangling_external(self):
        with self.assertRaises(Reject):audit_refs({"fileID":9,"guid":"a"*32,"type":2},{1},set())
    def test_null_external_rejected(self):
        with self.assertRaises(Reject):audit_refs({"fileID":0,"guid":"a"*32},set(),set())
    def test_geometry_count_and_area(self):
        b=dict(particles=1,vertices=4,indices=6,finite=True,nondegenerate=True)
        self.assertTrue(valid_bake(b))
        self.assertFalse(valid_bake(dict(b,nondegenerate=False)))
        self.assertFalse(valid_bake(dict(b,indices=3)))
    def test_exact_component_payload_preserved(self):
        tr=dict(m_LocalPosition=dict(x=0,y=0,z=0),m_LocalRotation=dict(x=0,y=0,z=0,w=1),m_LocalScale=dict(x=1,y=1,z=1))
        ps="--- !u!198 &3\nParticleSystem:\n  custom: 001\n"
        ren="--- !u!199 &4\nParticleSystemRenderer:\n  custom: 002\n"
        data=fixture(1,2,3,4,None,0,tr,ps,ren)
        self.assertIn(ps.encode(),data);self.assertIn(ren.encode(),data)
    def test_failed_import_without_rows_retains_safe_counters(self):
        r=dict(run_id="r",private_log_guard=True,unity_version="2021.3.45f2",backend="Vulkan",phase="numeric_properties",
               failure_category="InvalidOperationException",asset_identities=4,numeric_declared=11,numeric_matched=10,numeric_undeclared=2,rows=None,private_asset_name="omit")
        obs=import_observation({"run_id":"r"},r)
        self.assertEqual(obs["editor_phase"],"numeric_properties")
        self.assertEqual(obs["editor_row_count"],0)
        self.assertEqual(obs["import_counters"]["numeric_matched"],10)
        self.assertNotIn("private_asset_name",obs)
    def test_wrong_run_rejected(self):
        with self.assertRaises(Reject):import_observation({"run_id":"r"},{"run_id":"other"})
if __name__=="__main__":unittest.main()
