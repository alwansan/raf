"""Synthetic SSA image operand tracing; zero original game shader bytes."""
import struct
import unittest
from scripts.probe_fft_spirv_image_flow import image_slot_dataflow


def spv(ops):
    words = [0x07230203, 0x10000, 0, 200, 0]
    for op, args in ops:
        words.extend([(1 + len(args)) << 16 | op, *args])
    return struct.pack("<" + "I" * len(words), *words)


def example():
    return [
        (59, [2, 5, 0]), (71, [5, 33, 2]), (71, [5, 34, 0]),
        (59, [2, 6, 0]), (71, [6, 33, 0]), (71, [6, 34, 0]),
        (61, [2, 20, 5]), (99, [20, 42, 43]),
        (61, [2, 21, 6]), (95, [3, 44, 21, 45]),
    ]


class ImageFlowTests(unittest.TestCase):
    def test_direct_load_and_fetch_bindings_are_proven(self):
        r = image_slot_dataflow(spv(example()))
        self.assertTrue(r["all_image_operations_uniquely_traced"])
        self.assertEqual(r["image_operand_slot_uses"]["write"]["resolved_slot_counts"],
                         [{"descriptor_set": 0, "binding": 2, "calls": 1}])
        self.assertEqual(r["image_operand_slot_uses"]["fetch"]["resolved_slot_counts"],
                         [{"descriptor_set": 0, "binding": 0, "calls": 1}])

    def test_copy_and_access_chain_track_variable(self):
        ops = example()
        ops.insert(-2, (83, [2, 30, 20]))
        ops[8] = (99, [30, 42, 43])
        r = image_slot_dataflow(spv(ops))
        self.assertEqual(r["image_operand_slot_uses"]["write"]["resolved_slot_counts"][0]["binding"], 2)

    def test_unresolved_and_ambiguous_reported_not_guessed(self):
        ops = example()
        ops[8] = (99, [199, 42, 43])
        r = image_slot_dataflow(spv(ops))
        self.assertFalse(r["all_image_operations_uniquely_traced"])
        self.assertEqual(r["image_operand_slot_uses"]["write"]["unresolved_count"], 1)

    def test_invalid_input_fails_closed(self):
        with self.assertRaises(ValueError):
            image_slot_dataflow(spv(example())[:-4])
        with self.assertRaises(ValueError):
            image_slot_dataflow(b"X" * 12)
        with self.assertRaises(ValueError):
            image_slot_dataflow(spv(example() + [(71, [5, 33, 4])]))

    def test_no_private_name_or_semantic_claim(self):
        r = image_slot_dataflow(spv(example()))
        self.assertFalse(r["private_shader_ids_or_names_disclosed"])
        self.assertFalse(r["source_semantic_equivalence_or_device_execution_proven"])


if __name__ == "__main__":
    unittest.main()
