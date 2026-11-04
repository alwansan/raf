"""B18 source-free DXBC fixture: RDEF schema and original Unity slot parity."""
import copy
import json
import struct
import unittest

from scripts.b18_fft_compiled_rdef_bindings import compare, compiled_binding_hashes
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

    def test_tampered_unity_metadata_rejected(self):
        tree = fixture()
        tree["variants"][0]["kernels"][0]["variantMap"][0][1]["outBuffers"][0]["bindPoint"] = 1
        with self.assertRaises(ValueError):
            compare(tree)


if __name__ == "__main__":
    unittest.main()
