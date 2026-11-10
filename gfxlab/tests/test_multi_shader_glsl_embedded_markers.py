import unittest
from types import SimpleNamespace
from gfxlab.tools.multi_shader_glsl_embedded_markers import (
    scan_binary, boundary_mentions, inspect, marker_offset_bin,
)
from gfxlab.tools.multi_shader_unreferenced_reflection import (
    EXPECTED_COMPILED, EXPECTED_REFERENCED,
)

PROPS={"_MainTex","_BumpMap","_MetallicGlossMap","_Glossiness"}
TEX={"_MainTex","_BumpMap","_MetallicGlossMap"}
BOUND=TEX

class TestOriginalEmbeddedGlMarkers(unittest.TestCase):
    def test_token_boundary_avoids_longer_identifiers(self):
        raw=b"_MainTexture _BumpMap _Glossiness"
        self.assertEqual(boundary_mentions(raw,PROPS),{"_BumpMap","_Glossiness"})
        with self.assertRaises(ValueError):
            boundary_mentions(raw,{"illegal-key"})

    def test_detect_wrapped_glsl_ascii_without_publishing_bytes(self):
        raw=b"\xff\x00BINARYPREFIX" + b"X"*123 + (
            b"\x00#version 310 es\nuniform sampler2D _MainTex;\n"
            b"void main() { }\x00")
        d=scan_binary(raw,PROPS,TEX,BOUND)
        self.assertTrue(d["embedded_nul"])
        self.assertTrue(d["glsl_version_marker_anywhere"])
        self.assertTrue(d["main_function_marker_anywhere"])
        self.assertTrue(d["uniform_token_anywhere"])
        self.assertTrue(d["sampler_token_anywhere"])
        self.assertEqual(d["glsl_version_offset_bin"],"first_4096_bytes")
        self.assertEqual(d["original_bound_property_tokens"],{"_MainTex"})
        self.assertEqual(d["uniform_line_bound_property_tokens"],{"_MainTex"})
        self.assertFalse(d["printable_ascii_window_4096_or_more"])

    def test_wrapped_source_marker_not_a_proof_of_uniform_binding(self):
        raw=b"\xff\x01raw binary _MainTex in unrelated literal"
        d=scan_binary(raw,PROPS,TEX,BOUND)
        self.assertEqual(d["original_bound_property_tokens"],{"_MainTex"})
        self.assertFalse(d["uniform_token_anywhere"])
        self.assertEqual(d["uniform_line_bound_property_tokens"],set())

    def test_no_glsl_markers_is_unknown_not_invalid_shader(self):
        d=scan_binary(b"opaque-binary-without-shader-strings",PROPS,TEX,BOUND)
        self.assertFalse(d["main_function_marker_anywhere"])
        self.assertFalse(d["glsl_version_marker_anywhere"])
        self.assertEqual(d["glsl_version_offset_bin"],"absent")

    def test_original_program_count_and_empty_exclusion(self):
        p=[
            SimpleNamespace(m_ProgramType=SimpleNamespace(name="kShaderGpuProgramDX11VertexSM50"),
                            m_ProgramCode=b"private")
            for _ in range(EXPECTED_COMPILED)
        ]
        for i in range(EXPECTED_REFERENCED,EXPECTED_REFERENCED+112):
            p[i].m_ProgramCode=b""
        for i in range(EXPECTED_REFERENCED+112,EXPECTED_REFERENCED+112+139):
            p[i].m_ProgramType.name="kShaderGpuProgramGLES3"
            p[i].m_ProgramCode=b"\x00uniform sampler2D _MainTex;"
        for i in range(EXPECTED_REFERENCED+112+139,EXPECTED_REFERENCED+112+139+120):
            p[i].m_ProgramType.name="kShaderGpuProgramGLCore43"
            p[i].m_ProgramCode=b"other"
        d=inspect(p,set(range(EXPECTED_REFERENCED)),PROPS,TEX,BOUND)
        self.assertEqual(d["GLES"]["source_programs"],139)
        self.assertEqual(d["GLCORE"]["source_programs"],120)
        self.assertEqual(d["GLES"]["programs_with_bound_uniform_line_tokens"],139)
        self.assertEqual(d["GLES"]["unique_original_bound_property_tokens"],1)
        self.assertNotIn("_MainTex",str(d))
        self.assertNotIn("private",str(d))

    def test_invalid_source_byte_shape_rejected(self):
        with self.assertRaisesRegex(ValueError,"BINARY_SIZE_INVALID"):
            scan_binary(b"",PROPS,TEX,BOUND)
        with self.assertRaisesRegex(ValueError,"COMPILED_LINK_SHAPE_DRIFT"):
            inspect([],set(),PROPS,TEX,BOUND)
