import struct
import tempfile
from pathlib import Path
import unittest

from scripts.t1_fft_candidate_keyed_trace_audit import analyze, read_and_analyze
from scripts.t1_fft_trace_compare import INVOCATION_RECORD, INVOCATION_SIZE


def candidate(rows):
    result = bytearray(INVOCATION_SIZE)
    struct.pack_into("<I", result, 0, len(rows))
    for i, row in enumerate(rows):
        offset = 4 + i * INVOCATION_RECORD.size
        result[offset:offset + INVOCATION_RECORD.size] = INVOCATION_RECORD.pack(*row)
    return bytes(result)


RECORDS = [
    (site, 8, 4, 0, 0, 2, 3, 0, 11, 0, 0, 0)
    for site in range(3)
]


class ActualCandidateTraceValidationTests(unittest.TestCase):
    def test_three_nonempty_sites_and_keyed_record_type(self):
        a = analyze(candidate(RECORDS))
        self.assertEqual(a["records_by_site"], [1, 1, 1])
        self.assertTrue(a["unique_invocation_keys_verified"])
        self.assertFalse(a["original_spirv_keyed_capture_present"])
        self.assertFalse(a["independent_pair_comparison_performed"])
        self.assertFalse(a["vulkan_vs_unity_numeric_parity_proven"])
        self.assertNotIn("8, 4", str(a))

    def test_reordered_records_are_accepted(self):
        self.assertEqual(analyze(candidate(RECORDS[::-1]))["records_by_site"], [1, 1, 1])

    def test_second_invocation_in_one_site_increments_count(self):
        second = (1, 8, 4, 0, 1, 7, 8, 0, 12, 0, 0, 0)
        self.assertEqual(analyze(candidate(RECORDS + [second]))["records_by_site"], [1, 2, 1])

    def test_duplicate_key_cannot_claim_valid_capture(self):
        with self.assertRaises(ValueError):
            analyze(candidate(RECORDS + RECORDS[:1]))

    def test_no_records_is_invalid(self):
        with self.assertRaises(ValueError):
            analyze(bytes(INVOCATION_SIZE))

    def test_missing_site_is_invalid(self):
        with self.assertRaises(ValueError):
            analyze(candidate(RECORDS[:2]))

    def test_bad_capture_size_fails_closed(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "trace.bin"
            for item in (candidate(RECORDS)[:-1], candidate(RECORDS) + b"x"):
                path.write_bytes(item)
                with self.assertRaises(ValueError):
                    read_and_analyze(path)

    def test_binary_values_never_appear_in_summary(self):
        extreme = [(0, 4, 0, 0, 0, 200, -1, 0, 0xffffffff, 0, 0, 0),
                   (1, 4, 0, 0, 0, 201, -2, 0, 0xffffffff, 0, 0, 0),
                   (2, 4, 0, 0, 0, 202, -3, 0, 0xffffffff, 0, 0, 0)]
        report = analyze(candidate(extreme))
        self.assertNotIn("4294967295", str(report))
        self.assertNotIn("-3", str(report))
        self.assertEqual(report["records_by_site"], [1, 1, 1])


if __name__ == "__main__":
    unittest.main()
