import tempfile
import unittest
from pathlib import Path
from scripts.t1_water_logcat_first_roots import classify, scan

class FirstRootsTests(unittest.TestCase):
    def test_classification_no_raw_data(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'part.log'
            p.write_text('11-05 22:09:11.002 E Unity: Invalid compute kernel index 6 SECRET_TOKEN\n'
                         '11-05 22:09:11.004 E Unity: Ultimate Water Spectrum invalid pass SECRET_TOKEN\n'
                         '11-05 22:09:11.005 E Unity: Ultimate Water Foam Global invalid pass\n')
            result = scan([p])
            self.assertEqual(result['root_line_counts'], {'kernel_index_6': 1, 'pass_spectrum': 1, 'pass_foam_global': 1})
            self.assertEqual(result['first_by_category']['kernel_index_6'], '11-05 22:09:11.002')
            self.assertNotIn('SECRET_TOKEN', str(result))
            self.assertFalse(result['findkernel_dispatch_proven'])
    def test_unrelated_pass_and_fake_kernel(self):
        self.assertIsNone(classify('UI: invalid pass, not water'))
        self.assertIsNone(classify('Kernel 6 ready'))
        self.assertEqual(classify('Invalid kernel index 7'), 'kernel_other')
        self.assertEqual(classify('Kernel at index (6) is invalid'), 'kernel_index_6')
        self.assertEqual(classify("Shader Ultimate Water/Spectrum does not have a pass 0"), 'pass_spectrum')
    def test_earliest_timestamp_independent_of_segment_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            late = Path(tmp) / 'late.log'
            early = Path(tmp) / 'early.log'
            late.write_text('E Unity: Invalid compute kernel index 6\n'
                            '11-05 23:09:11.005 E Unity: Invalid compute kernel index 6\n'
                            '11-05 23:09:11.006 E Unity: Ultimate Water Spectrum invalid pass\n')
            early.write_text('11-05 22:09:11.002 E Unity: Invalid compute kernel index 6\n'
                             '11-05 22:09:11.003 E Unity: Ultimate Water Spectrum invalid pass\n')
            forward = scan([late, early])
            backward = scan([early, late])
            self.assertEqual(forward['first_by_category'], backward['first_by_category'])
            self.assertEqual(forward['first_by_category']['kernel_index_6'], '11-05 22:09:11.002')
            self.assertEqual(forward['first_by_category']['pass_spectrum'], '11-05 22:09:11.003')
            self.assertEqual(forward['root_line_counts']['kernel_index_6'], 3)

    def test_oversized_physical_line_tail_never_classified(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'oversized.log'
            # The tail contains a valid-looking record, but it belongs to an
            # oversized physical line and must not become a second record.
            p.write_bytes(b'X' * 32769 +
                          b'11-05 22:09:11.001 E Unity: Invalid compute kernel index 6\\n' +
                          b'11-05 22:09:11.002 E Unity: Invalid compute kernel index 6\\n')
            result = scan([p])
            self.assertEqual(result['root_line_counts'], {'kernel_index_6': 1})
            self.assertEqual(result['first_by_category']['kernel_index_6'],
                             '11-05 22:09:11.002')

    def test_symlink_and_duplicate_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            p = Path(tmp) / 'a'; p.write_text('test')
            with self.assertRaises(ValueError): scan([p, p])
            q = Path(tmp) / 'b'; q.symlink_to(p)
            with self.assertRaises(ValueError): scan([q])

if __name__ == '__main__':
    unittest.main()
