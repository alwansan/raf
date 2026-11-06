"""Strict source-free DXBC DCL_CONSTANT_BUFFER SM4/5 size/slot regression."""
import struct,unittest
from scripts.t3_particle108_cb_size_semantics import (
  private_cb_declarations,classify_four_pairs,STATUS)

def cb(slot,size_vectors,access=0,dimensions=2,typ=8):
    operand=(typ<<12)|(dimensions<<20)
    indexes=[slot,size_vectors] if dimensions==2 else [slot]
    return [89|(int(access)<<11)|((2+len(indexes))<<24),operand,*indexes]

def dx(stage=1,major=5,minor=0,decls=None):
    if decls is None:decls=cb(1,24)+cb(2,0)
    words=[(stage<<16)|(major<<4)|minor,2+len(decls),*decls]
    raw=struct.pack("<"+"I"*len(words),*words)
    chunk=b"SHDR"+struct.pack("<I",len(raw))+raw
    return b"DXBC"+bytes(16)+struct.pack("<III",1,36+len(chunk),1)+struct.pack("<I",36)+chunk

def pairs():
    return [(dx(1),dx(0)) for _ in range(4)]

class CBufferSizeTests(unittest.TestCase):
    def test_sm5_cb_second_index_is_vector_count_not_register(self):
        version,records=private_cb_declarations(dx(),1)
        self.assertEqual(version,(5,0))
        self.assertEqual(records,((1,24,0),(2,0,0)))

    def test_zero_size_means_unknown(self):
        report=classify_four_pairs(pairs())
        c=report["counts"]
        self.assertEqual(c["original_CB_16byte_vector_size_declarations"],16)
        self.assertEqual(c["original_CB_zero_unknown_size_declarations"],8)
        self.assertEqual(c["original_CB_nonzero_known_size_declarations"],8)
        self.assertTrue(report["CB_zero_size_means_UNKNOWN"])
        self.assertEqual(report["CB_second_index_semantics"],"16_BYTE_VECTOR_COUNT")
        self.assertFalse(report["private_CB_register_ids_and_sizes_published"])

    def test_changing_only_cb_decl_size_does_not_change_primary_register_profile(self):
        p=pairs()
        p[3]=(dx(1,decls=cb(1,32)+cb(2,0)),p[3][1])
        c=classify_four_pairs(p)["counts"]
        self.assertEqual(c["original_VS_CB_full_profile_distinct"],2)
        self.assertEqual(c["original_VS_CB_slot_profile_distinct"],1)
        self.assertEqual(c["original_VS_CB_size_profile_distinct"],2)
        self.assertEqual(c["original_VS_CB_slots_with_size_change"],1)
        self.assertEqual(c["original_PS_CB_full_profile_distinct"],1)

    def test_primary_slot_change_independently_detected(self):
        p=pairs()
        p[2]=(dx(1,decls=cb(4,24)+cb(2,0)),p[2][1])
        c=classify_four_pairs(p)["counts"]
        self.assertEqual(c["original_VS_CB_slot_profile_distinct"],2)
        self.assertEqual(c["original_VS_CB_size_profile_distinct"],1)

    def test_dynamic_access_bit_is_recorded_not_ignored(self):
        p=pairs()
        p[1]=(dx(1,decls=cb(1,24,1)+cb(2,0)),p[1][1])
        c=classify_four_pairs(p)["counts"]
        self.assertEqual(c["original_CB_dynamic_access_declarations"],1)
        self.assertEqual(c["original_VS_CB_full_profile_distinct"],2)
        self.assertEqual(c["original_VS_CB_slot_profile_distinct"],1)

    def test_sm4_0_and_sm4_1_supported_with_version_gate(self):
        for minor in (0,1):
            with self.subTest(minor=minor):
                version,rows=private_cb_declarations(dx(1,major=4,minor=minor),1)
                self.assertEqual(version,(4,minor))
                self.assertEqual(len(rows),2)

    def test_sm5_1_cannot_be_misread_as_sm5_0_two_index_cb(self):
        with self.assertRaisesRegex(ValueError,"DXBC_CB_UNSUPPORTED_SHADER_MODEL"):
            private_cb_declarations(dx(1,major=5,minor=1),1)

    def test_sm4_2_and_sm6_0_fail_closed(self):
        for major,minor in ((4,2),(6,0)):
            with self.subTest(ver=(major,minor)),self.assertRaisesRegex(ValueError,"DXBC_CB_UNSUPPORTED_SHADER_MODEL"):
                private_cb_declarations(dx(1,major=major,minor=minor),1)

    def test_wrong_cb_operand_index_dimension_rejected(self):
        with self.assertRaisesRegex(ValueError,"DXBC_CB_EXPECT_TWO_INDEX_DECL"):
            private_cb_declarations(dx(1,decls=cb(1,24,dimensions=1)),1)

    def test_wrong_cb_operand_type_rejected(self):
        with self.assertRaisesRegex(ValueError,"DXBC_BIND_OPERAND_TYPE"):
            private_cb_declarations(dx(1,decls=cb(1,24,typ=7)),1)

    def test_stage_identity_and_scope_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"DXBC_BIND_PROGRAM_STAGE"):
            private_cb_declarations(dx(0),1)
        with self.assertRaisesRegex(ValueError,"ORIGINAL_FOUR_DXBC_PAIRS_REQUIRED"):
            classify_four_pairs(pairs()[:3])

    def test_no_cb_declaration_is_distinct_from_unknown_size(self):
        p=[(dx(1,decls=[]),dx(0,decls=[])) for _ in range(4)]
        c=classify_four_pairs(p)["counts"]
        self.assertEqual(c["original_CB_zero_unknown_size_declarations"],0)
        self.assertEqual(c["original_CB_16byte_vector_size_declarations"],0)
        self.assertEqual(c["original_VS_CB_slot_profile_distinct"],1)

if __name__=="__main__":unittest.main()
