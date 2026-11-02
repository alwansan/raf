"""Synthetic CSharp FFT original call-graph lexical analyzer fixtures."""
import unittest
from scripts.probe_original_fft_caller_graph import source_declarations, find_original_calls


class KernelCallerGraphTests(unittest.TestCase):
    def test_reports_signature_and_numeric_callsite_without_code(self):
        lib = ("class Dx11FFT {\n"
               " public void Calculate(ComputeShader shader, int kernelIndex, int width) {\n"
               " }\n"
               " public void Ordinary(int x) {}\n"
               "}\n")
        caller = ("class WavesRendererFFT {\n"
                  " void Begin() { helper.Calculate(shader, 6, 64); }\n"
                  "}\n")
        defs = source_declarations(lib)
        found = find_original_calls(caller, defs)
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["arguments"][1]["value"], 6)
        self.assertFalse(found[0]["cross_file_runtime_target_verified"])
        self.assertNotIn("Calculate", str(found))
        self.assertNotIn("shader", str(found))

    def test_must_not_conflate_call_with_unrelated_method(self):
        defs = source_declarations("class S { public void Update(int frames) {} }")
        self.assertEqual(find_original_calls("someone.Update(6);", defs), [])


if __name__ == "__main__":
    unittest.main()
