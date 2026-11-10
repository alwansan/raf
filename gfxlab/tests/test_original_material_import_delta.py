import unittest
from gfxlab.tools.original_material_import_delta import (
    near_source_scalar,FALLBACK_GLOSS
)

class TestMaterialImportParityGap(unittest.TestCase):
    def test_exact_compare_is_not_rounded_visual_guess(self):
        self.assertTrue(near_source_scalar(0.45,FALLBACK_GLOSS))
        self.assertFalse(near_source_scalar(0.5,FALLBACK_GLOSS))
        self.assertFalse(near_source_scalar(0.451,FALLBACK_GLOSS))
    def test_zero_and_one_must_be_exact(self):
        self.assertTrue(near_source_scalar(0,0))
        self.assertTrue(near_source_scalar(1.0,1))
        self.assertFalse(near_source_scalar(0.9,1))
    def test_float_validation_fail_closed(self):
        for value in (True,None,"0.45",float("nan"),float("inf"),10001):
            with self.subTest(value=str(value)):
                with self.assertRaises(ValueError):
                    near_source_scalar(value,FALLBACK_GLOSS)
