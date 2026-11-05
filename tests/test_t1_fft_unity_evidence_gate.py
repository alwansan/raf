import unittest
from scripts.t1_fft_unity_evidence_gate import classify


def fixture(**changes):
    r = dict(editor_invoked=True, editor_supports_compute=False,
             candidate_assets_imported=20, candidate_main_kernels_resolved=0,
             expected_threadgroups_matched=0, observed_errors=0,
             original_authored_compute_restored=False,
             original_runtime_kernel_mapping_proven=False,
             android_gpu_or_pixels_verified=False)
    r.update(changes)
    return r


class GateTests(unittest.TestCase):
    def test_headless_import_not_runtime(self):
        r = classify(fixture())
        self.assertTrue(r['candidate_import_proven'])
        self.assertFalse(r['synthetic_main_runtime_probe_proven'])

    def test_synthetic_runtime_not_original(self):
        r = classify(fixture(editor_supports_compute=True, candidate_main_kernels_resolved=20,
                             expected_threadgroups_matched=20))
        self.assertTrue(r['synthetic_main_runtime_probe_proven'])
        self.assertFalse(r['original_game_kernel_mapping_proven'])

    def test_reject_fake_device(self):
        with self.assertRaises(ValueError): classify(fixture(android_gpu_or_pixels_verified=True))

    def test_reject_boolean_count(self):
        with self.assertRaises(ValueError): classify(fixture(candidate_assets_imported=True))

    def test_reject_impossible_order(self):
        with self.assertRaises(ValueError): classify(fixture(candidate_main_kernels_resolved=1))

    def test_reject_no_compute_runtime(self):
        with self.assertRaises(ValueError): classify(fixture(expected_threadgroups_matched=1,
                                                            candidate_main_kernels_resolved=1))

    def test_reject_uninvoked(self):
        with self.assertRaises(ValueError): classify(fixture(editor_invoked=False))

    def test_reject_extra_field(self):
        with self.assertRaises(ValueError): classify(fixture(unexpected='leak'))

    def test_error_blocks_positive(self):
        self.assertFalse(classify(fixture(observed_errors=1))['candidate_import_proven'])


if __name__ == '__main__':
    unittest.main()
