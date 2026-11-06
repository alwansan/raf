"""T3 synthetic-only strict source-native D3D11 DXBC RDEF resource parsers."""
import json
import struct
import unittest

from scripts.t3_particle108_original_dxbc_rdef import (
    source_rdef,_private_register_layout,classify_four_pairs,STATUS,SAFE_RDEF_FAILURE_REASON,
)


def synthetic_dxbc(bindings=()):
    """Owned synthetic one-RDEF-chunk test DXBC, not a proprietary shader."""
    table=bytearray(28)
    struct.pack_into("<IIII",table,0,0,0,len(bindings),28)
    strings=bytearray()
    for name,kind,register,count in bindings:
        offset=28+32*len(bindings)+len(strings)
        strings+=name.encode("ascii")+b"\x00"
        table+=struct.pack("<8I",offset,kind,0,0,0,register,count,0)
    table+=strings
    chunk=b"RDEF"+struct.pack("<I",len(table))+table
    offset=36
    size=offset+len(chunk)
    return b"DXBC"+b"\x00"*16+struct.pack("<III",1,size,1)+struct.pack("<I",offset)+chunk


def fixtures():
    v=synthetic_dxbc([("_PRIVATE_CB",0,0,1)])
    f=synthetic_dxbc([("_PRIVATE_TEXTURE",2,2,1),("_PRIVATE_SAMPLER",3,1,1)])
    return [(v,f) for _ in range(4)]


