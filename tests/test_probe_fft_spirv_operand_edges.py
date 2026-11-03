"""Synthetic SPIR-V producer-edge fixtures without private shader bytes."""
import struct
import unittest

from scripts.probe_fft_spirv_operand_edges import (
    direct_producer_edges, compare_direct_producer_edges)


def spv(ops, bound=200):
    words = [0x07230203, 0x10000, 0, bound, 0]
    for opcode, operands in ops:
        words.extend([(1 + len(operands)) << 16 | opcode, *operands])
    return struct.pack("<" + "I" * len(words), *words)


class OperandEdgeTests(unittest.TestCase):
    def test_direct_tracked_edges_and_unknown_sources(self):
        p = direct_producer_edges(spv([
            (124, [1, 10, 99]),  # bitcast from untracked input
            (128, [1, 11, 10, 98]),  # bitcast -> integer add
            (132, [1, 12, 11, 10]),  # add and bitcast -> multiply
        ]))
        self.assertEqual(p["tracked_opcode_counts"]["124"], 1)
        self.assertEqual(p["direct_tracked_producer_edges"], [
            {"producer_opcode": 124, "consumer_opcode": 128, "uses": 1},
            {"producer_opcode": 124, "consumer_opcode": 132, "uses": 1},
            {"producer_opcode": 128, "consumer_opcode": 132, "uses": 1},
        ])
        self.assertEqual(p["tracked_operand_uses"], 5)
        self.assertEqual(p["operand_uses_from_untracked_producers"], 2)
        self.assertFalse(p["all_dependencies_classified"])
        self.assertFalse(p["numeric_or_device_equivalence_proven"])

    def test_identical_histogram_different_edges_detected(self):
        a = direct_producer_edges(spv([
            (124, [1, 10, 99]), (128, [1, 11, 10, 98]),
            (132, [1, 12, 11, 97])]))
        b = direct_producer_edges(spv([
            (124, [1, 10, 99]), (128, [1, 11, 96, 98]),
            (132, [1, 12, 10, 11])]))
        diff = compare_direct_producer_edges(a, b)
        self.assertTrue(diff["same_tracked_opcode_counts"])
        self.assertFalse(diff["same_direct_tracked_producer_edges"])
        self.assertEqual(len(diff["direct_tracked_edge_differences"]), 2)
        self.assertFalse(diff["identical_operands_or_semantic_equivalence_proven"])

    def test_phi_incoming_labels_not_value_edges(self):
        p = direct_producer_edges(spv([
            (124, [1, 10, 99]),
            (245, [1, 20, 10, 10, 99, 11]),
            (128, [1, 30, 20, 99]),
        ]))
        self.assertIn(
            {"producer_opcode": 124, "consumer_opcode": 245, "uses": 1},
            p["direct_tracked_producer_edges"])
        self.assertIn(
            {"producer_opcode": 245, "consumer_opcode": 128, "uses": 1},
            p["direct_tracked_producer_edges"])
        self.assertEqual(p["tracked_operand_uses"], 5)

    def test_phi_forward_value_backedge_is_recorded(self):
        p = direct_producer_edges(spv([
            (245, [1, 20, 30, 50]),
            (132, [1, 30, 20, 99]),
        ]))
        self.assertIn(
            {"producer_opcode": 132, "consumer_opcode": 245, "uses": 1},
            p["direct_tracked_producer_edges"])
        self.assertIn(
            {"producer_opcode": 245, "consumer_opcode": 132, "uses": 1},
            p["direct_tracked_producer_edges"])

    def test_same_edges_do_not_prove_numeric_semantics(self):
        a = direct_producer_edges(spv([(124, [1, 10, 90]),
                                       (128, [1, 11, 10, 91])]))
        b = direct_producer_edges(spv([(124, [1, 10, 88]),
                                       (128, [1, 11, 10, 92])]))
        result = compare_direct_producer_edges(a, b)
        self.assertTrue(result["same_direct_tracked_producer_edges"])
        self.assertFalse(result["identical_operands_or_semantic_equivalence_proven"])

    def test_invalid_word_stream_and_instruction_rejected(self):
        with self.assertRaisesRegex(ValueError, "module"):
            direct_producer_edges(spv([])[:-1])
        with self.assertRaisesRegex(ValueError, "header"):
            direct_producer_edges(b"NOPE" + spv([])[4:])
        for ops in ([(124, [1, 10])], [(128, [1, 10, 11])],
                    [(245, [1, 20, 30, 50, 40])]):
            with self.subTest(ops=ops), self.assertRaisesRegex(ValueError, "Malformed"):
                direct_producer_edges(spv(ops))

    def test_duplicate_or_out_of_range_tracked_result_fails(self):
        for ops in (
            [(124, [1, 10, 90]), (128, [1, 10, 80, 70])],
            [(124, [1, 200, 90])],
            [(132, [1, 10, 201, 70])],
            [(128, [1, 0, 80, 70])],
        ):
            with self.subTest(ops=ops), self.assertRaisesRegex(ValueError, "result/value ID"):
                direct_producer_edges(spv(ops))

    def test_comparison_rejects_boolean_and_bad_counters(self):
        p = direct_producer_edges(spv([(124, [1, 10, 90])]))
        bad = dict(p, tracked_opcode_counts=dict(p["tracked_opcode_counts"], **{"124": True}))
        with self.assertRaisesRegex(ValueError, "counters"):
            compare_direct_producer_edges(p, bad)
        bad = dict(p, tracked_operand_uses=300)
        with self.assertRaisesRegex(ValueError, "census"):
            compare_direct_producer_edges(p, bad)

    def test_output_excludes_private_ids_and_claims(self):
        result = direct_producer_edges(spv([(124, [1, 10, 193]),
                                           (128, [1, 11, 10, 194])]))
        self.assertNotIn("193", str(result))
        self.assertNotIn("194", str(result))
        self.assertFalse(result["private_shader_ids_or_values_disclosed"])
        self.assertTrue(result["bounded_subset_only"])


if __name__ == "__main__":
    unittest.main()
