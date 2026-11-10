import struct
import unittest
from gfxlab.tools.multi_shader_linked_dxbc_debug_chunks import (
    safe_container_chunks,inspect_one_dxbc,authentic_source_property_tokens,
)

PROPERTIES={"_MainTex","_BumpMap","_Glossiness"}

def make_dxbc(chunks):
    n=len(chunks)
    data=bytearray(32+4*n)
    data[:4]=b"DXBC"
    struct.pack_into("<I",data,20,1)
    struct.pack_into("<I",data,28,n)
    for i,(tag,payload) in enumerate(chunks):
        off=len(data)
        struct.pack_into("<I",data,32+i*4,off)
        data+=tag
        data+=struct.pack("<I",len(payload))
        data+=payload
    struct.pack_into("<I",data,24,len(data))
    return bytes(data)

class TestAuthenticLinkedShader48DXBCChunks(unittest.TestCase):
    def test_complete_public_chunk_categories(self):
        blob=make_dxbc([(b"ISGN",b"sig"),
                        (b"SHDR",b"\x00\x01\x02\x03"),
                        (b"STAT",b"tiny")])
        chunks=safe_container_chunks(blob)
        self.assertEqual([x[0] for x in chunks],["ISGN","SHDR","STAT"])
        result=inspect_one_dxbc(blob,PROPERTIES)
        self.assertFalse(result["rdef_chunk_present"])
        self.assertFalse(result["alternative_reflection_or_debug_chunk_present"])
        self.assertFalse(result["material_property_register_offset_proven"])

    def test_alt_debug_has_exact_private_property_token_only(self):
        blob=make_dxbc([
            (b"SHDR",b"CODE"),
            (b"SDBG",b"private _MainTex; _MainTexture not a property\0")])
        result=inspect_one_dxbc(blob,PROPERTIES)
        self.assertTrue(result["alternative_reflection_or_debug_chunk_present"])
        self.assertTrue(result["original_property_name_in_alternative_chunk_present"])
        self.assertEqual(result["distinct_original_property_name_hits_in_debug_chunks"],1)
        self.assertFalse(result["material_property_register_offset_proven"])
        self.assertNotIn("_MainTex",str(result))

    def test_rdef_structural_presence_never_claims_binding(self):
        blob=make_dxbc([
            (b"SHEX",b"CODE"),
            (b"RDEF",struct.pack("<4I",0,0,0,0))])
        result=inspect_one_dxbc(blob,PROPERTIES)
        self.assertTrue(result["rdef_chunk_present"])
        self.assertFalse(result["material_property_register_offset_proven"])

    def test_unknown_chunk_names_are_not_exported(self):
        blob=make_dxbc([(b"SHDR",b"CODE"),(b"ABCD",b"private unknown")])
        result=inspect_one_dxbc(blob,PROPERTIES)
        self.assertEqual(result["tag_counts"]["OTHER_PUBLIC_TAG_UNRECOGNIZED"],1)
        self.assertNotIn("ABCD",str(result))
        self.assertNotIn("private unknown",str(result))

    def test_reject_overlapping_or_truncated_source_chunks(self):
        blob=bytearray(make_dxbc([(b"SHDR",b"CODE"),(b"STAT",b"DATA")]))
        first=struct.unpack_from("<I",blob,32)[0]
        struct.pack_into("<I",blob,36,first)
        with self.assertRaisesRegex(ValueError,"OVERLAP"):
            safe_container_chunks(bytes(blob))
        blob=bytearray(make_dxbc([(b"SHDR",b"CODE")]))
        off=struct.unpack_from("<I",blob,32)[0]
        struct.pack_into("<I",blob,off+4,10000)
        with self.assertRaisesRegex(ValueError,"TRUNCATED"):
            safe_container_chunks(bytes(blob))

    def test_reject_source_without_stage_or_malformed_magic(self):
        with self.assertRaisesRegex(ValueError,"STAGE_CODE_MISSING"):
            safe_container_chunks(make_dxbc([(b"SDBG",b"stuff")]))
        broken=bytearray(make_dxbc([(b"SHDR",b"CODE")]))
        broken[:4]=b"BAD!"
        with self.assertRaisesRegex(ValueError,"MAGIC_INVALID"):
            safe_container_chunks(bytes(broken))

    def test_private_token_boundary_and_reject_invalid_source_name(self):
        a=authentic_source_property_tokens(b"_MainTexture _Glossiness _MainTex",PROPERTIES)
        self.assertEqual(a,{"_Glossiness","_MainTex"})
        with self.assertRaisesRegex(ValueError,"NAME_UNEXPECTED"):
            authentic_source_property_tokens(b"data",{"unsafe/name"})
