import unittest
from unittest.mock import patch
from scripts.w1_recover_depth_passes import linked_program, interfaces_match, variant_key


class DepthPassLinkage(unittest.TestCase):
    def test_stage_and_blob_index_not_inferred_from_order(self):
        with patch('scripts.w1_recover_depth_passes.scan_blob', return_value={'valid_dxbc_containers': [
                {'offset_in_original_object': 2, 'bytes': 4}]}), patch(
                'scripts.w1_recover_depth_passes.version_tokens', return_value=[{'shader_stage_code': 1}]):
            code, report = linked_program({'m_BlobIndex': 1}, [(0, b'wrong'), (2, b'XXgoodYY')], 1)
            self.assertEqual(code, b'good')
            self.assertEqual(report['segment_index'], 2)
            with self.assertRaises(ValueError):
                linked_program({'m_BlobIndex': 1}, [(0, b'wrong'), (2, b'XXgoodYY')], 0)

    def test_bad_table_index_rejected(self):
        for i in (-1, 2, True, None):
            with self.assertRaises(ValueError):
                linked_program({'m_BlobIndex': i}, [(0, b'one')], 1)

    def test_permutation_and_interface_negative_controls(self):
        self.assertNotEqual(variant_key({'m_KeywordIndices': [1]}), variant_key({'m_KeywordIndices': [2]}))
        vertex = {'outputs': [{'location': 0, 'type': 'vec2'}]}
        self.assertTrue(interfaces_match(vertex, {'inputs': [{'location': 0, 'type': 'vec2'}]}))
        self.assertFalse(interfaces_match(vertex, {'inputs': [{'location': 1, 'type': 'vec2'}]}))
        self.assertFalse(interfaces_match(vertex, {'inputs': [{'location': 0, 'type': 'vec4'}]}))


if __name__ == '__main__':
    unittest.main()
