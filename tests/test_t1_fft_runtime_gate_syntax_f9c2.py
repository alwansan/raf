"""T1 WATER-001 regression: FFT evidence gate must import and enforce radix-2."""
import unittest
from scripts.t1_fft_runtime_evidence_gate import validate


def fixture(size):
    return {
        "build_sha": "a" * 40,
        "device_session": "LogRaft-20261108-164850-270",
        "dispatches": [{
            "shader_guid": "b" * 32,
            "kernel_name": "FFT_Horizontal",
            "find_kernel_result": 6,
            "dispatch_kernel": 6,
            "groups": [8, 8, 1],
            "fft_size": size,
            "bank": 0,
            "pass_index": 0,
            "bindings": ["Input", "Output"],
        }],
    }


class RuntimeGateSyntaxAndRadix2Tests(unittest.TestCase):
    def test_imported_gate_accepts_256(self):
        self.assertTrue(validate(fixture(256))["binding_contract_complete"])

    def test_rejects_zero_one_non_power_of_two(self):
        for size in (0, 1, 3, 255, 257):
            with self.subTest(size=size), self.assertRaisesRegex(ValueError, "radix-2"):
                validate(fixture(size))

    def test_rejects_boolean_fft_size(self):
        with self.assertRaisesRegex(ValueError, "invalid fft_size"):
            validate(fixture(True))


if __name__ == "__main__":
    unittest.main()
