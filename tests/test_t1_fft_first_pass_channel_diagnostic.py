import unittest
from scripts.t1_fft_first_pass_channel_diagnostic import analyze

class ChannelDiagnosticTests(unittest.TestCase):
    def test_identity(self):
        pixels = [(1., 2., 3., 4.), (5., 6., 7., 8.)]
        report = analyze(pixels, pixels)
        self.assertEqual(report["identity_mismatch_count"], 0)
        self.assertFalse(report["permutation_improves"])

    def test_swapped_channels(self):
        original = [(1., 2., 3., 4.), (5., 6., 7., 8.)]
        swapped = [(2., 1., 3., 4.), (6., 5., 7., 8.)]
        report = analyze(original, swapped)
        self.assertEqual(report["best_channel_permutation"], "GRBA")
        self.assertTrue(report["permutation_improves"])
        self.assertEqual(report["best_mismatch_count"], 0)

    def test_nonfinite_is_not_silent_success(self):
        report = analyze([(1., 2., 3., 4.)], [(float("nan"), 2., 3., 4.)])
        self.assertEqual(report["best_nonfinite_count"], 1)

    def test_rejects_bad_shapes(self):
        with self.assertRaises(ValueError):
            analyze([(1., 2., 3., 4.)], [])
        with self.assertRaises(ValueError):
            analyze([], [])

    def test_rejects_negative_tolerance(self):
        with self.assertRaises(ValueError):
            analyze([(1., 2., 3., 4.)], [(1., 2., 3., 4.)], atol=-1)

if __name__ == "__main__":
    unittest.main()
