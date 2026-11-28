import unittest
from tools.gt_top_resource_closure.probe import check_texture_slot, uv_equal, Blocked, document
from pathlib import Path
from tempfile import TemporaryDirectory

class ResourceClosureTests(unittest.TestCase):
    def setUp(self):
        self.g="a"*32
        self.t="b"*32
        self.uv=(1.,1.,0.,0.)
        self.src=((1,9),self.uv)
        self.trace={(28,"owner.assets",9):(2800000,self.t,"3")}
        self.resolve=lambda owner,p: ("owner.assets",p["m_PathID"])

    def check(self,exp,src=None,trace=None):
        return check_texture_slot(src or self.src,exp,"material.assets",self.g,self.resolve,
                                  self.trace if trace is None else trace)

    def test_exact_external_pointer(self):
        self.assertEqual(self.check(((2800000,self.t,3),self.uv)),
                         (("owner.assets",9),(self.t,2800000),3))

    def test_wrong_guid_fileid_or_type_rejected(self):
        for p in ((2800000,"c"*32,3),(1,self.t,3),(2800000,self.t,2)):
            with self.subTest(p=p),self.assertRaises(Blocked):
                self.check((p,self.uv))

    def test_missing_trace_not_null(self):
        with self.assertRaises(Blocked):
            self.check(((0,"0"*32,0),self.uv),trace={})

    def test_null_pointer_exact(self):
        self.assertIsNone(self.check(((0,"0"*32,0),self.uv),src=((0,0),self.uv)))
        with self.assertRaises(Blocked):
            self.check(((1,self.t,3),self.uv),src=((0,0),self.uv))

    def test_local_document_exact(self):
        trace={(28,"owner.assets",9):(9,self.g,"2")}
        self.assertEqual(self.check(((9,"0"*32,0),self.uv),trace=trace),
                         (("owner.assets",9),(self.g,9),0))
        with self.assertRaises(Blocked):
            self.check(((9,"0"*32,0),self.uv),trace=self.trace)

    def test_binary32_uv_and_mutation(self):
        self.assertTrue(uv_equal((0.1,1.,0.,0.),(0.10000000149011612,1.,0.,0.)))
        self.assertFalse(uv_equal(self.uv,(1.,1.,.25,0.)))
        with self.assertRaises(Blocked):
            self.check(((2800000,self.t,3),(1.,1.,.25,0.)))

    def test_exact_document_identity(self):
        with TemporaryDirectory() as tmp:
            p=Path(tmp)/"x.asset"
            p.write_text("%YAML 1.1\n--- !u!21 &1\nMaterial:\n  m_Name: fixture\n--- !u!28 &2\nTexture2D:\n  m_Name: fixture\n")
            self.assertIn("Texture2D:",document(p,2,28))
            with self.assertRaises(Blocked):
                document(p,1,28)
            p.write_text("%YAML 1.1\n--- !u!28 &2\nTexture2D: {}\n--- !u!28 &2\nTexture2D: {}\n")
            with self.assertRaises(Blocked):
                document(p,2,28)

if __name__=="__main__":
    unittest.main()
