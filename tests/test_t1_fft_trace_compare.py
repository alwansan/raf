import struct
import unittest

from scripts.t1_fft_trace_compare import RECORD, SIZE, compare


BASE = [(0, 1, 2, 0, 10, 0, 0, 0), (1, 1, 2, 0, 20, 0, 0, 0),
        (2, 1, 2, 0, 30, 0, 0, 0)]


def trace(rows, count=None):
    return (struct.pack("<I", len(rows) if count is None else count) +
            b"".join(RECORD.pack(*row) for row in rows)).ljust(SIZE, b"\0")


class TraceCompareTests(unittest.TestCase):
    def test_order_independent_with_repeated_reads(self):
        rows = BASE + [BASE[0]]
        self.assertTrue(compare(trace(rows), trace(rows[::-1]))["match"])

    def test_separates_coordinate_and_value_drift(self):
        rows = [(0, 9, 2, 0, 10, 0, 0, 0), (1, 1, 2, 0, 21, 0, 0, 0), BASE[2]]
        result = compare(trace(BASE), trace(rows))
        self.assertFalse(result["match"])
        self.assertEqual(result["sites"][0], {"missing_coordinate_records": 1,
            "extra_coordinate_records": 1, "value_records_compared": 0, "value_bit_mismatches": 0})
        self.assertEqual(result["sites"][1]["value_bit_mismatches"], 1)

    def test_rejects_overflow_and_missing_site(self):
        for bad in (trace(BASE, 513), trace(BASE[:2]), trace(BASE)[:-1]):
            with self.assertRaises(ValueError):
                compare(trace(BASE), bad)
