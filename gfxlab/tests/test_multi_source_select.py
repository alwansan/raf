import unittest
from gfxlab.tools.multi_source_select import label_category, MIN_VERTICES, ROLE_KEEP
from gfxlab.tools.obj_normalize import source_vertex_span_valid

class MultiSelectTests(unittest.TestCase):
    def test_shears_not_player_from_ancestor(self):
        self.assertNotEqual(label_category(["Shears","Shears"],"skinned",3,375,1),"person")
    def test_person_requires_rig(self):
        self.assertEqual(label_category(["HumanBody","Body"],"skinned",20,3000,1),"person")
        self.assertNotEqual(label_category(["Body","Body"],"skinned",2,3000,1),"person")
    def test_animal_requires_rig(self):
        self.assertEqual(label_category(["Llama","Llama"],"skinned",25,5000,2),"animal")
    def test_static_large(self):
        self.assertEqual(label_category(["Engine","Large"],"static",0,7000,2),"large_prop")
    def test_missing_names_stays_generic(self):
        self.assertEqual(label_category(["",""],"static",0,600,1),"generic")
    def test_limits_and_texture_roles(self):
        self.assertGreaterEqual(MIN_VERTICES,16)
        self.assertIn("basecolor",ROLE_KEEP)
    def test_spatial_extent_is_real_in_unity_float32(self):
        self.assertTrue(source_vertex_span_valid([(0,0,0),(1,0,0),(0,1,0)]))
        self.assertTrue(source_vertex_span_valid([(0,0,0),(1e-9,0,0)]))
        self.assertFalse(source_vertex_span_valid([(0,0,0)]*400))
        self.assertFalse(source_vertex_span_valid([(0,0,0),(1e-15,0,0)]))
        self.assertFalse(source_vertex_span_valid([(float("nan"),0,0),(1,1,1)]))
        self.assertFalse(source_vertex_span_valid([(1e30,0,0),(1e30+1,0,0)]))
if __name__=="__main__": unittest.main()
