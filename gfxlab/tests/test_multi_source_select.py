import unittest
from gfxlab.tools.multi_source_select import label_category, MIN_VERTICES, ROLE_KEEP

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
if __name__=="__main__": unittest.main()
