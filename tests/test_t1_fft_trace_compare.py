import struct
import unittest

from scripts.t1_fft_trace_compare import (
    INVOCATION_RECORD, INVOCATION_SIZE, RECORD, SIZE, axis_mapping, compare, compare_invocations,
)


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

INVOCATIONS = [(site, 3, 0, 0, 0, *sample) for site, *sample in BASE]


def invocation_trace(rows):
    return (struct.pack("<I", len(rows)) +
            b"".join(INVOCATION_RECORD.pack(*row) for row in rows)).ljust(INVOCATION_SIZE, b"\0")


class InvocationTraceTests(unittest.TestCase):
    def test_keys_pair_across_order_and_repeated_reads(self):
        repeated = (0, 3, 0, 0, 1, *BASE[0][1:])
        rows = INVOCATIONS + [repeated]
        self.assertTrue(compare_invocations(invocation_trace(rows),
                                            invocation_trace(rows[::-1]))["match"])

    def test_swapped_coordinates_hide_drift_in_the_legacy_histogram(self):
        first = (0, 3, 0, 0, 0, 1, 2, 0, 10, 0, 0, 0)
        second = (0, 4, 0, 0, 0, 9, 2, 0, 20, 0, 0, 0)
        before = [first, second, *INVOCATIONS[1:]]
        after = [(*first[:5], *second[5:]), (*second[:5], *first[5:]),
                 (*INVOCATIONS[1][:-4], 99, 0, 0, 0), INVOCATIONS[2]]
        self.assertTrue(compare(trace([row[:1] + row[5:] for row in before[:2] + INVOCATIONS[1:]]),
                                trace([row[:1] + row[5:] for row in after[:2] + INVOCATIONS[1:]]))["match"])
        result = compare_invocations(invocation_trace(before), invocation_trace(after))
        self.assertFalse(result["match"])
        self.assertEqual(result["sites"][0]["coordinate_mismatches"], 2)
        self.assertEqual(result["sites"][0]["changed_coordinate_value_mismatches"], 2)
        self.assertEqual(result["sites"][1]["same_coordinate_value_mismatches"], 1)

    def test_missing_and_extra_invocations_do_not_certify_parity(self):
        other = (0, 4, *INVOCATIONS[0][2:])
        result = compare_invocations(invocation_trace(INVOCATIONS),
                                     invocation_trace([other, *INVOCATIONS[1:]]))
        self.assertFalse(result["match"])
        self.assertEqual(result["sites"][0]["missing_reads"], 1)
        self.assertEqual(result["sites"][0]["extra_reads"], 1)
        self.assertEqual(result["sites"][0]["paired_reads"], 0)

    def test_rejects_duplicate_keys_and_legacy_layout(self):
        for bad in (invocation_trace(INVOCATIONS + INVOCATIONS[:1]), trace(BASE)):
            with self.assertRaises(ValueError):
                compare_invocations(invocation_trace(INVOCATIONS), bad)

    def test_counts_each_coordinate_axis_without_exporting_coordinates(self):
        rows = list(INVOCATIONS)
        row = rows[0]
        rows[0] = (*row[:5], row[5], row[6] + 1, row[7] + 1, *row[8:])
        result = compare_invocations(invocation_trace(INVOCATIONS), invocation_trace(rows))
        self.assertEqual(result["sites"][0]["coordinate_mismatches"], 1)
        self.assertEqual(result["sites"][0]["coordinate_axis_mismatches"],
                         {"x": 0, "y": 1, "mip": 1})

    def test_identity_coordinates_are_not_reported_as_translation(self):
        mapping = axis_mapping([(1, 1), (2, 2), (3, 3)])
        self.assertTrue(mapping["varied_reference"])
        self.assertFalse(mapping["uniform_translation"])
        self.assertFalse(mapping["uniform_reflection"])
        self.assertFalse(mapping["constant_observed"])

    def test_identical_invocation_coordinates_do_not_claim_address_shift(self):
        first = (0, 3, 0, 0, 0, 1, 2, 0, 10, 0, 0, 0)
        second = (0, 4, 0, 0, 0, 2, 2, 0, 20, 0, 0, 0)
        rows = [first, second, *INVOCATIONS[1:]]
        result = compare_invocations(invocation_trace(rows), invocation_trace(rows))
        self.assertTrue(result["match"])
        mapping = result["sites"][0]["coordinate_axis_mapping"]["x"]
        self.assertTrue(mapping["varied_reference"])
        self.assertFalse(mapping["uniform_translation"])
        self.assertFalse(mapping["uniform_reflection"])

    def test_axis_mapping_discriminates_address_shapes(self):
        for name, pairs in (
            ("uniform_translation", [(1, 4), (2, 5), (3, 6)]),
            ("uniform_reflection", [(1, 6), (2, 5), (3, 4)]),
            ("constant_observed", [(1, 6), (2, 6), (3, 6)]),
        ):
            mapping = axis_mapping(pairs)
            self.assertEqual({key for key, matched in mapping.items() if matched},
                             {"varied_reference", name})
        self.assertFalse(any(axis_mapping([(1, 9), (1, 9)]).values()))
        self.assertFalse(any(axis_mapping([]).values()))
