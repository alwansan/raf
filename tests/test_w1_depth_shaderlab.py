import struct
import unittest
from scripts.w1_depth_shaderlab import decode_empty_parameters, stage_body, render_state, val


def value(n):
    return {'val': n, 'name': ''}


def state():
    blend = {k: value(v) for k, v in dict(srcBlend=1, destBlend=0, srcBlendAlpha=1, destBlendAlpha=0, blendOp=0, blendOpAlpha=0, colMask=0).items()}
    s = {'m_Name': '', 'm_LOD': 0, 'm_Tags': {'tags': []}, 'rtSeparateBlend': False, 'rtBlend0': blend,
         'alphaToMask': value(0), 'zClip': value(1), 'zTest': value(8), 'zWrite': value(1), 'culling': value(0),
         'offsetFactor': value(0), 'offsetUnits': value(0), 'conservative': value(0), 'lighting': False,
         'fogMode': -1, 'fogDensity': value(0), 'fogStart': value(0), 'fogEnd': value(0),
         'fogColor': {k: value(0) for k in ('x', 'y', 'z', 'w')},
         'stencilRef': value(0), 'stencilReadMask': value(255), 'stencilWriteMask': value(255)}
    for key in ('stencilOp', 'stencilOpFront', 'stencilOpBack'):
        s[key] = {k: value(v) for k, v in dict(comp=8, **{'pass': 0}, fail=0, zFail=0).items()}
    return s


class DepthShaderLab(unittest.TestCase):
    def test_fast_property_name_is_not_a_dynamic_override(self):
        self.assertEqual(val({'val': 1, 'name': {'name': ''}}), 1)
        with self.assertRaises(ValueError):
            val({'val': 1, 'name': {'name': 'FixtureDynamic'}})

    def test_parameter_record_empty_and_complete_consumption(self):
        blob = struct.pack('<ii', 202012090, 1) + struct.pack('<i', 0) + struct.pack('<4i', 0, 0, 0, 0)
        self.assertTrue(decode_empty_parameters(blob)['overrides_empty'])
        for wrong in (blob[:-1], blob + b'\0\0\0\0', blob.replace(struct.pack('<i', 202012090), b'ABCD', 1)):
            with self.assertRaises(ValueError):
                decode_empty_parameters(wrong)
        with self.assertRaises(ValueError):
            decode_empty_parameters(struct.pack('<3i', 202012090, 0, 1))

    def test_depth_state_and_color_mask_not_defaulted(self):
        original = state()
        text = render_state(original)
        self.assertIn('ZWrite On', text)
        self.assertIn('ColorMask 0', text)
        self.assertIn('ZTest Always', text)
        original['zWrite'] = value(0)
        self.assertIn('ZWrite Off', render_state(original))
        original['rtBlend0']['colMask'] = value(7)
        with self.assertRaises(ValueError):
            render_state(original)

    def test_dynamic_or_nondefault_fog_not_discarded(self):
        original = state()
        original['zWrite']['name'] = 'FixtureProperty'
        with self.assertRaises(ValueError):
            render_state(original)
        original = state()
        original['fogDensity'] = value(1)
        with self.assertRaises(ValueError):
            render_state(original)

    def test_stage_bodies_are_separated(self):
        text = stage_body('float4 originalVertex;', 'float4 originalFragment;')
        self.assertLess(text.index('SHADER_STAGE_VERTEX'), text.index('originalVertex'))
        self.assertLess(text.index('SHADER_STAGE_FRAGMENT'), text.index('originalFragment'))


if __name__ == '__main__':
    unittest.main()
