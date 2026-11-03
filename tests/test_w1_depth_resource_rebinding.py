import unittest
from scripts.w1_rebind_depth_resources import rebind


class DepthResourceBinding(unittest.TestCase):
    def test_original_register_not_translated_descriptor_order(self):
        source = 'Texture2D<float4> t0 : register(t1); SamplerState s0 : register(s0); float4 sample() { return t0.Sample(s0, 0); }'
        metadata = {'m_CommonParameters': {'m_TextureParams': [{'m_Index': 0, 'm_NameIndex': 7, 'm_SamplerIndex': 0}]}}
        result, counts = rebind(source, metadata, [('FixtureDepth', 7)])
        self.assertIn('FixtureDepth : register(t1)', result)
        self.assertIn('FixtureDepth.Sample(samplerFixtureDepth', result)
        self.assertIn('samplerFixtureDepth : register(s0)', result)
        self.assertEqual(counts['textures_rebound'], 1)
        with self.assertRaises(ValueError):
            rebind(source.replace(' t0 ', ' unknown '), metadata, [('FixtureDepth', 7)])
        with self.assertRaises(ValueError):
            rebind(source, metadata, [('FixtureDepth', 8)])

    def test_two_texture_descriptor_slots_are_not_identifier_uses(self):
        source = 'Texture2D<float4> t0 : register(t2); Texture2D<float4> t1 : register(t3); SamplerState s0 : register(s0); SamplerState s1 : register(s1);'
        metadata = {'m_CommonParameters': {'m_TextureParams': [
            {'m_Index': 0, 'm_NameIndex': 7, 'm_SamplerIndex': 0},
            {'m_Index': 1, 'm_NameIndex': 8, 'm_SamplerIndex': 1}]}}
        result, counts = rebind(source, metadata, [('FixtureA', 7), ('FixtureB', 8)])
        self.assertIn('FixtureB : register(t3)', result)
        self.assertIn('samplerFixtureB : register(s1)', result)
        self.assertEqual(counts['textures_rebound'], 2)

    def test_vertex_position_and_uv_come_from_original_signature(self):
        source = 'struct SPIRV_Cross_Input { float4 pos : TEXCOORD0; float2 uv : TEXCOORD1; };'
        result, counts = rebind(source, {}, [], original_inputs={0: 'POSITION0', 1: 'TEXCOORD0'})
        self.assertIn('pos : POSITION0', result)
        self.assertIn('uv : TEXCOORD0', result)
        self.assertEqual(counts['vertex_semantics_restored'], 2)
        with self.assertRaises(ValueError):
            rebind(source, {}, [], original_inputs={0: 'POSITION0'})


if __name__ == '__main__':
    unittest.main()
