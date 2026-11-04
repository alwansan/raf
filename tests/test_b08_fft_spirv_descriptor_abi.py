"""B08 synthetic positive and mutation controls; no private shaders/assets."""
import struct
import unittest

from scripts.b08_fft_spirv_descriptor_abi import (
    describe_pair, require_shared_abi, check_executable_image_roles, EXPECTED_COUNT,
)


def source(groups=(64, 1, 1), registers=(0, 1, 0)):
    """Bounded synthetic cs_5_0 SHEX, no proprietary program."""
    instructions = []
    for kind, reg in zip(("read", "read", "write"), registers):
        op, typ = (88, 7) if kind == "read" else (156, 30)
        instructions.extend([(4 << 24) | (3 << 11) | op,
                             (typ << 12) | (1 << 20), reg, 0x5555])
    instructions.extend([(4 << 24) | 155, *groups])
    tokens = [(5 << 16) | (5 << 4), len(instructions) + 2, *instructions]
    code = struct.pack("<" + "I" * len(tokens), *tokens)
    return (b"DXBC" + b"\x00" * 16
            + struct.pack("<3I", 1, 44 + len(code), 1)
            + struct.pack("<I", 36) + b"SHEX"
            + struct.pack("<I", len(code)) + code)


def target(sets=(0, 0, 0), bindings=(0, 1, 2), sampled=(1, 1, 2),
           scalar_bits=32, group=(64, 1, 1), additional_entry=False,
           executable=False, fetched=(0, 1), written=True,
           unknown_read=False, storage_read=False):
    """Synthetic SPIR-V image descriptors with stable numeric type metadata."""
    words = []

    def put(op, *args):
        words.extend([(len(args) + 1) << 16 | op, *args])

    put(15, 5, 1, 0x6e69616d, 0)
    if additional_entry:
        put(15, 5, 2, 0x6e69616d, 0)
    put(16, 1, 17, *group)
    put(22, 10, scalar_bits)
    for i, (kind, slot, set_number) in enumerate(zip(sampled, bindings, sets)):
        image_id = 11 + i * 3
        pointer_id = image_id + 1
        var_id = image_id + 2
        put(25, image_id, 10, 1, 0, 0, 0, kind, 0)
        put(32, pointer_id, 0, image_id)
        put(59, pointer_id, var_id, 0)
        put(71, var_id, 34, set_number)
        put(71, var_id, 33, slot)
    if executable:
        for i in range(3):
            put(61, 11 + i*3, 80+i, 13+i*3)  # OpLoad image variable
        for i in fetched:
            put(95, 10, 100+i, 80+i, 42)    # OpImageFetch
        if written:
            put(99, 82, 42, 43)               # OpImageWrite
        if unknown_read:
            put(95, 10, 145, 199, 42)         # Unresolved dynamic ID
        if storage_read:
            put(95, 10, 146, 82, 42)          # Incorrect sampled read from UAV
    words = [0x07230203, 0x10000, 0, 200, 0] + words
    return struct.pack("<" + "I" * len(words), *words)


def good():
    return describe_pair(source(), target())


