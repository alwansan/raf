"""Synthetic bytecode container tests; no Unity, DirectX runtime or Raft assets."""
import struct
import unittest

from scripts.probe_directx_shader_bridge import inspect, inspect_dxbc, inspect_spirv


def dxbc(tag=b"SHDR", payload=b"DO_NOT_PRINT_PRIVATE_SHADER"):
    offset = 36
    data = bytearray(offset + 8 + len(payload))
    data[:4] = b"DXBC"
    struct.pack_into("<III", data, 20, 1, len(data), 1)
    struct.pack_into("<I", data, 32, offset)
    data[offset:offset + 4] = tag
    struct.pack_into("<I", data, offset + 4, len(payload))
    data[offset + 8:] = payload
    return bytes(data)


def spirv():
    # Valid-looking structural subset with an OpEntryPoint/LocalSize. We do
    # not claim full SPIR-V validation; real spirv-val runs in the lab CI.
    words = [
        0x07230203, 0x00010000, 0, 20, 0,
        0x00020011, 1,
        0x0003000e, 0, 1,
        0x0005000f, 5, 1, 0x6e69616d, 0,
        0x00060010, 1, 17, 8, 8, 1,
    ]
    return struct.pack("<" + "I" * len(words), *words)


class ShaderBridgeTests(unittest.TestCase):
    def test_dxbc_chunk_tags_never_expose_original_bytecode(self):
        result = inspect(dxbc())
        self.assertEqual(result["container"], "DXBC")
        self.assertEqual(result["chunk_tags"], {"SHDR": 1})
        self.assertTrue(result["executable_shader_chunk"])
        self.assertFalse(result["gpu_compatibility_verified"])
        self.assertFalse(result["shader_source_recovered"])
        self.assertFalse(result["code_emitted"])
        self.assertNotIn("DO_NOT_PRINT_PRIVATE_SHADER", str(result))
        self.assertEqual(inspect(dxbc(b"DXIL"))["container"], "DXIL")

    def test_spirv_entrypoint_stage_and_local_size_without_names(self):
        result = inspect(spirv())
        self.assertEqual(result["container"], "SPIR-V")
        self.assertEqual(result["version"], [1, 0])
        self.assertEqual(result["entrypoint_execution_models"], {5: 1})
        self.assertEqual(result["declared_local_workgroup_sizes"], [[8, 8, 1]])
        self.assertFalse(result["gpu_compatibility_verified"])
        self.assertNotIn("main", str(result))

    def test_malformed_dxbc_header_and_chunk_refused(self):
        data = bytearray(dxbc())
        struct.pack_into("<I", data, 24, len(data) - 1)
        with self.assertRaisesRegex(ValueError, "header"):
            inspect_dxbc(bytes(data))
        data = bytearray(dxbc())
        struct.pack_into("<I", data, 32, len(data) + 4)
        with self.assertRaisesRegex(ValueError, "offset"):
            inspect_dxbc(bytes(data))
        data = bytearray(dxbc())
        struct.pack_into("<I", data, 40, 0x7fffffff)
        with self.assertRaisesRegex(ValueError, "outside"):
            inspect_dxbc(bytes(data))

    def test_truncated_spirv_instruction_refused(self):
        data = bytearray(spirv())
        struct.pack_into("<I", data, 20, 0)
        with self.assertRaisesRegex(ValueError, "Truncated SPIR-V instruction"):
            inspect_spirv(bytes(data))
        data = bytearray(spirv())
        struct.pack_into("<I", data, 4, 0x00020000)
        with self.assertRaisesRegex(ValueError, "version"):
            inspect_spirv(bytes(data))
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            inspect(b"ABCDEF" * 6)


if __name__ == "__main__":
    unittest.main()
