import struct
import unittest
from scripts.w1_recover_graphics_programs import records


class OriginalGraphicsSegments(unittest.TestCase):
    def test_nonzero_segment_uses_own_offset(self):
        table = struct.pack('<I6I', 2, 28, 4, 0, 2, 4, 1) + b'base'
        self.assertEqual(records([table, b'XXnextYY']), [(0, b'base'), (1, b'next')])

    def test_wrong_segment_and_ranges_rejected(self):
        for offset, size, segment in [(0, 4, 2), (9, 4, 1), (0, 0, 1), (4, 4, 0)]:
            with self.subTest(offset=offset, size=size, segment=segment):
                with self.assertRaises(ValueError):
                    records([struct.pack('<4I', 1, offset, size, segment), b'abcd'])

    def test_truncated_table_and_missing_segment_rejected(self):
        for segments in ([], [b''], [struct.pack('<I', 1000000)], [struct.pack('<4I', 1, 0, 4, 1)]):
            with self.assertRaises(ValueError):
                records(segments)


if __name__ == '__main__':
    unittest.main()
