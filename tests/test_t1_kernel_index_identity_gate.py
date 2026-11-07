import importlib.util
import pathlib
import unittest

SOURCE = pathlib.Path(__file__).resolve().parents[1] / "scripts" / "t1_kernel_index_identity_gate.py"
spec = importlib.util.spec_from_file_location("kernel_gate", SOURCE)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

def sample():
    return {
        "source_sha": "a" * 40,
        "compute_shader_guid": "b" * 32,
        "kernel_name": "FFT",
        "find_kernel_index": 6,
        "dispatch_kernel_index": 6,
        "dispatch_groups": [8, 8, 1],
        "original_program_sha256": "c" * 64,
        "resource_binding_sha256": "d" * 64,
    }

class KernelIdentityGateTest(unittest.TestCase):
    def test_complete_structural_metadata(self):
        self.assertEqual(module.check(sample()), [])

    def test_integer_six_alone_does_not_identify_fft(self):
        self.assertIn("missing compute_shader_guid", module.check({"dispatch_kernel_index": 6}))

    def test_find_dispatch_mismatch(self):
        data = sample()
        data["dispatch_kernel_index"] = 5
        self.assertIn("FindKernel/Dispatch index mismatch", module.check(data))

    def test_boolean_is_not_index(self):
        data = sample()
        data["find_kernel_index"] = True
        self.assertTrue(any("find_kernel_index" in e for e in module.check(data)))

    def test_no_zero_group(self):
        data = sample()
        data["dispatch_groups"] = [8, 0, 1]
        self.assertTrue(any("dispatch_groups" in e for e in module.check(data)))

if __name__ == "__main__":
    unittest.main()
