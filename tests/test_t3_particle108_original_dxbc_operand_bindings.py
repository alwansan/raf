"""Source-free original D3D11 declaration operand regression and negative controls."""
import json,struct,unittest
from scripts.t3_particle108_original_dxbc_operand_bindings import (
    _private_parse_decl_operand,_private_stage_layout,classify_four_pairs,STATUS)

def decl(op,typ,indices,tail=(),rep=0,extended=False):
    token=(typ<<12)|(len(indices)<<20)|(rep<<22)|(int(extended)<<31)
    data=[token,*indices,*tail]
    return [op|((1+len(data))<<24),*data]

def dxbc(stage=1,items=None):
    if items is None:
        items=decl(89,8,[1,24])+decl(88,7,[3],[1234])+decl(90,6,[2])+decl(161,7,[4])+decl(162,7,[5],[16])
    words=[(stage<<16)|(5<<4),2+len(items),*items]
    b=struct.pack("<"+"I"*len(words),*words)
    chunk=b"SHDR"+struct.pack("<I",len(b))+b
    return b"DXBC"+bytes(16)+struct.pack("<III",1,36+len(chunk),1)+struct.pack("<I",36)+chunk

def pairs():
    return [(dxbc(1),dxbc(0)) for _ in range(4)]

class Tests(unittest.TestCase):
    def test_immediate_operand_cb_srv_sampler(self):
        for op,kind,indices,trail,family in ((89,8,[2,24],(),"cbuffer"),(88,7,[3],[1],"srv"),(90,6,[1],(),"sampler")):
            with self.subTest(family=family):
                self.assertEqual(_private_parse_decl_operand(decl(op,kind,indices,trail)[1:],op),(family,op,tuple(indices)))

    def test_stage_decodes_all_declarations(self):
        layout=_private_stage_layout(dxbc(),1)
        self.assertEqual(len(layout),5)
        self.assertEqual([x[0] for x in layout].count("srv"),3)

    def test_eight_pairs_profiles_and_zero_privacy_leak(self):
        result=classify_four_pairs(pairs());c=result["counts"]
        self.assertEqual(result["status"],STATUS)
        self.assertEqual(c["original_DXBC_stage_operand_layouts_parsed"],8)
        self.assertEqual(c["original_stage_declaration_operand_records"],40)
        self.assertEqual(c["original_dcl_cbuffer_operand_records"],8)
        self.assertEqual(c["original_dcl_srv_operand_records"],24)
        self.assertEqual(c["original_dcl_sampler_operand_records"],8)
        self.assertEqual(c["original_vertex_private_register_layout_stable_across_four"],1)
        self.assertEqual(c["original_fragment_private_register_layout_stable_across_four"],1)
        self.assertFalse(result["register_array_span_or_cbuffer_byte_offsets_proven"])
        self.assertNotIn("PRIVATE_ORIGINAL_REGISTER",json.dumps(result))

    def test_variant_register_discrepancy_detected(self):
        p=pairs()
        p[3]=(dxbc(1,decl(89,8,[9,24])+decl(88,7,[3],[1])),p[3][1])
        c=classify_four_pairs(p)["counts"]
        self.assertEqual(c["original_vertex_private_register_layouts_across_four_variants"],2)
        self.assertEqual(c["original_vertex_private_register_layout_stable_across_four"],0)

    def test_wrong_operand_type(self):
        with self.assertRaisesRegex(ValueError,"DXBC_BIND_OPERAND_TYPE"):
            _private_parse_decl_operand(decl(88,6,[4],[1])[1:],88)

    def test_unsupported_operand_dimensions(self):
        for idx in ([],[1,2,3]):
            with self.subTest(dimension=len(idx)),self.assertRaisesRegex(ValueError,"DXBC_BIND_OPERAND_DIMENSION"):
                _private_parse_decl_operand(decl(88,7,idx,[1])[1:],88)

    def test_non_immediate_index_modes_rejected(self):
        for rep in range(1,8):
            with self.subTest(rep=rep),self.assertRaisesRegex(ValueError,"DXBC_BIND_OPERAND_INDEX_REP_UNSUPPORTED"):
                _private_parse_decl_operand(decl(90,6,[2],rep=rep)[1:],90)

    def test_operand_extension_rejected(self):
        with self.assertRaisesRegex(ValueError,"DXBC_BIND_OPERAND_EXTENSION_UNSUPPORTED"):
            _private_parse_decl_operand(decl(90,6,[2],extended=True)[1:],90)

    def test_operand_index_truncation_and_absence_rejected(self):
        with self.assertRaisesRegex(ValueError,"DXBC_BIND_OPERAND_INDEX_OVERRUN"):
            _private_parse_decl_operand([(8<<12)|(1<<20)],89)
        with self.assertRaisesRegex(ValueError,"DXBC_BIND_OPERAND_MISSING"):
            _private_parse_decl_operand([],89)

    def test_bad_trailer_rejected(self):
        for op,typ,idx,trail in ((88,7,[4],()),(90,6,[2],[10])):
            with self.subTest(op=op),self.assertRaisesRegex(ValueError,"DXBC_BIND_DECL_TRAILER"):
                _private_parse_decl_operand(decl(op,typ,idx,trail)[1:],op)

    def test_wrong_compiled_shader_stage_rejected(self):
        with self.assertRaisesRegex(ValueError,"DXBC_BIND_PROGRAM_STAGE"):
            _private_stage_layout(dxbc(0),1)

    def test_missing_four_source_pairs_rejected(self):
        for p in ([],pairs()[:3],pairs()+pairs()[:1]):
            with self.subTest(count=len(p)),self.assertRaisesRegex(ValueError,"ORIGINAL_FOUR_DXBC_PAIRS_REQUIRED"):
                classify_four_pairs(p)

    def test_unrelated_opcodes_do_not_become_resources(self):
        one=dxbc(1,[0|(1<<24),1|(1<<24)])
        self.assertEqual(_private_stage_layout(one,1),())
        c=classify_four_pairs([(one,dxbc(0,[])) for _ in range(4)])["counts"]
        self.assertEqual(c["original_dcl_srv_operand_records"],0)

if __name__=="__main__":
    unittest.main()
