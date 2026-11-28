import unittest
from tools.gt_top_resource_closure import prestage as p, recheck as r, probe as prior

class PrestageTests(unittest.TestCase):
    def test_old_budget_blocker_now_admitted(self):
        p.plan_budget(1779131136,0,8*1024**3)
        with self.assertRaises(prior.Blocked):
            p.plan_budget(p.CAP+1,0,20*1024**3)
    def test_disk_budget_rejects_even_valid_pin_size(self):
        with self.assertRaises(prior.Blocked):
            p.plan_budget(1779131136,0,4*1024**3)
    def test_stream_path_and_empty_descriptor(self):
        self.assertEqual(p.stream_name("archive:/CAB-id/example.resS",1,2),"example.resS")
        self.assertIsNone(p.stream_name("",0,0))
        for raw,off,size in (("/etc/example.resS",0,2),("../example.resS",0,2),("x.resS",1,0),("x.resS",True,1)):
            with self.subTest(raw=raw),self.assertRaises(prior.Blocked):
                p.stream_name(raw,off,size)
    def test_exact_owner_rejects_traversal(self):
        self.assertEqual(p.exact_rel("example.assets"),"Raft_Data/example.assets")
        for v in ("../example.assets","a/b","..","a\\b"):
            with self.assertRaises(prior.Blocked):
                p.exact_rel(v)
    def test_non_Texture2D_type_not_coerced(self):
        from types import SimpleNamespace
        source=SimpleNamespace(resolve=lambda *a:("owner.assets",1),
             file=lambda *a:SimpleNamespace(objects={1:SimpleNamespace(type=SimpleNamespace(name="Cubemap"))}))
        uv=(1.,1.,0.,0.); guid="a"*32
        planned={"key":["owner.assets",1],"class":89}
        trace={(89,"owner.assets",1):(8900000,guid,"3")}
        self.assertEqual(r.exact_slot(((1,1),uv),((8900000,guid,3),uv),"m.assets","b"*32,source,trace,planned)[3],89)
        with self.assertRaises(prior.Blocked):
            r.exact_slot(((1,1),uv),((8900000,guid,3),uv),"m.assets","b"*32,source,trace,{"key":["owner.assets",1],"class":28})
    def test_trace_absence_not_null(self):
        from types import SimpleNamespace
        source=SimpleNamespace(resolve=lambda *a:("owner.assets",1),
             file=lambda *a:SimpleNamespace(objects={1:SimpleNamespace(type=SimpleNamespace(name="Texture2D"))}))
        uv=(1.,1.,0.,0.)
        with self.assertRaises(prior.Blocked):
            r.exact_slot(((1,1),uv),((0,"0"*32,0),uv),"m.assets","b"*32,source,{},{"key":["owner.assets",1],"class":28})
if __name__=="__main__":
    unittest.main()
