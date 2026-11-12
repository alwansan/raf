"""Purely synthetic name provenance negative controls."""
import unittest
from scripts.b09_spectrum_topology_contract import TARGET
from scripts.gt_spectrum_original_shaderfind_name import validate_name


class OriginalSpectrumShaderFindNameTests(unittest.TestCase):
    def test_exact_source_identity(self):
        self.assertEqual(validate_name(TARGET),TARGET)

    def test_no_broad_or_guessable_match(self):
        for x in ("Spectrum","Ultimate Water",TARGET+" ",TARGET+"\n","",True):
            with self.subTest(x=x):
                with self.assertRaises(ValueError):
                    validate_name(x)


if __name__=="__main__":
    unittest.main()
