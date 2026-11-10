import unittest
from gfxlab.tools.multi_material_float_wrap import (
    enum_label,scalar_bucket,color_bucket,_inspect_settings,KNOWN_FLOAT,
)

class TestMaterialFloatWrap(unittest.TestCase):
    def test_2021_texture_format_enum(self):
        self.assertEqual(enum_label("TextureFormat",10),"DXT1")
        self.assertEqual(enum_label("TextureFormat",12),"DXT5")
        self.assertEqual(enum_label("TextureFormat",11),"unmapped_source_code")

    def test_2021_color_space_is_texture_specific(self):
        self.assertEqual(enum_label("TextureColorSpace",0),"Linear")
        self.assertEqual(enum_label("TextureColorSpace",1),"sRGB")
        self.assertEqual(enum_label("TextureColorSpace",True),"missing_or_malformed")

    def test_filter_and_wrap_enums(self):
        self.assertEqual(enum_label("FilterMode",1),"Bilinear")
        self.assertEqual(enum_label("TextureWrapMode",0),"Repeat")
        self.assertEqual(enum_label("TextureWrapMode",1),"Clamp")
        self.assertEqual(enum_label("TextureWrapMode",-1),"unmapped_source_code")

    def test_unknown_class_rejected(self):
        with self.assertRaises(ValueError):
            enum_label("PlayerSettingsColorSpace",1)

    def test_scalar_buckets(self):
        self.assertEqual(scalar_bucket(-0.5),"negative")
        self.assertEqual(scalar_bucket(0),"zero")
        self.assertEqual(scalar_bucket(0.5),"between_zero_one")
        self.assertEqual(scalar_bucket(1),"one")
        self.assertEqual(scalar_bucket(2),"above_one")

    def test_invalid_scalars_rejected(self):
        for value in (float("nan"),float("inf"),True,"0",10001):
            with self.subTest(value=str(value)):
                with self.assertRaises(ValueError):
                    scalar_bucket(value)

    def test_color_buckets(self):
        self.assertEqual(color_bucket({"r":1,"g":1,"b":1,"a":1}),"white_rgba")
        self.assertEqual(color_bucket({"r":0,"g":0,"b":0,"a":0}),"zero_rgba")
        self.assertEqual(color_bucket({"r":1,"g":0,"b":0,"a":1}),"non_identity_color")

    def test_malformed_color_rejected(self):
        with self.assertRaises(ValueError):
            color_bucket({"r":1,"g":1,"b":1})

    def test_axis_wrap_modes_are_not_generic_wrap_mode(self):
        settings={"m_WrapU":0,"m_WrapV":1,"m_WrapW":2,
                  "m_FilterMode":1,"m_Aniso":1,"m_MipBias":0.0}
        self.assertEqual(_inspect_settings(settings),{
           "U":"Repeat","V":"Clamp","W":"Mirror","filter":"Bilinear"
        })

    def test_missing_axis_remains_unknown(self):
        settings={"m_WrapU":0,"m_FilterMode":1,"m_Aniso":1,"m_MipBias":0}
        result=_inspect_settings(settings)
        self.assertEqual(result["V"],"missing_or_malformed")
        self.assertEqual(result["W"],"missing_or_malformed")

    def test_approved_categories_are_not_raw_property_names(self):
        self.assertEqual(KNOWN_FLOAT["_Metallic"],"metallic_named")
        self.assertEqual(KNOWN_FLOAT["_BumpScale"],"normal_strength_named")
