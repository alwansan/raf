import unittest
from copy import deepcopy
from scripts import gt_fft_utilities_restore as fft

class TopologyTests(unittest.TestCase):
    def test_requires_seven_single_empty_keyword_routes(self):
        good=[dict(subshader=0, **{'pass': i}, routes=[{'enabled':[]}], unmatched_vertex_keywords=[],keyword_universe=[]) for i in range(7)]
        self.assertEqual(fft.validate_routes(good), 7)
        for changed in (good[:-1], good+good[:1]):
            with self.assertRaises(ValueError): fft.validate_routes(changed)
        for key,value in (('pass',2),('subshader',1),('routes',[{'enabled':['SYNTHETIC']}]),('keyword_universe',[{'name':'SYNTHETIC'}]),('unmatched_vertex_keywords',[[]])):
            changed=deepcopy(good)
            changed[3][key]=value
            with self.subTest(key=key), self.assertRaises(ValueError): fft.validate_routes(changed)

    def test_assembly_preserves_all_source_state_sections(self):
        layout='header\n'+''.join('Pass { state%d\n// Original stage programs attach here\n}\n'%i for i in range(7))
        shader=fft.attach_programs(layout, ['float authentic%d;'%i for i in range(7)])
        self.assertEqual(shader.count('HLSLPROGRAM'),7)
        for i in range(7): self.assertIn('state%d'%i,shader)
        self.assertNotIn('multi_compile',shader)
        self.assertNotIn('Original stage programs attach here',shader)
        with self.assertRaises(ValueError): fft.attach_programs(layout,['x']*6)
