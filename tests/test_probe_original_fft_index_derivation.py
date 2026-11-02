"""Synthetic original FFT index derivation checks; no Raft source content."""
import hashlib
import unittest
from scripts.probe_original_fft_index_derivation import index_source_links


class IndexDerivationTests(unittest.TestCase):
    def test_original_index_derived_from_resolution_not_passed(self):
        src = ("class FFT {\n"
               " void Run(ComputeShader shader, int resolution) {\n"
               "   int localIndex = (int)Mathf.Log(resolution, 2) - 6;\n"
               "   shader.SetTexture(localIndex, \"A\", src);\n"
               "   shader.Dispatch(localIndex, 1, 1, 1);\n"
               "   shader.SetTexture(localIndex + 1, \"A\", dst);\n"
               "   shader.Dispatch(localIndex + 1, 1, 1, 1);\n"
               " }}")
        data = index_source_links(src, hashlib.sha256(src.encode()).hexdigest())
        self.assertEqual(data["index_assignment_count"], 1)
        rhs = data["index_assignments"][0]["right_hand_side"]
        self.assertTrue(rhs["mathf_log2_call"])
        self.assertIn(6, rhs["integer_constants"])
        self.assertTrue(rhs["has_subtraction"])
        self.assertFalse(data["first_and_second_pass_index_runtime_values_verified"])
        self.assertNotIn("localIndex", str(data))
        self.assertNotIn("resolution", str(data))

    def test_wrong_source_and_missing_index_fail_closed(self):
        with self.assertRaisesRegex(ValueError, "hash changed"):
            index_source_links("shader.Dispatch(index, 1, 1, 1);", "0" * 64)
        src = "shader.Dispatch(2, 1, 1, 1);"
        with self.assertRaisesRegex(ValueError, "not identifiable"):
            index_source_links(src, hashlib.sha256(src.encode()).hexdigest())


if __name__ == "__main__":
    unittest.main()
