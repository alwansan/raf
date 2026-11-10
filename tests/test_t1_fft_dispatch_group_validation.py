"""Native FFT Dispatch group-count regression; no GPU success assertion."""
import unittest
from scripts.t1_fft_dispatch_pair_audit import audit, BEFORE, AFTER


def native(event, groups="1,1,1"):
    fields = ["sequence=1"]
    if event == BEFORE:
        fields += [
            "source_sha_prefix=8aa32937d423",
            "original_findkernel_callsite_present=false",
            "original_runtime_mapping=unverified",
            "gpu_result=unverified",
            "numeric_kernel_argument=6",
            "original_exponent=8",
            "shader_instance_session_local=1",
            "pass_offset=0",
            "group_xyz=" + groups,
        ]
    else:
        fields += ["managed_dispatch_call_returned=true", "gpu_result=unverified"]
    return {"operation": event, "detail": ";".join(fields),
            "area": "water", "session": "native-session"}


class NativeGroupTests(unittest.TestCase):
    def test_positive_y_is_accepted_as_trace_not_gpu_proof(self):
        result = audit([native(BEFORE, "1,8,1"), native(AFTER)])
        self.assertEqual(result["paired_count"], 1)
        self.assertFalse(result["gpu_execution_proven"])
        self.assertFalse(result["runtime_kernel_identity_proven"])

    def test_zero_y_rejected(self):
        with self.assertRaisesRegex(ValueError, "dispatch groups"):
            audit([native(BEFORE, "1,0,1"), native(AFTER)])

    def test_negative_y_rejected(self):
        with self.assertRaisesRegex(ValueError, "dispatch groups"):
            audit([native(BEFORE, "1,-2,1"), native(AFTER)])

    def test_nonunit_x_z_rejected(self):
        for group in ("2,8,1", "1,8,2"):
            with self.subTest(group=group):
                with self.assertRaisesRegex(ValueError, "dispatch groups"):
                    audit([native(BEFORE, group), native(AFTER)])


if __name__ == "__main__":
    unittest.main()
