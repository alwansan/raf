"""Pure source-free tests for authenticated Shader48→Material property families."""
import json
import unittest

from scripts import t3_original_921_material_property_contract as t3

SECRET = "PRIVATE_PROPRIETARY_PROPERTY_NEVER_LOG"
PRIVATE_TEX = "PRIVATE_TEXTURE_NAME_NEVER_LOG"

def shader(*items):
    return {"m_PropInfo":{"m_Props":[{"m_Name":name,"m_Type":typ}
                                         for name,typ in items]}}

def tex(name=PRIVATE_TEX, path=120):
    return {"m_First":name,
            "m_Second":{"m_Texture":{"m_FileID":0,"m_PathID":path},
                        "m_Scale":{"x":1.0,"y":1.0},
                        "m_Offset":{"x":0.0,"y":0.0}}}

def color(name=SECRET):
    return {"m_First":name,"m_Second":{"r":1.0,"g":0.2,"b":0.3,"a":1.0}}

def scalar(name="PRIVATE_FLOAT_NAME", n=1.0):
    return {"m_First":name,"m_Second":n}

def saved(*,textures=None,colors=None,floats=None,ints=None):
    return {"m_TexEnvs":[tex()] if textures is None else textures,
            "m_Colors":[color()] if colors is None else colors,
            "m_Floats":[scalar()] if floats is None else floats,
            "m_Ints":[] if ints is None else ints}

def classified(decls=None, props=None, weights=None):
    p = {PRIVATE_TEX:"texture", SECRET:"color", "PRIVATE_FLOAT_NAME":"float"} if decls is None else decls
    data = {("sharedassets0.assets",9):saved()} if props is None else props
    w = {k:921 for k in data} if weights is None else weights
    return t3.classify_private_921_materials(p,data,w)

