import unittest
from types import SimpleNamespace

from gfxlab.tools.multi_shader_gl_program_envelope import (
    inspect_candidates, bounded_envelope_flags, safe_keywords,
    length_bucket, ascii_bucket, version_bucket,
)
from gfxlab.tools.multi_shader_unreferenced_reflection import (
    EXPECTED_COMPILED, EXPECTED_REFERENCED,
)


def synthetic_table():
    arr=[
        SimpleNamespace(
            m_ProgramType=SimpleNamespace(name="kShaderGpuProgramDX11VertexSM50"),
            m_ProgramCode=b"PRIVATE_DX11_SHADER",
            m_Version=202012090,m_Keywords=["ORIGINAL_PRIVATE_FEATURE"])
        for _ in range(EXPECTED_COMPILED)
    ]
    for i in range(EXPECTED_REFERENCED,EXPECTED_REFERENCED+112):
        arr[i].m_ProgramCode=b""
    for i in range(EXPECTED_REFERENCED+112,EXPECTED_REFERENCED+112+139):
        arr[i].m_ProgramType.name="kShaderGpuProgramGLES3"
        arr[i].m_ProgramCode=b"\x11\x00_PRIVATE_GLES_CODE\x00"
        arr[i].m_Keywords=["ORIGINAL_PRIVATE_FEATURE"]
    for i in range(EXPECTED_REFERENCED+112+139,EXPECTED_REFERENCED+112+139+120):
        arr[i].m_ProgramType.name="kShaderGpuProgramGLCore43"
        arr[i].m_ProgramCode=b"\xff\xfeBINARY"
        arr[i].m_Keywords=["SOME_OTHER_SECRET_FEATURE"]
    return arr


class TestShader48GLBinaryEnvelope(unittest.TestCase):
    def test_public_shapebins_and_version_classes(self):
        self.assertEqual(length_bucket(1),"1_to_31")
        self.assertEqual(length_bucket(32),"32_to_127")
        self.assertEqual(length_bucket(128),"128_to_511")
        self.assertEqual(length_bucket(512),"512_to_4095")
        self.assertEqual(length_bucket(4096),"4096_to_65535")
        self.assertEqual(length_bucket(65536),"65536_and_more")
        with self.assertRaises(ValueError):length_bucket(0)
        self.assertEqual(version_bucket(202012090),"2021_2_or_newer")
        self.assertEqual(version_bucket(201806140),"2019_to_2021_1")
        self.assertEqual(version_bucket(201509030),"2015_to_2018")
        self.assertEqual(ascii_bucket(b"\x00"*5),"0_to_24_percent")
        self.assertEqual(ascii_bucket(b"ASCII"),"75_to_100_percent")

    def test_structural_length_headers_only_are_not_a_parser(self):
        data=(12).to_bytes(4,"little")+b"12345678"
        flags=bounded_envelope_flags(data)
        self.assertTrue(flags["u32le_first_word_equals_total_bytes"])
        self.assertFalse(flags["u32le_first_word_equals_trailing_bytes"])
        data=(4).to_bytes(4,"little")+b"ABCD"
        self.assertTrue(bounded_envelope_flags(data)["u32le_first_word_equals_trailing_bytes"])
        self.assertTrue(bounded_envelope_flags(b"\x04\x22\x4d\x18test")["known_leading_lz4_frame_magic"])
        self.assertTrue(bounded_envelope_flags(b"\x03\x02\x23\x07rest")["known_leading_spirv_magic"])
        self.assertTrue(bounded_envelope_flags(b"\x78\x9ccompressed")["known_leading_zlib_header"])
        with self.assertRaisesRegex(ValueError,"OUT_OF_BOUNDS"):
            bounded_envelope_flags(b"")

    def test_keyword_signature_is_private_and_never_in_report(self):
        p=SimpleNamespace(m_Keywords=["SECRET_B","SECRET_A"])
        self.assertEqual(safe_keywords(p),("SECRET_A","SECRET_B"))
        p.m_Keywords=["SECRET_B","SECRET_B"]
        with self.assertRaisesRegex(ValueError,"DUPLICATE_KEYWORDS"):
            safe_keywords(p)
        p.m_Keywords=[""]
        with self.assertRaisesRegex(ValueError,"KEYWORD_INVALID"):
            safe_keywords(p)

    def test_candidate_platform_consistency_and_private_keyword_matches(self):
        d=inspect_candidates(
            synthetic_table(),set(range(EXPECTED_REFERENCED)),
            "kShaderCompPlatformD3D11")
        self.assertEqual(d["GLES"]["candidate_entries"],139)
        self.assertEqual(d["GLCORE"]["candidate_entries"],120)
        self.assertEqual(d["GLES"]["nonempty_keyword_signature_matches_linked_dx11"],139)
        self.assertEqual(d["GLES"]["nonempty_keyword_signature_unique_linked_match"],0)
        self.assertEqual(d["GLES"]["platform_family_matches_original_compiler_platform"],0)
        self.assertEqual(d["GLCORE"]["platform_family_matches_original_compiler_platform"],0)
        self.assertEqual(d["GLES"]["distinct_private_code_payload_count"],1)
        self.assertEqual(d["GLCORE"]["distinct_private_code_payload_count"],1)
        self.assertEqual(d["GLES"]["source_code_byte_size_buckets"]["1_to_31"],139)
        self.assertFalse(d["GLES"]["keyword_match_proves_original_pass_or_material_binding"])
        self.assertNotIn("SECRET",str(d))
        self.assertNotIn("PRIVATE",str(d))

    def test_gles_platform_label_alone_still_does_not_prove_pass(self):
        d=inspect_candidates(
            synthetic_table(),set(range(EXPECTED_REFERENCED)),
            "kShaderCompPlatformGLES3Plus")
        self.assertEqual(d["GLES"]["platform_family_matches_original_compiler_platform"],139)
        self.assertEqual(d["GLCORE"]["platform_family_matches_original_compiler_platform"],0)
        self.assertFalse(d["GLES"]["keyword_match_proves_original_pass_or_material_binding"])

    def test_fail_closed_wrong_compiled_count_and_unbounded_gl_payload(self):
        with self.assertRaisesRegex(ValueError,"TABLE_DRIFT"):
            inspect_candidates([],set(),"kShaderCompPlatformD3D11")
        data=synthetic_table()
        data[-1].m_ProgramCode=b"X"*(16*1024*1024+1)
        with self.assertRaisesRegex(ValueError,"TOO_LARGE"):
            inspect_candidates(data,set(range(EXPECTED_REFERENCED)),
                               "kShaderCompPlatformD3D11")
