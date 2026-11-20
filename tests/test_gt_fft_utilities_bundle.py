from copy import deepcopy
import unittest
import struct
from scripts.gt_verify_921_shader_bundle import verify_routes


def source():
    stage={'m_SubPrograms':[{'m_KeywordIndices':[]}]}
    return {'m_KeywordNames':[], 'm_SubShaders':[{'m_Passes':[
        {'progVertex':deepcopy(stage), 'progFragment':deepcopy(stage)} for _ in range(7)]}]}

class FFTBundle(unittest.TestCase):
    def test_seven_pass_empty_keywords_and_both_stages_required(self):
        parsed=source()
        self.assertEqual(verify_routes(parsed,expected_counts=(1,)*7,zero_keywords=True)['fragment_routes_by_pass'],[1]*7)
        parsed['m_SubShaders'][0]['m_Passes'][6]['progFragment']={}
        with self.assertRaises(ValueError): verify_routes(parsed,expected_counts=(1,)*7,zero_keywords=True)

    def test_global_or_row_keywords_cannot_hide_in_single_route(self):
        for indexed in (False,True):
            parsed=source(); parsed['m_KeywordNames']=['UNEXPECTED']
            if indexed: parsed['m_SubShaders'][0]['m_Passes'][0]['progVertex']['m_SubPrograms'][0]['m_KeywordIndices']=[0]
            with self.subTest(indexed=indexed),self.assertRaises(ValueError):
                verify_routes(parsed,expected_counts=(1,)*7,zero_keywords=True)

    def test_combined_unity_blob_requires_actual_vertex_and_fragment_entries(self):
        def module(model):
            return struct.pack('<10I',0x07230203,0x10000,0,2,0,(5<<16)|15,model,1,0,0)
        def blob(models):
            program=bytearray(52)
            for i,model in enumerate(models):
                raw=module(model)
                struct.pack_into('<II',program,4+i*8,len(program),len(raw))
                program.extend(raw)
            header=bytearray(28)
            struct.pack_into('<I',header,0,202012090)
            return bytes(header)+struct.pack('<I',len(program))+program
        parsed=source()
        for shader_pass in parsed['m_SubShaders'][0]['m_Passes']:
            shader_pass['progVertex']['m_SubPrograms'][0]['m_BlobIndex']=0
            shader_pass['progFragment']={}
        valid=[(0,blob((0,4)))]
        proof=verify_routes(parsed,valid,smolv_decoder='unused-plain-spirv',expected_counts=(1,)*7,zero_keywords=True)
        self.assertEqual(proof['fragment_routes_by_pass'],[1]*7)
        with self.assertRaises(ValueError):
            verify_routes(parsed,[(0,blob((0,)))],smolv_decoder='unused-plain-spirv',expected_counts=(1,)*7,zero_keywords=True)