class MaterialPropertyContractTests(unittest.TestCase):
    def test_declaration_type_families_exact(self):
        properties,count=t3.declared_property_families(
            shader((PRIVATE_TEX,4),(SECRET,0),("VEC",1),("ALPHA",2),("RANGE",3)))
        self.assertEqual(count,{"texture":1,"color":2,"float":2})
        self.assertEqual(properties["VEC"],"color")
        self.assertEqual(properties["RANGE"],"float")

    def test_matching_original_source_material_counts_by_weight(self):
        result=classified()
        c=result["counts"]
        self.assertEqual(c["source_Materials_linked_to_921_use_Shader48"],1)
        self.assertEqual(c["source_Material_Renderer_slots_linked_to_921_use_Shader48"],921)
        self.assertEqual(c["source_declared_property_saved_matches"],3)
        self.assertEqual(c["source_Materials_with_any_declared_texture_bound"],1)
        self.assertEqual(c["source_renderer_slots_with_saved_wrong_family"],0)
        self.assertEqual(c["source_declared_property_unsaved_uses_default_possible"],0)
        self.assertFalse(result["unity_Adreno_pixel_color_fixed_or_verified"])

    def test_shader_declared_not_saved_is_not_marked_as_shader_failure(self):
        decl={PRIVATE_TEX:"texture",SECRET:"color","PRIVATE_FLOAT_NAME":"float",
              "UNSAVED_WITH_SHADER_DEFAULT":"float"}
        c=classified(decls=decl)["counts"]
        self.assertEqual(c["source_declared_property_unsaved_uses_default_possible"],1)
        self.assertEqual(c["source_materials_with_at_least_one_unsaved_declared"],1)
        self.assertEqual(c["source_renderer_slots_with_at_least_one_unsaved_declared"],921)
        self.assertEqual(c["source_saved_wrong_family_entries"],0)

    def test_wrong_saved_family_is_an_observation_not_a_failure(self):
        d={PRIVATE_TEX:"texture",SECRET:"texture","PRIVATE_FLOAT_NAME":"float"}
        c=classified(decls=d)["counts"]
        self.assertEqual(c["source_saved_wrong_family_entries"],1)
        self.assertEqual(c["source_renderer_slots_with_saved_wrong_family"],921)
        self.assertEqual(c["source_declared_property_saved_matches"],2)
        self.assertEqual(c["source_declared_property_unsaved_uses_default_possible"],0)

    def test_stale_saved_properties_are_counted_separately(self):
        d={PRIVATE_TEX:"texture",SECRET:"color"}
        c=classified(decls=d)["counts"]
        self.assertEqual(c["source_saved_properties_not_declared"],1)
        self.assertEqual(c["source_materials_with_saved_not_declared"],1)
        self.assertEqual(c["source_renderer_slots_with_saved_not_declared"],921)

    def test_zero_texture_pptr_is_a_real_null_not_bound(self):
        c=classified(props={("sharedassets0.assets",9):saved(textures=[tex(path=0)])})["counts"]
        self.assertEqual(c["source_saved_bound_texture_entries"],0)
        self.assertEqual(c["source_saved_null_texture_entries"],1)
        self.assertEqual(c["source_Materials_with_any_declared_texture_bound"],0)

    def test_original_shader_property_duplicate_rejected(self):
        with self.assertRaisesRegex(ValueError,"duplicate_or_unsupported"):
            t3.declared_property_families(shader((SECRET,0),(SECRET,2)))

    def test_original_shader_invalid_type_rejected(self):
        for typ in (5,7,True,"float"):
            with self.subTest(typ=typ),self.assertRaisesRegex(ValueError,"duplicate_or_unsupported"):
                t3.declared_property_families(shader((SECRET,typ)))

    def test_original_shader_missing_props_rejected(self):
        with self.assertRaisesRegex(ValueError,"property_table"):
            t3.declared_property_families({"m_PropInfo":{"m_Props":None}})

    def test_material_missing_saved_family_rejected(self):
        data=saved()
        del data["m_Ints"]
        with self.assertRaisesRegex(ValueError,"missing_original"):
            t3.normalize_private_saved_properties(data)

    def test_duplicate_saved_name_across_families_rejected(self):
        with self.assertRaisesRegex(ValueError,"cross_family"):
            t3.normalize_private_saved_properties(
                saved(floats=[scalar(name=SECRET)]))

    def test_invalid_private_texenv_uv_rejected(self):
        entry=tex()
        del entry["m_Second"]["m_Offset"]
        with self.assertRaisesRegex(ValueError,"UV"):
            t3.normalize_private_saved_properties(saved(textures=[entry]))

    def test_nonfinite_private_scalar_value_rejected(self):
        with self.assertRaises(ValueError):
            t3.normalize_private_saved_properties(saved(floats=[scalar(n=float("nan"))]))

    def test_genuine_material_renderer_weights_sum_must_be_921(self):
        with self.assertRaisesRegex(ValueError,"untrusted_original_921"):
            classified(weights={("sharedassets0.assets",9):920})

    def test_reject_bool_or_zero_renderer_weight(self):
        for w in (True,0,-1):
            with self.subTest(w=w),self.assertRaisesRegex(ValueError,"slot_weights"):
                classified(weights={("sharedassets0.assets",9):w} if w==True else
                           {("sharedassets0.assets",9):w,("resources.assets",1):921-w})

    def test_missing_original_material_weight_identity_rejected(self):
        with self.assertRaisesRegex(ValueError,"untrusted_original_921"):
            classified(weights={("sharedassets0.assets",10):921})

    def test_forged_shader_saved_material_owner_rejected(self):
        with self.assertRaisesRegex(ValueError,"invalid_authentic"):
            classified(props={("malicious.assets",1):saved()})

    def test_weighted_two_real_materials_no_duplicated_original_identity(self):
        a=("sharedassets0.assets",1);b=("resources.assets",2)
        p={a:saved(),b:saved(textures=[tex(path=0)],colors=[])}
        w={a:1,b:920}
        c=classified(props=p,weights=w)["counts"]
        self.assertEqual(c["source_Materials_linked_to_921_use_Shader48"],2)
        self.assertEqual(c["source_declared_property_saved_matches"],5)
        self.assertEqual(c["source_Materials_with_any_declared_texture_bound"],1)
        self.assertEqual(c["source_renderer_slots_with_at_least_one_unsaved_declared"],920)

    def test_material_int_stale_entry_kept_separate(self):
        c=classified(props={("sharedassets0.assets",9):saved(ints=[{"m_First":"SAVED_INT","m_Second":2}])})["counts"]
        self.assertEqual(c["source_saved_int_property_entries"],1)
        self.assertEqual(c["source_saved_properties_not_declared"],1)

    def test_private_property_names_values_never_leave_aggregate(self):
        output=json.dumps(classified(),sort_keys=True)
        for name in (SECRET,PRIVATE_TEX,"PRIVATE_FLOAT_NAME","sharedassets0.assets"):
            self.assertNotIn(name,output)
        self.assertFalse(json.loads(output)["same_export_or_android_Material_shader_program_binding_verified"])
        self.assertFalse(json.loads(output)["source_game_assets_modified"])


if __name__=="__main__":
    unittest.main()
