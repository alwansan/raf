"""Pure synthetic Shader Model 4/5 declaration parser regressions."""
import struct
import unittest
from scripts.a12r_dx11_cb_declarations import declarations


def pack(*values):
    return struct.pack("<" + "I" * len(values), *values)


def compiled(register_sizes=((0, 11), (1, 23)), bad_operand=None, shader_tag=b"SHDR"):
    code = [0x00010040, 0]
    for slot, reg_count in register_sizes:
        operand = (8 << 12) | (2 << 20) if bad_operand is None else bad_operand
        code += [(4 << 24) | 89, operand, slot, reg_count]
    code[1] = len(code)
    chunk = shader_tag + pack(len(code) * 4) + pack(*code)
    return b"DXBC" + b"\0" * 16 + pack(1, 36 + len(chunk), 1, 36) + chunk


class DxbcCbDeclarationTests(unittest.TestCase):
    def test_valid_original_style_slots_and_bytes(self):
        self.assertEqual(declarations(compiled()), {0: 176, 1: 368})

    def test_fragment_shader_works(self):
        self.assertEqual(declarations(compiled(((2, 5),), shader_tag=b"SHEX")), {2: 80})

    def test_duplicate_slot_refused(self):
        with self.assertRaisesRegex(ValueError, "unsafe_cb"):
            declarations(compiled(((1, 3), (1, 4))))

    def test_non_immediate_operand_refused(self):
        bad = (8 << 12) | (2 << 20) | (2 << 22)
        with self.assertRaisesRegex(ValueError, "unsupported_cb_operand"):
            declarations(compiled(bad_operand=bad))

    def test_bad_operand_type_refused(self):
        with self.assertRaisesRegex(ValueError, "unsupported_cb_operand"):
            declarations(compiled(bad_operand=(7 << 12) | (2 << 20)))

    def test_zero_unknown_cb_size_not_claimed(self):
        with self.assertRaisesRegex(ValueError, "unsafe_cb"):
            declarations(compiled(((0, 0),)))

    def test_missing_declaration_refused(self):
        with self.assertRaisesRegex(ValueError, "no_constant_buffers"):
            declarations(compiled(()))

    def test_truncated_bytecode_refused(self):
        with self.assertRaises(ValueError):
            declarations(compiled()[:-2])

    def test_invalid_instruction_length_refused(self):
        code = bytearray(compiled())
        offset = 36 + 8 + 8
        struct.pack_into("<I", code, offset, 89)
        with self.assertRaisesRegex(ValueError, "bad_instruction_size"):
            declarations(bytes(code))


if __name__ == "__main__":
    unittest.main()
