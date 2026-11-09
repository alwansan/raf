"""Source-only T1 WATER-001: runtime names and indices must agree across dispatches."""
import copy
import unittest
from scripts.t1_fft_runtime_evidence_gate import validate

def fixture():
    return {"build_sha": "a" * 40, "device_session": "LogRaft-20261108-164850-270",
            "dispatches": [{
                "shader_guid": "b" * 32, "kernel_name": "FFT_Horizontal",
                "find_kernel_result": 6, "dispatch_kernel": 6,
                "groups": [8, 8, 1], "fft_size": 256, "bank": 0,
                "pass_index": 0, "bindings": ["Input", "Output"]}]}

def add_dispatch(record):
    row = copy.deepcopy(record["dispatches"][0])
    row["pass_index"] = 1
    record["dispatches"].append(row)
    return row

class KernelIndexBijectionTests(unittest.TestCase):
    def test_repeated_named_kernel_on_second_pass_valid(self):
        d = fixture()
        add_dispatch(d)["bank"] = 1
        self.assertEqual(validate(d)["runtime_dispatches"], 2)

    def test_same_named_kernel_index_drift_rejected(self):
        d = fixture()
        row = add_dispatch(d)
        row.update(find_kernel_result=7, dispatch_kernel=7)
        with self.assertRaisesRegex(ValueError, "inconsistent index"):
            validate(d)

    def test_same_index_other_kernel_name_rejected(self):
        d = fixture()
        add_dispatch(d)["kernel_name"] = "FFT_Vertical"
        with self.assertRaisesRegex(ValueError, "inconsistent name"):
            validate(d)

    def test_distinct_named_kernels_and_indices_valid(self):
        d = fixture()
        row = add_dispatch(d)
        row.update(kernel_name="FFT_Vertical", find_kernel_result=7, dispatch_kernel=7)
        self.assertEqual(validate(d)["runtime_dispatches"], 2)

    def test_same_name_other_shader_index_can_differ(self):
        d = fixture()
        row = add_dispatch(d)
        row.update(shader_guid="c" * 32, find_kernel_result=0, dispatch_kernel=0)
        self.assertTrue(validate(d)["binding_contract_complete"])

    def test_same_index_other_shader_name_can_differ(self):
        d = fixture()
        row = add_dispatch(d)
        row.update(shader_guid="c" * 32, kernel_name="OtherKernel")
        self.assertTrue(validate(d)["binding_contract_complete"])

    def test_binding_control_chars_rejected(self):
        for bad in ("Input\\nOutput", "Input\\x7fMore", "Input\\x85More"):
            d = fixture()
            d["dispatches"][0]["bindings"][0] = bad.encode("ascii").decode("unicode_escape")
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, "control character"):
                validate(d)

    def test_c1_identity_control_chars_rejected(self):
        for key in ("device_session", "kernel_name"):
            d = fixture()
            if key == "device_session":
                d[key] = "session" + chr(0x85) + "other"
            else:
                d["dispatches"][0][key] = "FFT" + chr(0x85) + "_Horizontal"
            with self.subTest(key=key), self.assertRaises(ValueError):
                validate(d)

if __name__ == "__main__":
    unittest.main()
