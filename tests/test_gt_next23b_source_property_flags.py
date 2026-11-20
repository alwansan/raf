"""Source-free NEXT23b opt-in property flags, preserving authored values."""
import copy
import unittest
from scripts.t3_particle108_source_propstate import serialize_properties, PrivateContractError
from test_t3_particle108_source_propstate import prop


class Next23BPropertyFlags(unittest.TestCase):
    def test_optin_preserves_texture_hdr_renderer_and_drawer_flags(self):
        texture = prop('_Tex', 4, [0, 0, 0, 0], 'white', 2)
        texture['m_Flags'] = 4
        color = prop('_Color', 0, [3, 2, 1, .5])
        color['m_Flags'] = 16
        drawer = prop('_Mode', 2, [2, 0, 0, 0])
        drawer['m_Attributes'] = ['Enum(First,0,Second,2)']
        renderer = prop('_Renderer', 4, [0, 0, 0, 0], 'white', 2)
        renderer['m_Flags'] = 2
        parsed = {'m_PropInfo': {'m_Props': [texture, color, drawer, renderer]}}
        before = copy.deepcopy(parsed)
        text, counts = serialize_properties(parsed, allow_original_per_renderer_and_drawer=True,
                                             allow_next23b_texture_hdr_flags=True)
        self.assertIn('[NoScaleOffset] _Tex', text)
        self.assertIn('[HDR] _Color', text)
        self.assertIn('(3,2,1,0.5)', text)
        self.assertIn('[PerRendererData] _Renderer', text)
        self.assertIn('[Enum(First,0,Second,2)]', text)
        self.assertEqual(parsed, before)
        self.assertEqual(counts['original_authored_property_count'], 4)

    def test_default_contract_and_unknown_flag_combinations_remain_strict(self):
        for flags in (4, 16, 20, 8, 32):
            p = prop('_P', 4, [0, 0, 0, 0], 'white', 2)
            p['m_Flags'] = flags
            parsed = {'m_PropInfo': {'m_Props': [p]}}
            with self.assertRaises(PrivateContractError):
                serialize_properties(parsed, allow_original_per_renderer_and_drawer=True)
            if flags not in (4, 16):
                with self.assertRaises(PrivateContractError):
                    serialize_properties(parsed, allow_original_per_renderer_and_drawer=True,
                                         allow_next23b_texture_hdr_flags=True)

    def test_next23b_flag_type_pairs_are_exact_original_texture_and_color(self):
        for flags, typ, values, default, dim in ((4, 0, [1, 1, 1, 1], None, 0),
                                                (16, 4, [0, 0, 0, 0], 'white', 2)):
            p = prop('_P', typ, values, default, dim)
            p['m_Flags'] = flags
            with self.assertRaises(PrivateContractError):
                serialize_properties({'m_PropInfo': {'m_Props': [p]}},
                                     allow_original_per_renderer_and_drawer=True,
                                     allow_next23b_texture_hdr_flags=True)
