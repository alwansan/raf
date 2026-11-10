import unittest
from gfxlab.tools.multi_obj_attribute_parity import inspect_obj_attributes
class TestSourceObjDuplicateAttributes(unittest.TestCase):
    def test_equal_attributes_at_different_indices(self):
        s="v 0 0 0\nv 1 0 0\nv 0 1 0\nv 0 0 0\nvt 0 0\nvt 1 0\nvt 0 1\nvt 0 0\nvn 0 0 1\nvn 0 0 1\nf 1/1/1 2/2/1 3/3/1\nf 4/4/2 2/2/1 3/3/1\n"
        d=inspect_obj_attributes(s)
        self.assertEqual(d["source_declared_vertices"],4)
        self.assertEqual(d["referenced_source_indices"],4)
        self.assertEqual(d["distinct_position_uv_normal_float32"],3)
        self.assertEqual(d["source_triangles"],2)
        self.assertFalse(d["exact_importer_attribute_parity_proven"])
    def test_uv_or_normal_seam_remains_unique(self):
        s="v 0 0 0\nv 1 0 0\nv 0 1 0\nv 0 0 0\nvt 0 0\nvt 1 0\nvt 0 1\nvt 0 1\nvn 0 0 1\nf 1/1/1 2/2/1 3/3/1\nf 4/4/1 2/2/1 3/3/1\n"
        d=inspect_obj_attributes(s)
        self.assertEqual(d["distinct_position_float32"],3)
        self.assertEqual(d["distinct_position_uv_normal_float32"],4)
    def test_invalid_vertex_reference_fails(self):
        with self.assertRaises(ValueError):
            inspect_obj_attributes("v 0 0 0\nv 1 0 0\nv 0 1 0\nf 1 2 4\n")
