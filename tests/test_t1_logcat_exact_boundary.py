"""Regression for the physical-line boundary in T1 LogRaft scanner."""
import tempfile
import unittest
from pathlib import Path
from scripts.t1_water_logcat_first_roots import scan


class ExactBoundaryTest(unittest.TestCase):
    def test_unterminated_full_chunk_is_not_a_log_record(self):
        prefix = b'11-05 22:09:11.559 invalid kernel index 6 '
        # 32768 bytes of valid-looking text, then more bytes and newline.
        physical = prefix + b'x' * (32768 - len(prefix)) + b' continuation\n'
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'log.txt'
            p.write_bytes(physical)
            self.assertEqual(scan([p])['root_line_counts'], {})

    def test_newline_terminated_full_chunk_is_valid(self):
        prefix = b'11-05 22:09:11.559 invalid kernel index 6 '
        physical = prefix + b'x' * (32767 - len(prefix)) + b'\n'
        self.assertEqual(len(physical), 32768)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'log.txt'
            p.write_bytes(physical)
            self.assertEqual(scan([p])['root_line_counts'], {'kernel_index_6': 1})


if __name__ == '__main__':
    unittest.main()
