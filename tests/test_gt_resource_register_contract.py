"""Authored regressions for default-space resource declaration and metadata joins."""
import copy
import unittest
from scripts.gt_resource_register_contract import (
    RESOURCE, registered_resources, strip_registered_resources, texture_sampler_bindings,
)

BARE = 'Texture2D<float4> t3 : register(t21);\nSamplerState s7 : register(s16);\n'
SPACE = BARE.replace('t21)', 't21, space0)').replace('s16)', 's16, space0)')
COMMON = {'m_TextureParams': [{'m_Index':3, 'm_NameIndex':11, 'm_SamplerIndex':7},
                             {'m_Index':5, 'm_NameIndex':12, 'm_SamplerIndex':9}]}
NAMES = {11:'_OldTex', 12:'_UnusedTex'}
OVERRIDE = [{'kind':0, 'index':3, 'name':'_MainTex', 'extra_value':7}]
EXPECTED = [{'kind':'t','slot':3,'source_texture_name':'_MainTex'},
            {'kind':'s','slot':7,'source_texture_name':'_MainTex'}]


class ResourceRegisterContract(unittest.TestCase):
    def test_legacy_four_group_api_and_default_space(self):
        self.assertEqual([m.groups() for m in registered_resources(BARE)],
                         [m.groups() for m in registered_resources(SPACE)])
        self.assertEqual(RESOURCE.groups, 4)
        self.assertEqual(len(list(RESOURCE.finditer(SPACE))),2)

    def test_nonzero_and_malformed_space_rejected(self):
        for form in ('space1','space2','space00','space-1','spaceX','space0, space0'):
            with self.subTest(form=form), self.assertRaises(ValueError):
                registered_resources(SPACE.replace('space0',form,1))
        for code in (BARE.replace('register(t21)','register(t21, )'),
                     BARE.replace('register(t21)','register(t21'),
                     BARE.replace(': register(t21)',''),
                     BARE.replace('t3 :','t3[2] :')):
            with self.subTest(code=code), self.assertRaises(ValueError):
                registered_resources(code)

    def test_comment_and_string_declarations_not_counted(self):
        code = '// Texture2D t8 : register(t8, space1);\n' + SPACE + '\n/* SamplerState s8 : register(s8); */'
        self.assertEqual(len(registered_resources(code)),2)
        self.assertIn('// Texture2D t8 : register(t8, space1);',strip_registered_resources(code))

    def test_duplicate_translated_resource_or_wrong_class_rejected(self):
        for code in (BARE + 'Texture2D t4 : register(t21);',
                     BARE + 'Texture2D t3 : register(t22);',
                     BARE.replace('register(t21)','register(s21)'),
                     BARE.replace('register(s16)','register(t16)')):
            with self.subTest(code=code), self.assertRaises(ValueError):
                registered_resources(code)

    def test_strip_only_t_s_and_preserve_existing_unregistered(self):
        tail = 'cbuffer Example : register(b0) { float4 color; };\nTexture2D<float4> _Other;\n'
        self.assertEqual(strip_registered_resources(BARE+tail),strip_registered_resources(SPACE+tail))
        result = strip_registered_resources(SPACE+tail)
        self.assertEqual(result,'Texture2D<float4> t3;\nSamplerState s7;\n'+tail)
        self.assertEqual(strip_registered_resources(result),result)

    def test_texture_array_type_is_not_descriptor_array(self):
        self.assertEqual(registered_resources('Texture2DArray<float4> t3 : register(t21, space0);')[0][1],
                         'Texture2DArray<float4>')
        with self.assertRaises(ValueError):
            registered_resources('Texture2D<float4> t3[2] : register(t21, space0);')

    def test_source_slot_not_translated_slot_and_variant_override(self):
        for code in (BARE,SPACE):
            self.assertEqual(texture_sampler_bindings(code,COMMON,NAMES,OVERRIDE),EXPECTED)
            self.assertEqual(texture_sampler_bindings(code,COMMON,NAMES,[])[0]['source_texture_name'],'_OldTex')
        with self.assertRaisesRegex(ValueError,'ambiguous'):
            texture_sampler_bindings(SPACE.replace('t3 :','t21 :'),COMMON,NAMES,OVERRIDE)

    def test_duplicate_metadata_lane_not_hidden_by_dict_overwrite(self):
        d=copy.deepcopy(COMMON);d['m_TextureParams'].append(d['m_TextureParams'][0].copy())
        for common,variant in ((d,OVERRIDE),(COMMON,OVERRIDE+OVERRIDE)):
            with self.assertRaisesRegex(ValueError,'duplicate_original_texture_slot'):
                texture_sampler_bindings(SPACE,common,NAMES,variant)

    def test_missing_name_ambiguous_sampler_and_aliased_source_rejected(self):
        for common,names,variant,code in (
            (COMMON,{12:'_Unused'},OVERRIDE,SPACE),
            (COMMON,NAMES,OVERRIDE+[{'kind':0,'index':5,'name':'_Other','extra_value':7}],SPACE),
            (COMMON,NAMES,OVERRIDE,SPACE+'Texture2D t03 : register(t22);'),
            (COMMON,NAMES,OVERRIDE,SPACE.replace('s7 :','s8 :')),
        ):
            with self.subTest(code=code),self.assertRaises(ValueError):
                texture_sampler_bindings(code,common,names,variant)

    def test_invalid_metadata_types_and_target_collision(self):
        for change in ({'index':True},{'name':'not valid'},{'extra_value':True}):
            bad=dict(OVERRIDE[0],**change)
            with self.assertRaises(ValueError):
                texture_sampler_bindings(SPACE,COMMON,NAMES,[bad])
        code=SPACE+'Texture2D t5 : register(t22);'
        with self.assertRaisesRegex(ValueError,'symbol_collision'):
            texture_sampler_bindings(code,COMMON,NAMES,OVERRIDE+[{'kind':0,'index':5,'name':'_MainTex','extra_value':9}])


if __name__ == '__main__':
    unittest.main()
