"""B18 source-free DXBC fixture: RDEF schema and original Unity slot parity."""
import copy
import json
import struct
import unittest

from scripts.b18_fft_compiled_rdef_bindings import compare, compiled_binding_hashes, compiled_shex_registers
from scripts.probe_fft_variant_table import EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT


ROLES = (("S", 2, 4, 0), ("B", 2, 4, 1), ("T", 4, 4, 0))


def dxbc(rows=ROLES, *, bad_offset=False, extra_rdef=False):
    names = b""
    records = b""
    for name, kind, dimension, register in rows:
        start = 28 + len(rows) * 32 + len(names)
        records += struct.pack("<8I", start, kind, 3, dimension, 0, register, 1, 0)
        names += name.encode("utf-8") + b"\x00"
    payload = struct.pack("<7I", 0, 0, len(rows), 8192 if bad_offset else 28, 0, 0, 0) + records + names
    chunks = [(b"RDEF", payload), (b"SHEX", b"\x00"*4)]
    if extra_rdef:
        chunks.append((b"RDEF", payload))
    directory_size = 32 + 4 * len(chunks)
    offsets = []
    body = b""
    for name, contents in chunks:
        offsets.append(directory_size + len(body))
        body += name + struct.pack("<I", len(contents)) + contents
        body += b"\x00" * (-len(body) % 4)
    header = b"DXBC" + b"\x00"*16 + struct.pack("<3I", 1, directory_size + len(body), len(chunks))
    header += struct.pack("<" + "I"*len(chunks), *offsets)
    return header + body


def fixture():
    def r(name, bind):
        return {"name": name, "bindPoint": bind, "texDimension": 2, "samplerBindPoint": -1}
    kernels = []
    for group in EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT:
        fields = {
            "textures": [r("S", 0), r("B", 1)], "outBuffers": [r("T", 0)],
            "cbs": [], "inBuffers": [], "builtinSamplers": [],
            "threadGroupSize": [group, 1, 1], "binaryFixture": list(dxbc()),
        }
        kernels.append({"variantMap": [(0, fields)]})
    return {"variants": [{"kernels": kernels}]}




def shex_dx(dst=ROLES, group=(64, 1, 1), *, extra_cb=False, corrupted=False, customdata=False, extended=False):
    """Public synthetic SM5 tokenized instructions: real ordinal layout only."""
    instructions = []
    if customdata:
        instructions.extend([53, 4, 0xdeadbeef, 0x12345678])
    if extended:
        instructions.extend([(2 << 24) | (1 << 31) | 58, 0])
    for _, kind, dimension, register in dst:
        op_id = 88 if kind == 2 else 156
        operand_type = 7 if kind == 2 else 30
        instructions.extend([(4 << 24) | (dimension - 1) << 11 | op_id,
                             (operand_type << 12) | (1 << 20), register, 0x5555])
    instructions.extend([(4 << 24) | 155, *group])
    if extra_cb:
        instructions.extend([(3 << 24) | 89, (8 << 12) | (1 << 20), 0])
    tokens = [(5 << 16) | (5 << 4), 2 + len(instructions) + int(corrupted)] + instructions
    payload = struct.pack("<" + "I" * len(tokens), *tokens)
    body = b"SHEX" + struct.pack("<I", len(payload)) + payload
    count = 1
    header = b"DXBC" + b"\x00"*16 + struct.pack("<3I", 1, 36 + len(body), count)
    header += struct.pack("<I", 36)
    return header + body


def shex_fixture():
    tree = fixture()
    for i, group_x in enumerate(EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT):
        tree["variants"][0]["kernels"][i]["variantMap"][0][1]["binaryFixture"] = list(shex_dx(group=(group_x, 1, 1)))
    return tree

