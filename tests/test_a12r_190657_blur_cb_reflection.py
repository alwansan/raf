"""Synthetic fixture tests for private DXBC RDEF CB provenance."""
import json
import struct
import unittest
from scripts.a12r_190657_blur_cb_reflection import rdef, serialized_groups, compare, public_common_counts

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