class B08DescriptorABI(unittest.TestCase):
    def test_valid_original_role_model_produces_numeric_abi(self):
        result = good()
        self.assertEqual(len(result["sampled_image_descriptor_candidates_unordered_t0_t1"]), 2)
        self.assertEqual(result["storage_output_image_descriptor_from_unique_uav_class"][:2], (0, 2))
        self.assertFalse(result["src_t0_vs_t1_mapping_verified"])

    def test_twenty_source_slots_accept_same_abi(self):
        result = require_shared_abi([good() for _ in range(EXPECTED_COUNT)])
        self.assertTrue(result["identical_numeric_image_descriptor_abi_across_compiled_slots"])
        self.assertEqual(len(result["verified_numeric_descriptor_abi_sha256"]), 64)
        self.assertFalse(result["source_t0_to_descriptor_identity_verified"])
        self.assertFalse(result["unity_findkernel_runtime_mapping_verified"])

    def test_reordered_sampled_variable_declaration_not_false_t0_mapping(self):
        original = good()
        reordered = describe_pair(source(), target(bindings=(1, 0, 2)))
        self.assertEqual(original, reordered)
        self.assertFalse(reordered["src_t0_vs_t1_mapping_verified"])

    def test_one_read_descriptor_moves_in_one_slot_refused(self):
        rows = [good() for _ in range(EXPECTED_COUNT)]
        rows[13] = describe_pair(source(), target(bindings=(0, 4, 2)))
        with self.assertRaises(ValueError):
            require_shared_abi(rows)

    def test_one_output_descriptor_moves_to_other_set_refused(self):
        rows = [good() for _ in range(EXPECTED_COUNT)]
        rows[-1] = describe_pair(source(), target(sets=(0, 0, 7)))
        with self.assertRaises(ValueError):
            require_shared_abi(rows)

    def test_image_scalar_precision_changes_in_one_slot_refused(self):
        rows = [good() for _ in range(EXPECTED_COUNT)]
        rows[2] = describe_pair(source(), target(scalar_bits=16))
        with self.assertRaises(ValueError):
            require_shared_abi(rows)

    def test_count_short_or_extra_refused(self):
        for total in (0, EXPECTED_COUNT - 1, EXPECTED_COUNT + 1):
            with self.assertRaises(ValueError):
                require_shared_abi([good() for _ in range(total)])

    def test_duplicate_binding_not_accepted(self):
        with self.assertRaises(ValueError):
            describe_pair(source(), target(bindings=(0, 0, 2)))

    def test_loss_of_storage_class_refused(self):
        with self.assertRaises(ValueError):
            describe_pair(source(), target(sampled=(1, 1, 1)))

    def test_loss_of_original_t1_register_refused(self):
        with self.assertRaises(ValueError):
            describe_pair(source(registers=(0, 2, 0)), target())

    def test_workgroup_drift_refused(self):
        with self.assertRaises(ValueError):
            describe_pair(source(), target(group=(128, 1, 1)))

    def test_two_entrypoints_refused(self):
        with self.assertRaises(ValueError):
            describe_pair(source(), target(additional_entry=True))

    def test_forged_t0_mapping_attestation_refused(self):
        rows = [good() for _ in range(EXPECTED_COUNT)]
        for row in rows:
            row["src_t0_vs_t1_mapping_verified"] = True
        with self.assertRaises(ValueError):
            require_shared_abi(rows)

    def test_forged_runtime_kernel_attestation_refused(self):
        rows = [good() for _ in range(EXPECTED_COUNT)]
        for row in rows:
            row["runtime_unity_kernel_id_mapping_verified"] = True
        with self.assertRaises(ValueError):
            require_shared_abi(rows)


    def test_executable_image_uses_cover_all_three_declared_resources(self):
        r = check_executable_image_roles(target(executable=True), good())
        self.assertTrue(r["both_sampled_descriptor_candidates_actively_read"])
        self.assertTrue(r["sole_storage_output_descriptor_actively_written"])
        self.assertFalse(r["source_DXBC_t0_t1_semantic_binding_verified"])

    def test_unused_original_source_input_fails_closed(self):
        with self.assertRaises(ValueError):
            check_executable_image_roles(target(executable=True, fetched=(0,)), good())

    def test_declared_but_unwritten_storage_fails_closed(self):
        with self.assertRaises(ValueError):
            check_executable_image_roles(target(executable=True, written=False), good())

    def test_unresolved_executable_spirv_image_use_fails_closed(self):
        with self.assertRaises(ValueError):
            check_executable_image_roles(target(executable=True, unknown_read=True), good())

    def test_unexpected_storage_read_as_sampled_input_fails_closed(self):
        with self.assertRaises(ValueError):
            check_executable_image_roles(target(executable=True, storage_read=True), good())

    def test_declarations_without_image_operations_do_not_prove_readiness(self):
        with self.assertRaises(ValueError):
            check_executable_image_roles(target(), good())


if __name__ == "__main__":
    unittest.main()
