import unittest
from gfxlab.tools.obj_normalize import normalize_exported_obj
class OriginalObjNormalizerTests(unittest.TestCase):
    def test_missing_normals_rebuild_area_weighted(self):
        s="o Diagnostic\n"+"\n".join(f"v {i} {i%4} 0" for i in range(130))+"\n"
        s+="\n".join(f"vt {i/130} 0" for i in range(130))+"\n"
        s+="usemtl source_slot_0\nf 1/1 2/2 3/3\n"
        result,stats=normalize_exported_obj(s)
        self.assertEqual(stats["source_vertices"],130)
        self.assertEqual(stats["triangles"],1)
        self.assertTrue(stats["normals_generated_for_unity"])
        self.assertIn("f 1/1/1 2/2/2 3/3/3",result)
        self.assertIn("usemtl source_slot_0",result)
    def test_preserve_valid_face_normals(self):
        s="\n".join(f"v {i} 0 0" for i in range(130))+"\n"
        s+="vt 0 0\nvt 1 0\nvt 0 1\nvn 0 1 0\nf 1/1/1 2/2/1 3/3/1\n"
        result,stats=normalize_exported_obj(s)
        self.assertFalse(stats["normals_generated_for_unity"])
        self.assertIn("f 1/1/1 2/2/1 3/3/1",result)
    def test_reject_out_of_range_face(self):
        s="\n".join(f"v {i} 0 0" for i in range(130))+"\n"+"vt 0 0\nf 1/1 2/1 400/1"
        with self.assertRaises(ValueError):normalize_exported_obj(s)
    def test_no_uv_must_not_claim_colored_render(self):
        s="\n".join(f"v {i} 0 0" for i in range(130))+"\n"+"f 1 2 3"
        with self.assertRaises(ValueError):normalize_exported_obj(s)
if __name__=="__main__":unittest.main()