class B18RDEFTests(unittest.TestCase):
    def test_positive_20_programs_no_private_names(self):
        summary = compare(fixture())
        self.assertEqual(summary["original_compiled_fft_rdef_slots_correlated"], 20)
        self.assertTrue(summary["rdef_to_unity_t0_t1_u0_identity_matched"])
        self.assertFalse(summary["android_device_pixels_verified"])
        self.assertNotIn('"S"', json.dumps(summary))
        self.assertNotIn('"B"', json.dumps(summary))
        self.assertNotIn('"T"', json.dumps(summary))

    def test_name_mismatch_is_not_silent(self):
        tree = fixture()
        changed = (("wrong", 2, 4, 0), ROLES[1], ROLES[2])
        tree["variants"][0]["kernels"][7]["variantMap"][0][1]["binaryFixture"] = list(dxbc(changed))
        with self.assertRaisesRegex(ValueError, "disagrees"):
            compare(tree)

    def test_swapped_compiled_registers_fail_even_with_valid_names(self):
        tree = fixture()
        swapped = (("S", 2, 4, 1), ("B", 2, 4, 0), ROLES[2])
        tree["variants"][0]["kernels"][19]["variantMap"][0][1]["binaryFixture"] = list(dxbc(swapped))
        with self.assertRaisesRegex(ValueError, "disagrees"):
            compare(tree)

    def test_missing_duplicate_out_of_range_and_wrong_resource_type(self):
        candidates = [
            ROLES[:2],
            (ROLES[0], ROLES[0], ROLES[2]),
            (ROLES[0], ROLES[1], ("T", 3, 4, 0)),
            (ROLES[0], ROLES[1], ("T", 4, 3, 0)),
            (ROLES[0], ROLES[1], ("T", 4, 4, 1025)),
        ]
        for candidate in candidates:
            with self.subTest(candidate=candidate), self.assertRaises(ValueError):
                compiled_binding_hashes(dxbc(candidate))

    def test_customdata_and_unrelated_extended_opcode_are_skipped_by_lengths(self):
        original = shex_dx(customdata=True, extended=True)
        slots, group = compiled_shex_registers(original)
        self.assertEqual(set(slots), {("input", 0), ("input", 1), ("output", 0)})
        self.assertEqual(group, [64, 1, 1])

    def test_bad_rdef_offset_duplicate_and_bad_container(self):
        for candidate in (dxbc(bad_offset=True), dxbc(extra_rdef=True), dxbc()[:-1],
                          b"NOPE" + dxbc()[4:]):
            with self.subTest(size=len(candidate)), self.assertRaises(ValueError):
                compiled_binding_hashes(candidate)

    def test_pointer_outside_string_area_rejected(self):
        corrupt = bytearray(dxbc())
        off = struct.unpack_from("<I", corrupt, 32)[0]
        struct.pack_into("<I", corrupt, off + 8 + 28, 1)
        with self.assertRaisesRegex(ValueError, "pointer"):
            compiled_binding_hashes(bytes(corrupt))

    def test_bad_utf8_resource_name_rejected(self):
        corrupt = bytearray(dxbc())
        off = struct.unpack_from("<I", corrupt, 32)[0]
        corrupt[off + 8 + 124] = 0xff
        with self.assertRaisesRegex(ValueError, "encoding"):
            compiled_binding_hashes(bytes(corrupt))

    def test_ambiguous_second_program_rejected(self):
        tree = fixture()
        tree["variants"][0]["kernels"][0]["variantMap"][0][1]["secondBinary"] = list(dxbc())
        with self.assertRaisesRegex(ValueError, "Ambiguous"):
            compare(tree)

    def test_shex_without_reflection_has_register_proof_not_name_proof(self):
        result = compare(shex_fixture())
        self.assertEqual(result["original_compiled_fft_shex_slots_correlated"], 20)
        self.assertEqual(result["original_compiled_fft_rdef_slots_correlated"], 0)
        self.assertFalse(result["rdef_to_unity_t0_t1_u0_identity_matched"])
        self.assertFalse(result["compiled_resource_names_proven_from_binary_when_no_rdef"])

    def test_shex_wrong_register_dimension_and_group_fail(self):
        for changed, group in (
            ((ROLES[0][0], 2, 4, 1), (64, 1, 1)),
            ((ROLES[0][0], 2, 3, 0), (64, 1, 1)),
            (ROLES[0], (128, 1, 1)),
        ):
            tree = shex_fixture()
            variant = list(ROLES)
            variant[0] = changed
            tree["variants"][0]["kernels"][0]["variantMap"][0][1]["binaryFixture"] = list(
                shex_dx(dst=variant, group=group))
            with self.assertRaises(ValueError):
                compare(tree)

    def test_shex_missing_resource_extra_cb_or_malformed_length_fail(self):
        for binary in (shex_dx(dst=ROLES[:2]), shex_dx(extra_cb=True),
                       shex_dx(corrupted=True)):
            with self.assertRaises(ValueError):
                compiled_shex_registers(binary)

    def test_tampered_unity_metadata_rejected(self):
        tree = fixture()
        tree["variants"][0]["kernels"][0]["variantMap"][0][1]["outBuffers"][0]["bindPoint"] = 1
        with self.assertRaises(ValueError):
            compare(tree)


if __name__ == "__main__":
    unittest.main()
