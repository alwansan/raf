import unittest
from gfxlab.tools.multi_vertex_reference_audit import inspect_obj
class TestOriginalObjUsage(unittest.TestCase):
    def test_unused_vertex_is_counted_not_deleted(self):
        s="v 0 0 0\nv 1 0 0\nv 0 1 0\nv 2 2 2\nvt 0 0\nvt 1 0\nvt 0 1\nvn 0 0 1\nf 1/1/1 2/2/1 3/3/1\n"
        d=inspect_obj(s)
        self.assertEqual(d["declared_vertices"],4)
        self.assertEqual(d["referenced_vertices"],3)
        self.assertEqual(d["unreferenced_vertices"],1)
        self.assertEqual(d["referenced_uvs"],3)
        self.assertEqual(d["referenced_normals"],1)
    def test_indices_are_strict(self):
        for s in ("v 0 0 0\nf 1 2 3\n",
                  "v 0 0 0\nv 0 1 0\nv 0 0 1\nf 1 2 0\n"):
            with self.subTest(s=s),self.assertRaises(ValueError):inspect_obj(s)
