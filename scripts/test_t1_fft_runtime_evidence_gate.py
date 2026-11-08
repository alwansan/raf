#!/usr/bin/env python3
"""Source-only tests: no synthetic success may be treated as device evidence."""
import unittest
from scripts.t1_fft_runtime_evidence_gate import validate, no_duplicate_keys

def sample():
    return {"build_sha": "a" * 40, "device_session": "LogRaft-real-session",
            "dispatches": [{"shader_guid": "b" * 32, "kernel_name": "FFT",
              "find_kernel_result": 6, "dispatch_kernel": 6,
              "groups": [16, 16, 1], "fft_size": 256, "bank": 0,
              "pass_index": 0, "bindings": ["Input", "Output"]}]}

class RuntimeGateTests(unittest.TestCase):
    def test_complete_structural_contract(self):
        self.assertTrue(validate(sample())["binding_contract_complete"])

    def test_original_numeric_six_alone_is_not_identity(self):
        d = sample()
        del d["dispatches"][0]["kernel_name"]
        with self.assertRaises(ValueError):
            validate(d)

    def test_findkernel_dispatch_mismatch(self):
        d = sample()
        d["dispatches"][0]["dispatch_kernel"] = 7
        with self.assertRaises(ValueError):
            validate(d)

    def test_no_device_session(self):
        d = sample()
        d["device_session"] = ""
        with self.assertRaises(ValueError):
            validate(d)

    def test_no_binding_names(self):
        d = sample()
        d["dispatches"][0]["bindings"] = []
        with self.assertRaises(ValueError):
            validate(d)

    def test_duplicate_json_keys(self):
        with self.assertRaises(ValueError):
            no_duplicate_keys([("build_sha", "a"), ("build_sha", "b")])

if __name__ == "__main__":
    unittest.main()
