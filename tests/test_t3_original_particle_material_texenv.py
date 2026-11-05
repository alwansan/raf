"""T3 source-free adversarial original ParticleShader48 108 Material TexEnv controls.

The type-48 source keys/Material21 PPtrs below are synthetic, not Raft IDs.
"""
import json
import math
import unittest

from scripts import t3_original_particle_material_texenv as m
from scripts.b05_verify_material_texenv_bindings import normalize_texenvs


def original_env(name, fid, pid, scale=(1.,1.), offset=(0.,0.)):
    return {"m_First":name, "m_Second":{
        "m_Texture":{"m_FileID":fid,"m_PathID":pid},
        "m_Scale":{"x":scale[0],"y":scale[1]},
        "m_Offset":{"x":offset[0],"y":offset[1]}}}


class OriginalParticleMaterialTexEnv(unittest.TestCase):
    def fixture(self):
        material_a=("resources.assets",301)
        material_b=("sharedassets0.assets",302)
        rows={
          material_a:(normalize_texenvs([
              original_env("fixture_private_tex",0,120),
              original_env("fixture_second_tex",2,530),
              original_env("fixture_null_tex",0,0)
          ]),2),
          material_b:(normalize_texenvs([
              original_env("fixture_private_tex",1,999),
              original_env("fixture_null_tex",0,0)
          ]),1)
        }
        return rows,set(rows)

    def test_true_distinct_materials_vs_108_renderer_slot_multiplicity(self):
        rows,selected=self.fixture()
        out=m.census(rows,selected,renderer_slots=108)
        self.assertEqual(out["status"],m.STATUS)
        self.assertEqual(out["original_particle_renderer_material_slot_references"],108)
        self.assertEqual(out["original_particle_material_objects"],2)
        self.assertEqual(out["original_particle_texenv_slots"],5)
        self.assertEqual(out["original_particle_texenv_local_texture_pointers"],1)
        self.assertEqual(out["original_particle_texenv_external_texture_pointers"],2)
        self.assertEqual(out["original_particle_texenv_null_texture_slots"],2)
        self.assertEqual(out["original_particle_texenv_uv_complete"],5)
        self.assertEqual(out["original_particle_material_objects_with_bound_textures"],2)
        self.assertEqual(out["original_particle_distinct_texture_PPtr_shapes_in_material_owners"],3)
        self.assertFalse(out["bound_Texture2D_asset_type_or_payload_verified"])
        self.assertFalse(out["same_instance_export_or_Android_device_texture_binding_verified"])
        safe=json.dumps(out)
        for token in ("fixture_private_tex","fixture_second_tex","fixture_null_tex",
                      '"m_PathID"', '"m_FileID"', "resources.assets", "sharedassets0.assets"):
            self.assertNotIn(token,safe)

    def test_material_selection_and_renderer_counts_must_match(self):
        rows,selected=self.fixture()
        for expected in (set(), {("resources.assets",301)}, selected|{("resources.assets",999)}):
            with self.subTest(expected=repr(expected)),self.assertRaisesRegex(ValueError,"scope"):
                m.census(rows,expected)
        with self.assertRaisesRegex(ValueError,"scope"):
            m.census(rows,selected,renderer_slots=1)

    def test_original_provider_and_owner_material_key_validation(self):
        rows,selected=self.fixture()
        data={("unknown_owner.assets",42):next(iter(rows.values()))}
        with self.assertRaisesRegex(ValueError,"material_row"):
            m.census(data,set(data))
        data={("resources.assets",True):next(iter(rows.values()))}
        with self.assertRaisesRegex(ValueError,"material_row"):
            m.census(data,set(data))

    def test_b05_real_original_texenv_schema_rejects_duplicate_and_bad_texture_pointer(self):
        with self.assertRaises(ValueError):
            normalize_texenvs([original_env("fixture",0,1),original_env("fixture",0,2)])
        with self.assertRaises(ValueError):
            normalize_texenvs([original_env("negative",-1,6)])
        with self.assertRaises(ValueError):
            normalize_texenvs([original_env("null_ext",3,0)])
        with self.assertRaises(ValueError):
            normalize_texenvs([original_env("nan_uv",0,1,scale=(math.nan,1.))])

    def test_external_fileid_outside_owner_dependencies_is_not_counted(self):
        rows,selected=self.fixture()
        a=("resources.assets",301)
        original_slots,count=rows[a]
        copied=dict(original_slots)
        copied["fixture_private_tex"]=((3,5),(1.,1.,0.,0.))
        rows[a]=(copied,count)
        with self.assertRaisesRegex(ValueError,"texture_pointer"):
            m.census(rows,selected)

    def test_empty_texenv_material_is_valid_but_not_proof_of_texture(self):
        key=("resources.assets",88)
        r=m.census({key:({},0)},{key},renderer_slots=108)
        self.assertEqual(r["original_particle_materials_with_no_texenv_slots"],1)
        self.assertEqual(r["original_particle_texenv_slots"],0)
        self.assertEqual(r["original_particle_material_objects_with_bound_textures"],0)
        self.assertFalse(r["same_instance_export_or_Android_device_texture_binding_verified"])

    def test_bad_normalized_uv_rejected_not_published(self):
        key=("resources.assets",88)
        for uv in ((1.,1.,1.),(float("inf"),1.,0.,0.),(True,1.,0.,0.)):
            with self.subTest(uv=repr(uv)),self.assertRaisesRegex(ValueError,"texenv_uv"):
                m.census({key:({"private":((0,10),uv)},0)},{key})

if __name__=="__main__":
    unittest.main()
