"""A15 synthetic negative/positive controls for original parsed shader passes."""
import unittest
from scripts.a15_probe_original_shader_passes import OWNERS, summarize


def shader(owner=OWNERS[0], identity=1, subshaders=None):
    if subshaders is None:
        subshaders = [{"m_Passes": [{}]}]
    return owner, identity, {"m_SubShaders": subshaders}


class ParsedShaderPassTests(unittest.TestCase):
    def test_exact_passes_over_multiple_subshaders_and_owners(self):
        rows = [
            shader(OWNERS[0], 8, [{"m_Passes": [{}, {}]}, {"m_Passes": [{}]}]),
            shader(OWNERS[1], 8, [{"m_Passes": [{}]}]),
        ]
        result = summarize(rows)
        self.assertEqual(result["original_serialized_shader_objects"], 2)
        self.assertEqual(result["original_serialized_subshader_records"], 3)
        self.assertEqual(result["original_serialized_pass_records"], 4)
        self.assertEqual(result["original_passes_per_shader_histogram"], {1: 1, 3: 1})
        self.assertEqual(result["original_shaders_with_multiple_passes"], 1)
        self.assertFalse(result["original_to_exported_shader_join_verified"])
        self.assertFalse(result["unity_gpu_or_device_verified"])

    def test_empty_original_pass_is_not_invented(self):
        self.assertEqual(summarize([shader(subshaders=[])])["original_shaders_with_zero_passes"], 1)
        self.assertEqual(summarize([shader(subshaders=[{"m_Passes": []}])])["original_serialized_pass_records"], 0)

    def test_empty_inventory_rejected(self):
        with self.assertRaises(ValueError):
            summarize([])

    def test_duplicate_owner_path_id_rejected(self):
        with self.assertRaises(ValueError):
            summarize([shader(), shader()])

    def test_same_path_id_other_owner_not_merged(self):
        result = summarize([shader(OWNERS[0], 1), shader(OWNERS[1], 1)])
        self.assertEqual(result["original_serialized_shader_objects"], 2)

    def test_bad_identifier_and_owner_rejected(self):
        for owner, ident in [(OWNERS[0], True), (OWNERS[0], 0), (OWNERS[0], -1),
                             ("not-original", 1), (OWNERS[1], 2.5)]:
            with self.subTest(owner=owner, ident=ident):
                with self.assertRaises(ValueError):
                    summarize([shader(owner, ident)])

    def test_missing_or_malformed_parsed_form_rejected(self):
        for value in (None, [], "raw", {}, {"m_SubShaders": None},
                      {"m_SubShaders": "not-a-list"}):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    summarize([(OWNERS[0], 1, value)])

    def test_subshader_must_be_a_record(self):
        with self.assertRaises(ValueError):
            summarize([shader(subshaders=[None])])

    def test_passes_must_be_list_of_records(self):
        for passes in (None, "pass", [None], [1]):
            with self.subTest(passes=passes):
                with self.assertRaises(ValueError):
                    summarize([shader(subshaders=[{"m_Passes": passes}])])

    def test_original_private_names_are_not_published(self):
        secret = "private-original-shader-name-marker"
        row = (OWNERS[0], 4, {"m_Name": secret, "m_SubShaders": [
            {"m_Name": secret, "m_Passes": [{"m_Name": secret}]}]})
        result = summarize([row])
        self.assertNotIn(secret, str(result))
        self.assertTrue(result["serialized_not_executable_programs"])

if __name__ == "__main__":
    unittest.main()
