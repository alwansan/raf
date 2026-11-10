import unittest
from enum import IntEnum
from types import SimpleNamespace

from gfxlab.tools.multi_shader_unused_program_families import (
    program_family, stage_family, recognizable_prefix,
    inspect_unused_platforms, alt_pass_program_links,
)
from gfxlab.tools.multi_shader_unreferenced_reflection import (
    EXPECTED_COMPILED, EXPECTED_REFERENCED,
)

class ProgramType(IntEnum):
    DX9Pixel=1
    GLES3Vertex=2
    VulkanFragment=3
    D3D11Vertex=4

def programs():
    x=[SimpleNamespace(m_ProgramType=ProgramType.DX9Pixel,
                       m_ProgramCode=b"opaque-format")
       for _ in range(EXPECTED_COMPILED)]
    for i in range(EXPECTED_REFERENCED,EXPECTED_REFERENCED+112):
        x[i].m_ProgramCode=b""
    return x

class TestShader48UnusedProgramPlatforms(unittest.TestCase):
    def test_generic_public_type_categories_not_source_names(self):
        self.assertEqual(program_family("GLES3Vertex"),"GLES")
        self.assertEqual(program_family("GLCorePixel"),"GLCORE")
        self.assertEqual(program_family("VulkanFragment"),"VULKAN")
        self.assertEqual(program_family("D3D11Vertex"),"D3D11")
        self.assertEqual(program_family("DX9Pixel"),"D3D9")
        self.assertEqual(program_family("MetalVertex"),"METAL")
        self.assertEqual(program_family("PS4Geometry"),"CONSOLE")
        self.assertEqual(program_family("unfamiliar"),"OTHER")
        self.assertEqual(stage_family("GLES3Vertex"),"VERTEX")
        self.assertEqual(stage_family("DX9Pixel"),"FRAGMENT")
        self.assertEqual(stage_family("VulkanCompute"),"COMPUTE")
        with self.assertRaises(ValueError):program_family("")

    def test_only_exact_leading_payload_headers_recognized(self):
        self.assertEqual(recognizable_prefix(bytes([3,2,35,7,0,0,0,0])),
                         "SPIRV_LEADING_MAGIC")
        self.assertEqual(recognizable_prefix(b"\xef\xbb\xbf  #version 310 es\n"),
                         "GLSL_LEADING_VERSION")
        self.assertEqual(recognizable_prefix(b"prefix #version 310 es"),"UNKNOWN_OR_WRAPPED")
        self.assertEqual(recognizable_prefix(b"DXBC"+b"0"*34),
                         "DXBC_LEADING_MAGIC_UNVALIDATED")
        self.assertEqual(recognizable_prefix(b"DXBC"),"UNKNOWN_OR_WRAPPED")

    def test_counts_unreferenced_excluding_empty_entries(self):
        d=inspect_unused_platforms(programs(),set(range(EXPECTED_REFERENCED)))
        self.assertEqual(d["unused_total"],381)
        self.assertEqual(d["unused_empty_code"],112)
        self.assertEqual(d["unused_non_d3d11_code"],269)
        self.assertEqual(d["nonempty_platform_type_families"]["D3D9"],269)
        self.assertEqual(d["nonempty_strict_leading_payload_signatures"]["UNKNOWN_OR_WRAPPED"],269)
        self.assertFalse(d["type_or_header_proves_original_android_pass_link"])
        self.assertNotIn("opaque-format",str(d))

    def test_detect_candidates_without_proving_original_material_link(self):
        p=programs()
        p[-1].m_ProgramType=ProgramType.VulkanFragment
        p[-1].m_ProgramCode=bytes([3,2,35,7,0,0,0,0])
        p[-2].m_ProgramType=ProgramType.GLES3Vertex
        p[-2].m_ProgramCode=b"#version 310 es"
        d=inspect_unused_platforms(p,set(range(EXPECTED_REFERENCED)))
        self.assertEqual(d["type_label_gles_or_vulkan_candidate_count"],2)
        self.assertEqual(d["strict_leading_glsl_or_spirv_magic_count"],2)
        self.assertFalse(d["type_or_header_proves_original_android_pass_link"])

    def test_source_alternate_program_field_requires_exact_type_match(self):
        p=programs()
        p[-1].m_ProgramType=ProgramType.GLES3Vertex
        sub=[{"m_Passes":[{} for _ in range(4)]},
             {"m_Passes":[{} for _ in range(3)]}]
        sub[0]["m_Passes"][0]["progGeometry"]={
            "m_SubPrograms":[{
                "m_BlobIndex":EXPECTED_COMPILED-1,
                "m_GpuProgramType":int(ProgramType.GLES3Vertex)
            }]
        }
        d=alt_pass_program_links(sub,p,set(range(EXPECTED_REFERENCED)))
        self.assertEqual(d["other_original_pass_program_field_rows"],1)
        self.assertEqual(d["other_original_pass_stage_variant_rows"],1)
        self.assertEqual(d["other_original_pass_unique_previously_unused_indices"],1)
        sub[0]["m_Passes"][0]["progGeometry"]["m_SubPrograms"][0]["m_GpuProgramType"]=999
        with self.assertRaisesRegex(ValueError,"TYPE_MISMATCH"):
            alt_pass_program_links(sub,p,set(range(EXPECTED_REFERENCED)))

    def test_unexpected_unused_d3d11_rejected(self):
        p=programs()
        p[-1].m_ProgramType=ProgramType.D3D11Vertex
        with self.assertRaisesRegex(ValueError,"UNEXPECTED_UNREFERENCED"):
            inspect_unused_platforms(p,set(range(EXPECTED_REFERENCED)))

    def test_wrong_count_and_unbounded_private_code_rejected(self):
        with self.assertRaisesRegex(ValueError,"LINKED_INDEX_SET_CHANGED"):
            inspect_unused_platforms(programs(),{0})
        p=programs()
        p[-1].m_ProgramCode=b"X"*(16*1024*1024+1)
        with self.assertRaisesRegex(ValueError,"UNBOUNDED"):
            inspect_unused_platforms(p,set(range(EXPECTED_REFERENCED)))
