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
        ops.insert(7, (83, [2, 30, 20]))
        ops[8] = (99, [30, 42, 43])
        r = image_slot_dataflow(spv(ops))
        self.assertEqual(r["image_operand_slot_uses"]["write"]["total"], 1)
        self.assertEqual(r["image_operand_slot_uses"]["write"]["unresolved_count"], 0)
        self.assertEqual(r["image_operand_slot_uses"]["write"]["resolved_slot_counts"][0]["binding"], 2)

    def test_unresolved_and_ambiguous_reported_not_guessed(self):
        ops = example()
        ops[8] = (99, [199, 42, 43])
        r = image_slot_dataflow(spv(ops))
        self.assertFalse(r["all_image_operations_uniquely_traced"])
        self.assertEqual(r["image_operand_slot_uses"]["write"]["unresolved_count"], 1)

    def test_select_with_unknown_arm_cannot_claim_unique_binding(self):
        ops = example()
        ops.insert(7, (169, [2, 30, 50, 20, 199]))
        ops[8] = (99, [30, 42, 43])
        r = image_slot_dataflow(spv(ops))
        self.assertFalse(r["all_image_operations_uniquely_traced"])
        self.assertEqual(r["image_operand_slot_uses"]["write"]["unresolved_count"], 1)

    def test_missing_descriptor_set_is_unresolved(self):
        ops = [row for row in example() if row != (71, [5, 34, 0])]
        r = image_slot_dataflow(spv(ops))
        self.assertFalse(r["all_image_operations_uniquely_traced"])
        self.assertEqual(r["image_operand_slot_uses"]["write"]["unresolved_count"], 1)

    def test_distinct_select_bindings_are_ambiguous(self):
        ops = example()
        ops.insert(7, (169, [2, 30, 50, 20, 6]))
        ops[8] = (99, [30, 42, 43])
        r = image_slot_dataflow(spv(ops))
        self.assertEqual(r["image_operand_slot_uses"]["write"]["ambiguous_count"], 1)

    def test_invalid_input_fails_closed(self):
        with self.assertRaises(ValueError):
            image_slot_dataflow(spv(example())[:-4])
        with self.assertRaises(ValueError):
            image_slot_dataflow(b"X" * 12)
        with self.assertRaises(ValueError):
            image_slot_dataflow(spv(example() + [(71, [5, 33, 4])]))

    def test_duplicate_load_id_cannot_rewrite_uniquely_traced_binding(self):
        ops = example()
        ops.insert(7, (61, [2, 20, 6]))  # previously overwrote 20: set0/binding2 -> binding0
        with self.assertRaisesRegex(ValueError, "Repeated SPIR-V tracked result ID"):
            image_slot_dataflow(spv(ops))

    def test_alias_id_must_not_shadow_declared_variable(self):
        ops = example()
        ops.insert(7, (83, [2, 5, 20]))  # variable 5 owns original set0/binding2
        with self.assertRaisesRegex(ValueError, "Repeated SPIR-V tracked result ID"):
            image_slot_dataflow(spv(ops))

    def test_variable_id_must_not_shadow_earlier_alias(self):
        with self.assertRaisesRegex(ValueError, "Repeated SPIR-V tracked result ID"):
            image_slot_dataflow(spv(example() + [(59, [2, 20, 0])]))

    def test_select_and_phi_must_not_redefine_existing_load_id(self):
        for operation in ((169, [2, 20, 50, 5, 6]),
                          (245, [2, 20, 5, 80, 6, 81])):
            with self.subTest(operation=operation[0]):
                ops = example()
                ops.insert(7, operation)
                with self.assertRaisesRegex(ValueError, "Repeated SPIR-V tracked result ID"):
                    image_slot_dataflow(spv(ops))

    def test_no_private_name_or_semantic_claim(self):
        r = image_slot_dataflow(spv(example()))
        self.assertFalse(r["private_shader_ids_or_names_disclosed"])
        self.assertFalse(r["source_semantic_equivalence_or_device_execution_proven"])


if __name__ == "__main__":
    unittest.main()
