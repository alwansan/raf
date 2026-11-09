"""T1 WATER-001: runtime evidence identities must be usable for correlation."""
import copy
import unittest

from scripts.t1_fft_runtime_evidence_gate import validate


def fixture():
    return {
        "build_sha": "a" * 40,
        "device_session": "LogRaft-20261108-164850-270",
        "dispatches": [{
            "shader_guid": "b" * 32,
            "kernel_name": "FFT_Horizontal",
            "find_kernel_result": 6,
            "dispatch_kernel": 6,
            "groups": [8, 8, 1],
            "fft_size": 256,
            "bank": 0,
            "pass_index": 0,
            "bindings": ["Input", "Output"],
        }],
    }


class RuntimeIdentityTests(unittest.TestCase):
    def test_valid_named_kernel_and_session(self):
        self.assertTrue(validate(fixture())["binding_contract_complete"])

    def test_blank_kernel_rejected(self):
        row = fixture()
        row["dispatches"][0]["kernel_name"] = "   "
        with self.assertRaises(ValueError):
            validate(row)

    def test_padded_kernel_rejected(self):
        row = fixture()
        row["dispatches"][0]["kernel_name"] = " FFT_Horizontal "
        with self.assertRaises(ValueError):
            validate(row)

    def test_control_character_kernel_rejected(self):
        row = fixture()
        row["dispatches"][0]["kernel_name"] = "FFT\nHorizontal"
        with self.assertRaises(ValueError):
            validate(row)

    def test_blank_device_session_rejected(self):
        row = fixture()
        row["device_session"] = "  "
        with self.assertRaises(ValueError):
            validate(row)

    def test_control_character_device_session_rejected(self):
        row = fixture()
        row["device_session"] = "session\nother"
        with self.assertRaises(ValueError):
            validate(row)

    def test_original_data_unchanged(self):
        row = fixture()
        original = copy.deepcopy(row)
        validate(row)
        self.assertEqual(row, original)


if __name__ == "__main__":
    unittest.main()
