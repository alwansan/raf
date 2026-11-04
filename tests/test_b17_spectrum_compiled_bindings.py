"""Source-free synthetic positive and negative checks for B17 Spectrum registers."""
import struct
import unittest

from scripts.b17_spectrum_compiled_bindings import (
    compiled_declarations, serialized_slots, compare_program,
)


def dxbc(*, stage=0, tex=(0, 1), samplers=((0, 0),), uavs=(),
         duplicate=False, corrupt=False, extra_resource=False):
    words = []
    for slot in tex:
        words += [(4 << 24) | (3 << 11) | 88, (7 << 12) | (1 << 20), slot, 0x5555]
    for slot, mode in samplers:
        words += [(3 << 24) | (mode << 11) | 90, (6 << 12) | (1 << 20), slot]
    for slot in uavs:
        words += [(4 << 24) | (3 << 11) | 156, (30 << 12) | (1 << 20), slot, 0x5555]
    if duplicate:
        words += [(4 << 24) | (3 << 11) | 88, (7 << 12) | (1 << 20), tex[0], 0x5555]
    if extra_resource:
        words += [(3 << 24) | 161, 0, 0]
    words += [(2 << 24) | 58, 0]
    tokens = [(stage << 16) | (5 << 4), len(words) + 2 + int(corrupt)] + words
    body = struct.pack("<" + "I" * len(tokens), *tokens)
    offset = 36
    header = b"DXBC" + b"\0"*16 + struct.pack("<3I", 1, offset + 8 + len(body), 1)
    return header + struct.pack("<I", offset) + b"SHEX" + struct.pack("<I", len(body)) + body


def program(tex=(0, 1), samplers=(), sampler_in_texture=None, uavs=()):
    texture_rows = []
    for index in tex:
        item = {"m_Index": index, "m_NameIndex": 0}
        if sampler_in_texture is not None:
            item["m_SamplerIndex"] = sampler_in_texture
        texture_rows.append(item)
    return {"m_CommonParameters": {
        "m_TextureParams": texture_rows,
        "m_SamplerParams": [{"m_Index": s} for s in samplers],
        "m_UAVParams": [{"m_Index": u} for u in uavs],
    }}


class SpectrumCompiledBindingsTests(unittest.TestCase):
    def test_compiled_texture_sampler_numeric_parity(self):
        row = compare_program(program(sampler_in_texture=0), dxbc(), 0)
        self.assertTrue(all(row["numeric_slot_parity"].values()))
        self.assertEqual(row["compiled_counts"], {"texture": 2, "sampler": 1, "uav": 0})
        self.assertFalse(row["names_or_material_sampler_states_verified"])

    def test_compiled_variant_order_is_irrelevant(self):
        row = compare_program(program(sampler_in_texture=1),
                              dxbc(tex=(1, 0), samplers=((1, 1),)), 0)
        self.assertTrue(all(row["numeric_slot_parity"].values()))
        self.assertEqual(row["compiled_sampler_modes"], [1])

    def test_compiled_mismatch_not_silently_accepted(self):
        row = compare_program(program(sampler_in_texture=0), dxbc(tex=(1, 3)), 0)
        self.assertFalse(row["numeric_slot_parity"]["texture"])

    def test_explicit_implicit_sampler_union(self):
        self.assertEqual(serialized_slots(program(samplers=(2,), sampler_in_texture=0))["sampler"], {0, 2})

    def test_sentinel_sampler_unbound(self):
        self.assertEqual(serialized_slots(program(sampler_in_texture=65535))["sampler"], set())
        self.assertEqual(serialized_slots(program(sampler_in_texture=-1))["sampler"], set())

    def test_sampler_mismatch_reported(self):
        row = compare_program(program(sampler_in_texture=0), dxbc(samplers=((2, 0),)), 0)
        self.assertFalse(row["numeric_slot_parity"]["sampler"])

    def test_uav_parity(self):
        row = compare_program(program(uavs=(2,), sampler_in_texture=0), dxbc(uavs=(2,)), 0)
        self.assertTrue(all(row["numeric_slot_parity"].values()))

    def test_duplicate_compiled_register_refused(self):
        with self.assertRaisesRegex(ValueError, "Duplicate compiled"):
            compiled_declarations(dxbc(duplicate=True), 0)

    def test_wrong_shader_stage_refused(self):
        with self.assertRaisesRegex(ValueError, "stage/version"):
            compiled_declarations(dxbc(stage=1), 0)

    def test_corrupt_declared_length_refused(self):
        with self.assertRaisesRegex(ValueError, "stage/version"):
            compiled_declarations(dxbc(corrupt=True), 0)

    def test_unknown_resource_declaration_refused(self):
        with self.assertRaisesRegex(ValueError, "Unsupported compiled"):
            compiled_declarations(dxbc(extra_resource=True), 0)

    def test_wrong_compiled_operand_type_refused(self):
        bad = bytearray(dxbc())
        struct.pack_into("<I", bad, 56, (8 << 12) | (1 << 20))
        with self.assertRaisesRegex(ValueError, "indexing"):
            compiled_declarations(bytes(bad), 0)

    def test_boolean_not_numeric_slot(self):
        with self.assertRaisesRegex(ValueError, "noninteger"):
            serialized_slots(program(tex=(True,)))

    def test_duplicate_serialized_slot_refused(self):
        with self.assertRaisesRegex(ValueError, "Duplicate serialized"):
            serialized_slots(program(tex=(0, 0)))

    def test_missing_table_not_equal_empty(self):
        p = program()
        del p["m_CommonParameters"]["m_SamplerParams"]
        with self.assertRaisesRegex(ValueError, "Missing or ambiguous"):
            serialized_slots(p)

    def test_ambiguous_aliases_refused(self):
        p = program()
        p["m_CommonParameters"]["m_SamplerParameters"] = []
        with self.assertRaisesRegex(ValueError, "Missing or ambiguous"):
            serialized_slots(p)

    def test_invalid_negative_sampler_index_refused(self):
        with self.assertRaisesRegex(ValueError, "Invalid original texture sampler"):
            serialized_slots(program(sampler_in_texture=-2))


if __name__ == "__main__":
    unittest.main()
