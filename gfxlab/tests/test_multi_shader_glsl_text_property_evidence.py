import unittest
from types import SimpleNamespace
from gfxlab.tools.multi_shader_glsl_text_property_evidence import (
    sanitize_comment_text, safe_property_token_hits,
    bounded_glsl_evidence, analyze_programs,
)
from gfxlab.tools.multi_shader_unreferenced_reflection import (
    EXPECTED_COMPILED, EXPECTED_REFERENCED,
)

PROPS={"_MainTex","_BumpMap","_MetallicGlossMap","_Glossiness"}
TEX={"_MainTex","_BumpMap","_MetallicGlossMap"}
BOUND=TEX

class TestSourceGlslTextEvidence(unittest.TestCase):
    def test_exact_boundary_and_strip_comments(self):
        src="// uniform sampler2D _MainTex;\n/* uniform sampler2D _BumpMap; */\nuniform sampler2D _MainTexture;"
        clean=sanitize_comment_text(src)
        self.assertEqual(safe_property_token_hits(clean,{"_MainTex","_BumpMap"}),set())
        with self.assertRaises(ValueError):
            safe_property_token_hits("uniform bad-name;",{"bad-name"})

    def test_real_utf8_shader_and_uniform_token_overlap(self):
        raw=b"// _BumpMap unused\n#version 300 es\nuniform sampler2D _MainTex;\nvoid main() {}"
        d=bounded_glsl_evidence(raw,PROPS,TEX,BOUND)
        self.assertTrue(d["strict_utf8"])
        self.assertTrue(d["glsl_version_directive"])
        self.assertTrue(d["main_function"])
        self.assertTrue(d["uniform_statement_present"])
        self.assertTrue(d["sampler_declaration_present"])
        self.assertEqual(d["authored_property_token_matches"],{"_MainTex"})
        self.assertEqual(d["bound_material_uniform_matches"],{"_MainTex"})
        self.assertNotIn("_BumpMap",d["bound_material_property_token_matches"])

    def test_non_utf8_source_stays_unknown(self):
        d=bounded_glsl_evidence(b"\xff\xfe\x00",PROPS,TEX,BOUND)
        self.assertFalse(d["strict_utf8"])
        self.assertTrue(d["embedded_null_byte"])
        self.assertFalse(d["glsl_version_directive"])
        self.assertEqual(d["authored_property_token_matches"],set())

    def test_strict_length_and_metadata_guards(self):
        with self.assertRaisesRegex(ValueError,"TOO_LARGE"):
            bounded_glsl_evidence(b"x"*(16*1024*1024+1),PROPS,TEX,BOUND)
        with self.assertRaisesRegex(ValueError,"PROPERTY_SET_MISMATCH"):
            analyze_programs([None]*EXPECTED_COMPILED,set(range(EXPECTED_REFERENCED)),PROPS,{"_Other"},BOUND)

    def test_aggregates_do_not_disclose_names_or_bytes(self):
        p=[
            SimpleNamespace(m_ProgramType=SimpleNamespace(name="DX11VertexSM50"),
                            m_ProgramCode=b"original-compiled-binary")
            for _ in range(EXPECTED_COMPILED)
        ]
        start=EXPECTED_REFERENCED
        for i in range(start,start+112):
            p[i].m_ProgramCode=b""
        for i in range(start+112,start+112+139):
            p[i].m_ProgramType.name="kShaderGpuProgramGLES3"
            p[i].m_ProgramCode=b"uniform sampler2D _MainTex; void main() {}"
        for i in range(start+112+139,start+112+139+120):
            p[i].m_ProgramType.name="kShaderGpuProgramGLCore43"
            p[i].m_ProgramCode=b"\xff\xfe"
        for i in range(start+112+139+120,EXPECTED_COMPILED):
            p[i].m_ProgramType.name="DX9Pixel"
            p[i].m_ProgramCode=b"binary"
        d=analyze_programs(p,set(range(EXPECTED_REFERENCED)),PROPS,TEX,BOUND)
        self.assertEqual(d["GLES"]["candidate_entries"],139)
        self.assertEqual(d["GLES"]["strict_utf8_decoded"],139)
        self.assertEqual(d["GLES"]["unique_bound_material_uniform_property_tokens"],1) if (
            "unique_bound_material_uniform_property_tokens" in d["GLES"]) else self.assertEqual(
                d["GLES"]["unique_bound_material_uniform_tokens"],1)
        self.assertEqual(d["GLCORE"]["invalid_utf8_or_binary"],120)
        self.assertNotIn("_MainTex",str(d))
        self.assertNotIn("original-compiled-binary",str(d))
