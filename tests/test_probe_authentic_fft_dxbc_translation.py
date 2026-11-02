"""Synthetic SPIR-V reflection contract; never uses original game shader bytes."""
import struct
import unittest
from scripts.probe_authentic_fft_dxbc_translation import spirv_resource_bindings

def make_spv(instructions):
    words = [0x07230203, 0x00010000, 0, 16, 0]
    for op, operands in instructions:
        words.extend([(1 + len(operands)) << 16 | op, *operands])
    return struct.pack("<" + "I" * len(words), *words)

class FftSpirvBindingTests(unittest.TestCase):
    def test_returns_numeric_set_binding_only(self):
        spv = make_spv([(71, [7, 33, 2]), (71, [7, 34, 0]),
                        (71, [9, 33, 6]), (71, [9, 34, 1])])
        info = spirv_resource_bindings(spv)
        self.assertEqual(info["descriptor_binding_pairs"], [[0, 2], [1, 6]])
        self.assertEqual(info["targets_with_explicit_binding"], 2)
        self.assertFalse(info["resource_names_disclosed"])

    def test_unset_descriptor_set_does_not_fabricate_set_zero(self):
        spv = make_spv([(71, [7, 33, 12])])
        self.assertEqual(spirv_resource_bindings(spv)["descriptor_binding_pairs"], [[None, 12]])

    def test_rejects_truncation_and_wrong_magic(self):
        with self.assertRaisesRegex(ValueError, "truncated"):
            spirv_resource_bindings(b"\x00" * 8)
        spv = make_spv([(71, [7, 33, 2])])
        with self.assertRaisesRegex(ValueError, "header"):
            spirv_resource_bindings(b"NOPE" + spv[4:])
        with self.assertRaisesRegex(ValueError, "instruction boundary"):
            spirv_resource_bindings(spv[:-4])


if __name__ == "__main__":
    unittest.main()
