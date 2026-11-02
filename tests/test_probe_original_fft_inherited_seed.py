import json
import unittest
from scripts.probe_original_fft_inherited_seed import prove, sha


class InheritedSeedTests(unittest.TestCase):
    def sources(self):
        derived = '''class Dx11FFT : GpuFFT {
 public Dx11FFT(ComputeShader cs, int size, bool precise, bool wide) : base(size,precise,wide,true) {
  kernel = inheritedCount - 5 << 1;
  if (wide) { kernel += 10; }
 }
 public void Run() { cs.SetTexture(kernel,"A",src); cs.Dispatch(kernel,1,1,1); cs.Dispatch(kernel+1,1,1,1); }
}'''
        base = '''class GpuFFT {
 protected int inheritedCount;
 protected GpuFFT(int dimension, bool a, bool b, bool c) {
  inheritedCount = (int)(Mathf.Log(dimension) / Mathf.Log(2f));
 }
}'''
        return derived, base

    def run_proof(self, derived, base):
        return prove(derived, base, sha(derived), sha(base))

    def test_inherited_field_is_not_the_constructor_size_parameter(self):
        d, b = self.sources()
        report = self.run_proof(d, b)
        self.assertTrue(report['inherited_seed_dataflow_verified'])
        self.assertTrue(report['derived_second_int_forwarded_to_base_first_int'])
        self.assertFalse(report['unity_runtime_kernel_lookup_mapping_verified'])
        self.assertEqual(report['algebraic_examples_only'][1]['bank0'], [2,3])
        self.assertEqual(report['algebraic_examples_only'][3]['bank1'], [16,17])
        for private in ('inheritedCount', 'dimension', 'precise', 'wide'):
            self.assertNotIn(private, json.dumps(report))

    def test_wrong_source_hash_fails_closed(self):
        d, b = self.sources()
        with self.assertRaisesRegex(ValueError, 'fingerprint'):
            prove(d, b, '0'*64, sha(b))

    def test_wrong_base_or_aliased_size_is_not_claimed_proven(self):
        d, b = self.sources()
        for bad in (d.replace(': GpuFFT', ': Other'), d.replace('base(size,', 'base(size+1,')):
            with self.assertRaises(ValueError): self.run_proof(bad, b)

    def test_changed_log_or_extra_writes_are_refused(self):
        d, b = self.sources()
        for bad in (b.replace('Log(2f)', 'Log(4f)'), b.replace(' protected GpuFFT', ' protected int duplicate;\n protected GpuFFT').replace(' }\n}', ' inheritedCount += 1;\n }\n}')):
            with self.assertRaises(ValueError): self.run_proof(d, bad)

    def test_wrong_field_visibility_or_bank_guard_are_refused(self):
        d, b = self.sources()
        with self.assertRaises(ValueError): self.run_proof(d, b.replace('protected int', 'private int'))
        with self.assertRaises(ValueError): self.run_proof(d.replace('if (wide)', 'if (precise)'), b)
