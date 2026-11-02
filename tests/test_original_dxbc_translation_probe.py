"""No original Raft bytes used in fixture tests."""
import struct
import unittest
from scripts.run_original_dxbc_translation_probe import version_tokens


def original_public_fixture(kind=5, major=5, minor=0):
    program = struct.pack("<I", (kind << 16) | (major << 4) | minor) + b"synthetic only"
    offset = 36
    data = bytearray(36 + 8 + len(program))
    data[:4] = b"DXBC"
    struct.pack_into("<III", data, 20, 1, len(data), 1)
    struct.pack_into("<I", data, 32, offset)
    data[offset:offset + 4] = b"SHEX"
    struct.pack_into("<I", data, offset + 4, len(program))
    data[offset + 8:] = program
    return bytes(data)


class OriginalTranslationProbeTests(unittest.TestCase):
    def test_shader_version_fields_are_numeric_not_private_program(self):
        result = version_tokens(original_public_fixture())
        self.assertEqual(result, [{"shader_stage_code": 5, "shader_model": [5, 0]}])
        self.assertNotIn("synthetic only", str(result))

    def test_rejects_unrecognized_header(self):
        with self.assertRaisesRegex(ValueError, "Not DXBC"):
            version_tokens(b"wrong data")

    def test_reports_other_program_stages_without_assuming_compute(self):
        result = version_tokens(original_public_fixture(kind=1, major=4, minor=1))
        self.assertEqual(result[0]["shader_stage_code"], 1)
        self.assertEqual(result[0]["shader_model"], [4, 1])


if __name__ == "__main__":
    unittest.main()
