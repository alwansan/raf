"""Synthetic fixture tests for private DXBC RDEF CB provenance."""
import json
import struct
import unittest
from scripts.a12r_190657_blur_cb_reflection import rdef, serialized_groups, compare, public_common_counts, crosscheck_unity_cb

def u(x):
    return struct.pack("<I", x)

def label(s):
    raw = s.encode()
    return u(len(raw)) + raw + b"\0" * ((-len(raw)) % 4)

def params(size=544, key="FakeCB"):
    return (u(202012090) + u(2) + label("Global") + u(0) + u(0) + u(0)
            + label(key) + u(size) + u(0) + u(0) + u(0))

def compiled(size=544, key="FakeCB", bound=True):
    text = key.encode() + b"\0"
    at = 52 + (32 if bound else 0)
    definition = struct.pack("<6I", at, 0, 0, size, 0, 0)
    binding = struct.pack("<8I", at, 0, 0, 0, 0, 2, 1, 0) if bound else b""
    body = struct.pack("<7I", 1, 28, int(bound), 52, 0, 0, 0) + definition + binding + text
    chunk = b"RDEF" + u(len(body)) + body
    return b"DXBC" + b"\0" * 16 + u(1) + u(36 + len(chunk)) + u(1) + u(36) + chunk

class A12RTests(unittest.TestCase):
    def test_unity_and_original_dxbc_declaration_sizes_match(self):
        src = {"m_ConstantBuffers": [
            {"m_NameIndex": 3, "m_Size": 176},
            {"m_NameIndex": 4, "m_Size": 368},
        ], "m_ConstantBufferBindings": [
            {"m_NameIndex": 3, "m_Index": 0},
            {"m_NameIndex": 4, "m_Index": 1},
        ]}
        got = crosscheck_unity_cb([("SyntheticOne", 3), ("SyntheticTwo", 4)],
                                 src, {"SyntheticOne": 176, "SyntheticTwo": 368},
                                 dxbc_declarations={0: 176, 1: 368})
        self.assertTrue(got["dxbc_dcl_original_slot_size_verified"])
        self.assertFalse(got["dxbc_register_or_shaderlab_runtime_verified"])

    def test_unity_dxbc_declarations_mismatched_slot_or_size_fail_closed(self):
        src = {"m_ConstantBuffers": [{"m_NameIndex": 3, "m_Size": 176}],
               "m_ConstantBufferBindings": [{"m_NameIndex": 3, "m_Index": 2}]}
        for bad, expected in (({1: 176}, "registers_mismatch"), ({2: 160}, "sizes_mismatch")):
            with self.subTest(bad=bad), self.assertRaisesRegex(ValueError, expected):
                crosscheck_unity_cb([("Synthetic", 3)], src, {"Synthetic": 176},
                                    dxbc_declarations=bad)

    def test_unity_constant_buffer_names_sizes_and_registers_match_privately(self):
        key0, key1 = "FakeUnityCb0", "FakeUnityCb1"
        common = {
            "m_ConstantBuffers": [
                {"m_NameIndex": 7, "m_Size": 176, "m_MatrixParams": [{"private": "never-log"}]},
                {"m_NameIndex": 9, "m_Size": 368, "m_VectorParams": [{"private": "never-log"}]},
            ],
            "m_ConstantBufferBindings": [
                {"m_NameIndex": 7, "m_Index": 0},
                {"m_NameIndex": 9, "m_Index": 1},
            ],
        }
        result = crosscheck_unity_cb([(key0, 7), (key1, 9)], common,
                                     {key0: 176, key1: 368})
        self.assertTrue(result["unity_serialized_cb_identity_source_verified"])
        self.assertEqual(result["unity_serialized_cb_name_size_slot_matches"], 2)
        self.assertFalse(result["dxbc_register_or_shaderlab_runtime_verified"])
        self.assertFalse(result["dxbc_dcl_original_slot_size_verified"])
        for private in (key0, key1, "never-log"):
            self.assertNotIn(private, json.dumps(result))

    def test_unity_constant_buffer_size_and_name_drift_refused(self):
        common = {"m_ConstantBuffers": [{"m_NameIndex": 3, "m_Size": 176}],
                  "m_ConstantBufferBindings": [{"m_NameIndex": 3, "m_Index": 0}]}
        with self.assertRaisesRegex(ValueError, "sizes_mismatch"):
            crosscheck_unity_cb([("Fake", 3)], common, {"Fake": 368})
        with self.assertRaisesRegex(ValueError, "names_mismatch"):
            crosscheck_unity_cb([("Fake", 3)], common, {"Other": 176})

    def test_unity_cb_duplicate_register_rejected(self):
        common = {
            "m_ConstantBuffers": [{"m_NameIndex": 3, "m_Size": 176},
                                  {"m_NameIndex": 4, "m_Size": 368}],
            "m_ConstantBufferBindings": [{"m_NameIndex": 3, "m_Index": 0},
                                          {"m_NameIndex": 4, "m_Index": 0}],
        }
        with self.assertRaisesRegex(ValueError, "ambiguous_binding"):
            crosscheck_unity_cb([("First", 3), ("Second", 4)], common,
                                {"First": 176, "Second": 368})

    def test_known_unity_common_parameter_array_counts_never_leak_values(self):
        source = {"m_CommonParameters": {
            "m_ConstantBuffers": [{"private_shader_identifier": "do-not-publish"}],
            "m_TextureParams": [{"private_texture_identifier": "do-not-publish"}],
        }}
        result = public_common_counts(source)
        self.assertEqual(result["m_ConstantBuffers"], 1)
        self.assertEqual(result["m_TextureParams"], 1)
        self.assertNotIn("do-not-publish", json.dumps(result))

    def test_unknown_unity_common_shape_fails_closed(self):
        with self.assertRaises(ValueError):
            public_common_counts({"m_CommonParameters": {"m_ConstantBuffers": "bad"}})

    def test_exact_structure_only_not_game_ready(self):
        result = compare(serialized_groups(params()), rdef(compiled()))
        self.assertEqual(result["serialized_cb_used_bytes"], 544)
        self.assertEqual(result["name_size_and_slot_matches"], 1)
        self.assertFalse(result["shaderlab_runtime_or_gpu_verified"])
        self.assertNotIn("FakeCB", json.dumps(result))
    def test_size_mismatch_refused(self):
        result = compare(serialized_groups(params(512)), rdef(compiled()))
        self.assertEqual(result["name_matches"], 1)
        self.assertEqual(result["name_and_size_matches"], 0)
    def test_bound_required(self):
        result = compare(serialized_groups(params()), rdef(compiled(bound=False)))
        self.assertEqual(result["name_size_and_slot_matches"], 0)
    def test_name_mismatch_refused(self):
        result = compare(serialized_groups(params(key="Another")), rdef(compiled()))
        self.assertEqual(result["name_matches"], 0)
    def test_truncation_refused(self):
        code = compiled()
        for value in (b"", b"DXBC", code[:35], code[:-1]):
            with self.subTest(length=len(value)), self.assertRaises(ValueError):
                rdef(value)
    def test_trailing_params_refused(self):
        with self.assertRaises(ValueError):
            serialized_groups(params() + u(0))
    def test_wrong_schema_refused(self):
        raw = params()
        with self.assertRaises(ValueError):
            serialized_groups(u(0) + raw[4:])

if __name__ == "__main__":
    unittest.main()
