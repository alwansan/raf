"""Synthetic regression for explicit FFT member-call structural evidence only."""
import hashlib
import unittest
from scripts.t1_fft_dispatch_evidence import audit


class MemberCallTests(unittest.TestCase):
    def scan(self, source):
        raw = source.encode("utf-8")
        return audit(raw, hashlib.sha256(raw).hexdigest())

    def test_declarations_and_unqualified_helpers_are_not_compute_calls(self):
        r = self.scan("void FindKernel(int k) {} void Dispatch(int k) {} FindKernel(1); Dispatch(1);")
        self.assertFalse(r["findkernel_and_dispatch_syntax_present"])
        self.assertFalse(r["call_families_present"]["FindKernel"])
        self.assertFalse(r["call_families_present"]["Dispatch"])

    def test_explicit_member_calls_remain_visible(self):
        r = self.scan('shader.FindKernel("FFT"); shader.SetTexture(0, "A", tex); shader.Dispatch(0, 1, 1, 1);')
        self.assertTrue(r["findkernel_and_dispatch_syntax_present"])
        self.assertTrue(r["call_families_present"]["SetTexture"])
        self.assertFalse(r["resource_binding_dataflow_proven"])
        self.assertFalse(r["unity_execution_proven"])

    def test_null_conditional_member_syntax(self):
        r = self.scan('shader?.FindKernel("FFT"); shader?.Dispatch(0, 1, 1, 1);')
        self.assertTrue(r["findkernel_and_dispatch_syntax_present"])


if __name__ == "__main__":
    unittest.main()
