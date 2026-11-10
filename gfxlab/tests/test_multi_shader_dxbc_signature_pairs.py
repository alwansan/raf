import struct
import unittest

from gfxlab.tools.multi_shader_dxbc_signature_pairs import (
    safe_signature_entries,signature_from_container,compare_stage_signatures,
)


def signature_payload(records):
    head=bytearray(8+24*len(records))
    struct.pack_into("<II",head,0,len(records),8)
    for i,(name,index,sysval,typ,reg,mask,rwmask) in enumerate(records):
        offset=8+24*i
        string_offset=len(head)
        struct.pack_into("<IIIII",head,offset,string_offset,index,sysval,typ,reg)
        struct.pack_into("<BB",head,offset+20,mask,rwmask)
        head.extend(name.encode("ascii")+b"\x00")
    return bytes(head)


def make_dxbc(kind,payload):
    parts=[(b"SHDR",b"some-original-stage")]
    parts.append((kind.encode("ascii"),payload))
    raw=bytearray(32+4*len(parts))
    raw[:4]=b"DXBC"
    struct.pack_into("<I",raw,28,len(parts))
    for n,(name,data) in enumerate(parts):
        at=len(raw)
        struct.pack_into("<I",raw,32+4*n,at)
        raw+=name+struct.pack("<I",len(data))+data
    struct.pack_into("<I",raw,24,len(raw))
    return bytes(raw)


class TestSourceDXBCSignaturePairs(unittest.TestCase):
    def test_base_signature_record_parse(self):
        items=[("TEXCOORD",0,0,3,1,15,7),("SV_POSITION",0,1,3,0,15,15)]
        decoded=safe_signature_entries(signature_payload(items))
        self.assertEqual(decoded,items)
        self.assertEqual(len(decoded),2)

    def test_parse_signature_from_actual_bounded_chunk_envelope(self):
        items=[("COLOR",1,0,3,2,15,15)]
        self.assertEqual(signature_from_container(make_dxbc("OSGN",signature_payload(items)),"OSGN"),items)
        with self.assertRaisesRegex(ValueError,"ABSENT_OR_AMBIGUOUS"):
            signature_from_container(make_dxbc("OSGN",signature_payload(items)),"ISGN")

    def test_clean_non_system_pair_and_pixel_system_input(self):
        outputs=[("TEXCOORD",0,0,3,0,15,15),("SV_POSITION",0,1,3,1,15,15)]
        inputs=[("TEXCOORD",0,0,3,7,7,7),("SV_POSITION",0,1,3,8,15,15)]
        result=compare_stage_signatures(outputs,inputs)
        self.assertTrue(result["non_system_fragment_inputs_compatible_by_signature_only"])
        self.assertEqual(result["fragment_non_system_compatible_by_signature"],1)
        self.assertEqual(result["fragment_system_inputs"],1)
        self.assertEqual(result["fragment_non_system_missing_output"],0)
        self.assertFalse(result["interpolation_mode_and_rasterizer_system_value_semantics_verified"])

    def test_missing_semantic_type_and_mask_issues_counted_separately(self):
        v=[("TEXCOORD",0,0,3,0,3,3),("COLOR",0,0,3,1,15,15)]
        f=[("MISSING",0,0,3,0,3,3),("COLOR",0,0,2,1,15,15),
           ("TEXCOORD",0,0,3,2,15,15)]
        d=compare_stage_signatures(v,f)
        self.assertEqual(d["fragment_non_system_missing_output"],1)
        self.assertEqual(d["fragment_non_system_component_type_mismatches"],1)
        self.assertEqual(d["fragment_non_system_component_mask_gaps"],1)
        self.assertFalse(d["non_system_fragment_inputs_compatible_by_signature_only"])
        self.assertFalse(d["material_to_original_register_cb_mapping_verified"])

    def test_vertex_duplicate_semantics_cannot_prove_unambiguous_link(self):
        v=[("TEXCOORD",0,0,3,0,15,15),("TEXCOORD",0,0,3,1,15,15)]
        f=[("TEXCOORD",0,0,3,0,15,15)]
        d=compare_stage_signatures(v,f)
        self.assertEqual(d["fragment_non_system_ambiguous_output"],1)
        self.assertFalse(d["non_system_fragment_inputs_compatible_by_signature_only"])

    def test_bad_count_or_offset_fails_closed(self):
        data=bytearray(signature_payload([("TEXCOORD",0,0,3,1,15,15)]))
        struct.pack_into("<I",data,0,3000)
        with self.assertRaisesRegex(ValueError,"OUT_OF_BOUNDS"):
            safe_signature_entries(bytes(data))
        data=bytearray(signature_payload([("TEXCOORD",0,0,3,1,15,15)]))
        struct.pack_into("<I",data,8,0)
        with self.assertRaisesRegex(ValueError,"OFFSET_INVALID"):
            safe_signature_entries(bytes(data))

    def test_unterminated_name_fails_closed_and_does_not_echo_private_name(self):
        data=signature_payload([("TOP_SECRET_SOURCE_SEMANTIC",0,0,3,1,15,15)])
        with self.assertRaisesRegex(ValueError,"UNTERMINATED"):
            safe_signature_entries(data[:-1])
        with self.assertRaises(ValueError) as ctx:
            safe_signature_entries(b"\x01\x02")
        self.assertNotIn("TOP_SECRET",str(ctx.exception))

    def test_masks_must_fit_four_components(self):
        data=bytearray(signature_payload([("TEXCOORD",0,0,3,1,15,15)]))
        data[8+20]=0x80
        with self.assertRaisesRegex(ValueError,"COMPONENT_MASK_INVALID"):
            safe_signature_entries(bytes(data))
