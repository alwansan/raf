"""Synthetic typed-image SPIR-V tests; no original source or shader data."""
import struct
import unittest
from scripts.probe_fft_spirv_images import image_resource_contracts


def spv(instructions):
    words = [0x07230203, 0x00010000, 0, 32, 0]
    for opcode, args in instructions:
        words.extend([(len(args) + 1) << 16 | opcode, *args])
    return struct.pack("<" + "I" * len(words), *words)


def example():
    return [(22, [1, 32]), (25, [2, 1, 1, 0, 0, 0, 2, 2]),
            (32, [3, 0, 2]), (59, [3, 4, 0]),
            (71, [4, 33, 2]), (71, [4, 34, 0])]


class ImageContractTests(unittest.TestCase):
    def test_storage_rgba16f_module_declaration(self):
        result = image_resource_contracts(spv(example()))
        self.assertEqual(result["typed_image_declarations"][0], {
            "set": 0, "binding": 2, "scalar_kind": "float", "scalar_bits": 32,
            "dimension_enum": 1, "depth_enum": 0, "arrayed": 0,
            "multisampled": 0, "sampled_enum": 2, "format_enum": 2,
            "access_enum": None,
        })
        self.assertFalse(result["unity_format_proven"])
        self.assertFalse(result["gpu_execution_proven"])

    def test_sampled_image_type_wrapper(self):
        data = example()
        data.insert(2, (27, [5, 2]))
        data[3] = (32, [3, 0, 5])
        self.assertEqual(image_resource_contracts(spv(data))["count"], 1)

    def test_non_image_descriptor_not_fabricated(self):
        data = example()
        data[2] = (32, [3, 0, 7])
        self.assertEqual(image_resource_contracts(spv(data))["count"], 0)

    def test_missing_binding_fails(self):
        with self.assertRaisesRegex(ValueError, "binding missing"):
            image_resource_contracts(spv(example()[:-2]))

    def test_repeated_decoration_fails(self):
        with self.assertRaisesRegex(ValueError, "Repeated"):
            image_resource_contracts(spv(example() + [(71, [4, 33, 3])]))

    def test_missing_scalar_type_fails(self):
        with self.assertRaisesRegex(ValueError, "component type"):
            image_resource_contracts(spv(example()[1:]))

    def test_truncated_instruction_fails(self):
        with self.assertRaises(ValueError):
            image_resource_contracts(spv(example())[:-4])

    def test_no_fabricated_set_zero(self):
        info = image_resource_contracts(spv(example()[:-1]))
        self.assertIsNone(info["typed_image_declarations"][0]["set"])

    def test_conflicting_resource_slots_fail(self):
        data = example() + [(59, [3, 6, 0]), (71, [6, 33, 2]),
                            (71, [6, 34, 0])]
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            image_resource_contracts(spv(data))


if __name__ == "__main__":
    unittest.main()
