"""T2 synthetic guards: original Foam authored Shader property and Material PPtr."""
import unittest

from scripts.t2_foam_material_property_bridge import (
    shader_authored_texture_props, direct_material_target,
    original_foam_material_links,
)


def mat(shader_id=2420, file_id=0, slots=()):
    return {
        "m_Shader":{"m_FileID":file_id,"m_PathID":shader_id},
        "m_SavedProperties":{"m_TexEnvs":[{"m_First":name,"m_Second":val}
                                          for name,val in slots]},
    }


def env(pointer=(0,81), uv=True):
    data={"m_Texture":{"m_FileID":pointer[0],"m_PathID":pointer[1]}}
    if uv:
        data["m_Scale"]={"x":1.0,"y":1.0}
        data["m_Offset"]={"x":0.0,"y":0.0}
    return data


def profile(names=("prop0",)):
    return {
        "_private_authored_textures":set(names),
        "_private_stage_rows":[
            {"_source_names":list(names),"source_rows":len(names)},
            {"_source_names":[],"source_rows":0}
        ],
    }


class FoamMaterialOriginalPropertyTests(unittest.TestCase):
    def test_shader_type4_authored_texture_property_retained_private(self):
        texture, names=shader_authored_texture_props({"m_PropInfo":{"m_Props":[
            {"m_Name":"secret_tex","m_Type":4},
            {"m_Name":"scalar","m_Type":2},
        ]}})
        self.assertEqual(texture,{"secret_tex"})
        self.assertEqual(names,{"secret_tex","scalar"})

    def test_duplicate_authored_property_rejected_even_other_type(self):
        with self.assertRaises(ValueError):
            shader_authored_texture_props({"m_PropInfo":{"m_Props":[
                {"m_Name":"same","m_Type":4},{"m_Name":"same","m_Type":2},
            ]}})

    def test_empty_authored_property_list_is_empty_not_inferred(self):
        a,b=shader_authored_texture_props({"m_PropInfo":{"m_Props":[]}})
        self.assertEqual(a,set())
        self.assertEqual(b,set())

    def test_wrong_authored_property_container_or_type_fails(self):
        for case in (
            {"m_PropInfo":{}},
            {"m_PropInfo":{"m_Props":{}}},
            {"m_PropInfo":{"m_Props":[{"m_Name":"tex","m_Type":True}]}},
            {"m_PropInfo":{"m_Props":[{"m_Name":"tex","m_Type":4.0}]}},
            {"m_PropInfo":{"m_Props":[{"m_Name":"tex","m_Type":100}]}},
            {"m_PropInfo":{"m_Props":[{"m_Name":"","m_Type":4}]}},
            {"m_PropInfo":{"m_Props":[{"m_Name":"x\x00y","m_Type":4}]}},
        ):
            with self.subTest(case=case),self.assertRaises(ValueError):
                shader_authored_texture_props(case)

    def test_oversized_authored_shader_property_table_rejected(self):
        with self.assertRaises(ValueError):
            shader_authored_texture_props({"m_PropInfo":{
                "m_Props":[{"m_Name":"X"+str(i),"m_Type":4} for i in range(257)]}})

    def test_local_shader_pathid_pointer_exact_not_an_id_collision(self):
        self.assertTrue(direct_material_target(mat()))
        self.assertFalse(direct_material_target(mat(2420,1)))
        self.assertFalse(direct_material_target(mat(2419,0)))
        self.assertFalse(direct_material_target(mat(0,0)))

    def test_malformed_shader_pointer_rejected(self):
        for tree in ({"m_Shader":{"m_FileID":True,"m_PathID":2420}},
                     {"m_Shader":{"fileID":0,"pathID":2420}},
                     {"m_Shader":{"m_FileID":0}},
                     {"m_Shader":{"m_FileID":0,"m_PathID":-1}}):
            with self.subTest(tree=tree),self.assertRaises(ValueError):
                direct_material_target(tree)

    def test_same_owner_typed_texture_and_uv_proven(self):
        counts=original_foam_material_links(
            [mat(slots=[("prop0",env())])],profile(),{81:"Texture2D"})
        self.assertEqual(counts["original_materials_directly_referencing_local_foam_shader"],1)
        self.assertEqual(counts["original_foam_material_texenvs_matching_sampled_source_names"],1)
        self.assertEqual(counts["original_foam_matched_texenvs_with_local_typed_texture"],1)
        self.assertEqual(counts["original_foam_matched_texenvs_with_uv_transform"],1)
        self.assertEqual(counts["original_foam_materials_with_at_least_one_actual_sampled_texenv"],1)
        self.assertNotIn("prop0",str(counts))

    def test_null_texture_source_property_is_not_texture_binding(self):
        c=original_foam_material_links(
            [mat(slots=[("prop0",env((0,0),False))])],profile(),{})
        self.assertEqual(c["original_foam_matched_texenvs_with_null_texture"],1)
        self.assertEqual(c["original_foam_matched_texenvs_with_local_typed_texture"],0)
        self.assertEqual(c["original_foam_matched_texenvs_with_uv_transform"],0)

    def test_external_texture_file_id_classified_unresolved_not_proven(self):
        c=original_foam_material_links(
            [mat(slots=[("prop0",env((3,444)))])],profile(),{})
        self.assertEqual(c["original_foam_matched_texenvs_with_external_texture_unresolved"],1)
        self.assertEqual(c["original_foam_matched_texenvs_with_local_typed_texture"],0)

    def test_unrelated_material_shader_not_counted_as_foam(self):
        c=original_foam_material_links(
            [mat(2419,0,[("prop0",env())])],profile(),{81:"Texture2D"})
        self.assertEqual(c["original_materials_in_this_single_owner"],1)
        self.assertEqual(c["original_materials_directly_referencing_local_foam_shader"],0)
        self.assertEqual(c["original_foam_material_texenvs_matching_sampled_source_names"],0)

    def test_shader_property_without_actual_material_slot_is_not_source_upload(self):
        c=original_foam_material_links([mat()],profile(),{81:"Texture2D"})
        self.assertEqual(c["original_materials_directly_referencing_local_foam_shader"],1)
        self.assertEqual(c["original_foam_material_texenvs_matching_sampled_source_names"],0)

    def test_matched_slot_wrong_local_object_class_rejected(self):
        for local_type in (None,"Shader","Mesh","Material"):
            with self.subTest(local_type=local_type),self.assertRaises(ValueError):
                original_foam_material_links(
                    [mat(slots=[("prop0",env())])],profile(),
                    {81:local_type} if local_type else {})

    def test_saved_texenv_duplicate_private_name_rejected(self):
        with self.assertRaises(ValueError):
            original_foam_material_links([
                mat(slots=[("prop0",env()),("prop0",env((0,0)))]),
            ],profile(),{81:"Texture2D"})

    def test_missing_saved_properties_or_texenv_rejected_on_matching_material(self):
        for tree in (
            {"m_Shader":{"m_FileID":0,"m_PathID":2420}},
            {"m_Shader":{"m_FileID":0,"m_PathID":2420},"m_SavedProperties":{}},
            {"m_Shader":{"m_FileID":0,"m_PathID":2420},"m_SavedProperties":{"m_TexEnvs":{}}},
        ):
            with self.subTest(tree=tree),self.assertRaises(ValueError):
                original_foam_material_links([tree],profile(),{})

    def test_malformed_uv_scale_or_offset_rejected(self):
        bad=env()
        bad["m_Scale"]["x"]=float("nan")
        with self.assertRaises(ValueError):
            original_foam_material_links(
                [mat(slots=[("prop0",bad)])],profile(),{81:"Texture2D"})

    def test_material_texenv_unknown_name_not_alias_to_source(self):
        c=original_foam_material_links(
            [mat(slots=[("other_texture",env())])],profile(),{81:"Texture2D"})
        self.assertEqual(c["original_foam_material_texenvs_matching_sampled_source_names"],0)
        self.assertEqual(c["original_foam_material_texenvs_matching_authored_texture_properties"],0)

    def test_repeated_source_name_across_stages_is_one_material_slot(self):
        p=profile()
        p["_private_stage_rows"].append({"_source_names":["prop0"],"source_rows":1})
        c=original_foam_material_links(
            [mat(slots=[("prop0",env())])],p,{81:"Texture2D"})
        self.assertEqual(c["original_foam_material_texenvs_matching_sampled_source_names"],1)

    def test_multiple_original_materials_are_separate_source_objects(self):
        c=original_foam_material_links([
            mat(slots=[("prop0",env())]),
            mat(slots=[("prop0",env((0,0)))]),
        ],profile(),{81:"Texture2D"})
        self.assertEqual(c["original_materials_directly_referencing_local_foam_shader"],2)
        self.assertEqual(c["original_foam_matched_texenvs_with_local_typed_texture"],1)
        self.assertEqual(c["original_foam_matched_texenvs_with_null_texture"],1)

    def test_no_local_material_proof_is_legitimate_not_game_wide_absence(self):
        c=original_foam_material_links([],profile(),{})
        self.assertEqual(c["original_materials_directly_referencing_local_foam_shader"],0)

    def test_too_many_materials_refused(self):
        with self.assertRaises(ValueError):
            original_foam_material_links([mat() for _ in range(10001)],profile(),{})


if __name__=="__main__":
    unittest.main()
