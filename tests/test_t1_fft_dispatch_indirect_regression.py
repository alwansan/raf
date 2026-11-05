"""Synthetic regression for indirect dispatch classification; not a Unity runtime proof."""
import hashlib
import unittest
from scripts.t1_fft_dispatch_evidence import audit


class IndirectDispatchRegression(unittest.TestCase):
    def inspect(self, source):
        raw = source.encode('utf-8')
        return audit(raw, hashlib.sha256(raw).hexdigest())

    def test_indirect_only_member_call_is_structurally_detected(self):
        result = self.inspect('var k = cs.FindKernel("FFT"); cs.SetBuffer(k, "B", buffer); cs.DispatchIndirect(k, args);')
        self.assertTrue(result['findkernel_and_dispatch_syntax_present'])
        self.assertTrue(result['call_families_present']['DispatchIndirect'])
        self.assertFalse(result['call_families_present']['Dispatch'])
        self.assertFalse(result['original_program_to_kernel_mapping_proven'])
        self.assertFalse(result['resource_binding_dataflow_proven'])

    def test_indirect_without_findkernel_is_not_a_complete_pair(self):
        result = self.inspect('cs.DispatchIndirect(7, args);')
        self.assertFalse(result['findkernel_and_dispatch_syntax_present'])

    def test_indirect_in_strings_and_comments_is_not_detected(self):
        result = self.inspect('cs.FindKernel("K"); // cs.DispatchIndirect(0, args)\nvar s = "cs.DispatchIndirect(1,args)";')
        self.assertFalse(result['call_families_present']['DispatchIndirect'])
        self.assertFalse(result['findkernel_and_dispatch_syntax_present'])

    def test_bare_local_helpers_do_not_count(self):
        result = self.inspect('FindKernel("K"); DispatchIndirect(0,args);')
        self.assertFalse(result['findkernel_and_dispatch_syntax_present'])
        self.assertFalse(result['call_families_present']['DispatchIndirect'])


if __name__ == '__main__':
    unittest.main()
