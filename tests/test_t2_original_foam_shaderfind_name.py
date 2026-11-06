"""Source-free controls for private source-original shader name."""
import unittest
from scripts.t2_original_foam_shaderfind_name import safe_private_name

class OriginalFoamNameTests(unittest.TestCase):
    def test_exact_identity(self):
        self.assertEqual(safe_private_name("Synthetic/FoamName","Synthetic/FoamName"),"Synthetic/FoamName")
    def test_wrong_original_name_rejected(self):
        with self.assertRaises(ValueError): safe_private_name("Synthetic/FoamName2","Synthetic/FoamName")
    def test_casefold_not_allowed(self):
        with self.assertRaises(ValueError): safe_private_name("synthetic/FoamName","Synthetic/FoamName")
    def test_empty_unicode_and_line_break_rejected(self):
        for value in ("","\x00","one\x00two","one\ntwo","one\rtwo"):
            with self.subTest(value=repr(value)), self.assertRaises(ValueError):
                safe_private_name(value,value)
    def test_bool_not_name(self):
        with self.assertRaises(ValueError): safe_private_name(True,True)
    def test_oversized_rejected(self):
        with self.assertRaises(ValueError): safe_private_name("A"*257,"A"*257)

if __name__=="__main__": unittest.main()