class OriginalRdefTests(unittest.TestCase):
    def test_parses_private_dxbc_cb_textures_sampler(self):
        source=synthetic_dxbc([("_PrivateCB",0,0,1),
                               ("_PrivateT",2,5,1),("_PrivateS",3,4,1)])
        self.assertEqual(source_rdef(source),((0,0,1),(2,5,1),(3,4,1)))
        self.assertNotIn("_PrivateCB",str(source_rdef(source)))
    def test_four_pairs_eight_stages_and_stable_source_original_register_layout(self):
        report=classify_four_pairs(fixtures())
        self.assertEqual(report["status"],STATUS)
        self.assertEqual(report["counts"]["original_DXBC_stages_parsed"],8)
        self.assertEqual(report["counts"]["original_RDEF_resource_rows"],12)
        self.assertEqual(report["counts"]["source_original_vertex_fragment_keyword_pairs_parsed"],4)
        self.assertEqual(report["counts"]["vertex_RDEF_register_layout_stable_all_four"],1)
        self.assertEqual(report["counts"]["fragment_RDEF_register_layout_stable_all_four"],1)
        self.assertEqual(report["counts"]["RDEF_original_full_pair_register_layouts_distinct"],1)
        self.assertEqual(report["counts"]["cbuffer_resource_rows"],4)
        self.assertEqual(report["counts"]["sampler_resource_rows"],4)
        self.assertEqual(report["counts"]["srv_resource_rows"],4)
        self.assertFalse(report["SPIRV_descriptor_set_mapping_proven"])
        self.assertNotIn("_PRIVATE",json.dumps(report))
    def test_real_source_keyword_variant_original_register_discrepancy_detected(self):
        pairs=fixtures()
        pairs[3]=(pairs[3][0],synthetic_dxbc([("_PrivateTexture",2,7,1),
                                            ("_PrivateS",3,1,1)]))
        count=classify_four_pairs(pairs)["counts"]
        self.assertEqual(count["vertex_RDEF_register_layouts_distinct_across_four_keywords"],1)
        self.assertEqual(count["fragment_RDEF_register_layouts_distinct_across_four_keywords"],2)
        self.assertEqual(count["RDEF_original_full_pair_register_layouts_distinct"],2)
    def test_missing_original_RDEF_is_rejected(self):
        source=bytearray(synthetic_dxbc([]))
        source[36:40]=b"ISGN"
        with self.assertRaisesRegex(ValueError,"DXBC_ORIGINAL_RDEF_ABSENT"):
            source_rdef(bytes(source))
    def test_multiple_original_RDEF_chunks_are_distinguished_from_absence(self):
        source=bytearray(synthetic_dxbc([]))
        # Duplicate the synthetic RDEF chunk and rebuild the DXBC chunk-offset table.
        first=bytes(source[36:])
        second_offset=40+len(first)
        duplicate=(b"DXBC"+b"\x00"*16+
                   struct.pack("<III",1,second_offset+len(first),2)+
                   struct.pack("<II",40,second_offset)+first+first)
        with self.assertRaisesRegex(ValueError,"DXBC_ORIGINAL_RDEF_MULTIPLE"):
            source_rdef(duplicate)

    def test_original_DXBC_total_length_mismatch_rejected(self):
        source=bytearray(synthetic_dxbc([]))
        struct.pack_into("<I",source,24,len(source)+1)
        with self.assertRaisesRegex(ValueError,"DXBC_SOURCE_CONTAINER_LENGTH_OR_MAGIC"):
            source_rdef(bytes(source))
    def test_source_RDEF_truncated_chunk_rejected(self):
        source=bytearray(synthetic_dxbc([]))
        struct.pack_into("<I",source,40,2**32-1)
        with self.assertRaises(ValueError):
            source_rdef(bytes(source))
    def test_overlarge_or_zero_original_binding_count_rejected(self):
        for bad in (0,129):
            source=synthetic_dxbc([("_PrivateResource",2,3,bad)])
            with self.subTest(bad=bad),self.assertRaisesRegex(ValueError,"DESCRIPTOR_INVALID"):
                source_rdef(source)
    def test_original_resource_name_offset_outside_binary_rejected(self):
        source=bytearray(synthetic_dxbc([("_PrivateTexture",2,0,1)]))
        # DXBC chunk header at 36, RDEF data begins at 44, row begins at 72.
        struct.pack_into("<I",source,72,2**32-1)
        with self.assertRaisesRegex(ValueError,"DESCRIPTOR_INVALID"):
            source_rdef(bytes(source))
    def test_untrusted_D3D_resource_kind_rejected(self):
        source=synthetic_dxbc([("_PrivateUnknown",99,0,1)])
        with self.assertRaisesRegex(ValueError,"DESCRIPTOR_INVALID"):
            source_rdef(source)
    def test_same_family_register_overlap_is_measured_not_silently_dropped(self):
        layout,count=_private_register_layout(((2,0,2),(5,1,2),(3,0,1)))
        self.assertEqual(count["same_family_overlapping_register_slots"],1)
        self.assertEqual(count["srv_register_slots"],4)
        self.assertEqual(count["sampler_register_slots"],1)
        self.assertNotIn("_Private",str(layout))
    def test_register_namespace_separation_sampler_srv_cb_is_preserved(self):
        _,count=_private_register_layout(((0,0,1),(2,0,1),(3,0,1)))
        self.assertEqual(count["same_family_overlapping_register_slots"],0)
    def test_rdef_fail_reason_is_only_safe_static_classifier(self):
        self.assertEqual(SAFE_RDEF_FAILURE_REASON["DXBC_ORIGINAL_RDEF_ABSENT"],
                         "ORIGINAL_RDEF_ABSENT")
        self.assertEqual(SAFE_RDEF_FAILURE_REASON["DXBC_ORIGINAL_RDEF_MULTIPLE"],
                         "ORIGINAL_RDEF_MULTIPLE")
        self.assertNotIn("_PrivateTexture",json.dumps(SAFE_RDEF_FAILURE_REASON))
    def test_missing_four_original_pairs_rejected(self):
        for bad in ([],fixtures()[:3],fixtures()+fixtures()[:1]):
            with self.assertRaisesRegex(ValueError,"ORIGINAL_FOUR_DXBC_PAIRS_REQUIRED"):
                classify_four_pairs(bad)


if __name__=="__main__":
    unittest.main()
