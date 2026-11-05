"""T3 source-free adversarial original Renderer→Material→Shader usage counts.

No real original assets in repository fixtures. Pure classification remains
explicitly SYNTHETIC until the caller completed SHA-authenticated source load.
"""
import json
import unittest

from scripts import t3_original_renderer_shader_impact as m


class OriginalSceneShaderUsage(unittest.TestCase):
    def fixture(self):
        # 8 Renderer Material slots from original scene identities; six
        # nonnull original Material class targets; two truly null.
        edges=[
          ("level0",11,"MeshRenderer",("resources.assets",1)),
          ("level0",11,"MeshRenderer",("resources.assets",1)),
          ("level0",12,"SkinnedMeshRenderer",("resources.assets",1)),
          ("level0",13,"MeshRenderer",("sharedassets0.assets",2)),
          ("level0",14,"ParticleSystemRenderer",("sharedassets0.assets",2)),
          ("level1",15,"MeshRenderer",("sharedassets1.assets",3)),
          ("level1",16,"MeshRenderer",None),
          ("level1",17,"MeshRenderer",None),
        ]
        mats={
          ("resources.assets",1):("sharedassets0.assets",10),
          ("sharedassets0.assets",2):("sharedassets0.assets",11),
          ("sharedassets1.assets",3):("unity_builtin_extra",46),
        }
        shader={
          ("sharedassets0.assets",10):{"passes":4,"subshaders":1},
          ("sharedassets0.assets",11):{"passes":1,"subshaders":1},
        }
        return edges,mats,shader

    def run_data(self,data=None):
        return m.summarize(*(data or self.fixture()),expected_slots=8,expected_nonnull=6)

    def test_renderer_slot_frequency_vs_distinct_renderer_not_confused(self):
        result=self.run_data()
        self.assertEqual(result["status"],"SYNTHETIC_OR_UNAUTHENTICATED_SOURCE_ONLY")
        self.assertFalse(result["six_original_scenes_sha_verified"])
        self.assertEqual(result["original_material_target_owners_sha_verified"],0)
        self.assertEqual(result["original_nonnull_renderer_material_slots"],6)
        self.assertEqual(result["original_null_renderer_material_slots"],2)
        self.assertEqual(result["original_distinct_referenced_Material_objects"],3)
        self.assertEqual(result["original_distinct_referenced_Shader_objects"],3)
        self.assertEqual(result["original_distinct_typed_Shader48_targets"],2)
        self.assertEqual(result["counts"]["original_slots_to_verified_Shader48"],5)
        self.assertEqual(result["counts"]["original_slots_to_verified_multi_pass_Shader48"],3)
        self.assertEqual(result["counts"]["original_slots_to_unstaged_Unity_engine_Shader"],1)
        self.assertEqual(result["original_Shader_material_slot_use_frequency_bands"],{"1":1,"2-4":2})
        self.assertEqual(result["top_ten_original_shader_slot_counts_no_identity"],[3,2,1])
        self.assertEqual(result["top_ten_typed_Shader48_slot_counts_no_identity"],[3,2])
        self.assertEqual(result["original_Shader_distinct_renderer_use_frequency_bands"],{"1":1,"2-4":2})
        self.assertEqual(result["per_authenticated_source_shader_owner_counts"]["sharedassets0.assets"]["renderer_material_slots"],5)

    def test_same_renderer_multiple_slots_do_not_fake_distinct_renderer_count(self):
        data=self.fixture()
        data[0][1]=("level0",11,"MeshRenderer",("resources.assets",1))
        summary=self.run_data(data)
        self.assertEqual(summary["original_renderer_objects_with_any_material_slots"],7)
        self.assertEqual(summary["original_Shader_distinct_renderer_use_frequency_bands"],{"1":1,"2-4":2})

    def test_refuse_incomplete_unpinned_population(self):
        data=self.fixture()
        data[0].pop()
        with self.assertRaisesRegex(ValueError,"incomplete_original"):
            self.run_data(data)

    def test_missing_true_Material_class21_not_claimed_resolved(self):
        data=self.fixture()
        del data[1][("resources.assets",1)]
        with self.assertRaisesRegex(ValueError,"original_material_target_missing"):
            self.run_data(data)

    def test_staged_Shader48_missing_is_source_failure(self):
        data=self.fixture()
        del data[2][("sharedassets0.assets",10)]
        with self.assertRaisesRegex(ValueError,"original_Shader48_target_missing"):
            self.run_data(data)

    def test_other_owner_shaders_are_unverified_not_class48(self):
        data=self.fixture()
        data[1][("resources.assets",1)]=("sharedassets99.assets",234)
        result=self.run_data(data)
        self.assertEqual(result["counts"]["original_slots_to_unstaged_other_Shader"],3)
        self.assertEqual(result["counts"]["original_slots_to_verified_Shader48"],2)
        self.assertFalse(result["postvendor_dummy_marker_or_same_export_Shader_identity_checked"])

    def test_null_Material_Shader_stays_explicit_not_identity_guess(self):
        data=self.fixture()
        data[1][("resources.assets",1)]=None
        result=self.run_data(data)
        self.assertEqual(result["counts"]["original_Material_with_null_Shader_slots"],3)
        self.assertEqual(result["top_ten_original_shader_slot_counts_no_identity"],[2,1])

    def test_invalid_shader_source_owner_or_nonpositive_path_rejected(self):
        for bad in (("",1),("sharedassets0.assets",-1),("sharedassets0.assets",0),
                    ("sharedassets0.assets",True),("sharedassets0.assets","10")):
            data=self.fixture()
            data[1][("resources.assets",1)]=bad
            with self.subTest(bad=bad),self.assertRaisesRegex(ValueError,"malformed_original"):
                self.run_data(data)

    def test_invalid_or_foreign_renderer_Material_owners_rejected(self):
        for bad in (("sharedassets9.assets",1),("resources.assets",0),
                    ("resources.assets",True),("resources.assets","1")):
            data=self.fixture()
            data[0][0]=("level0",11,"MeshRenderer",bad)
            with self.subTest(bad=bad),self.assertRaisesRegex(ValueError,"unverified_original_material"):
                self.run_data(data)

    def test_invalid_Shader48_pass_field_rejected(self):
        for bad in (None,True,-1,"3"):
            data=self.fixture()
            data[2][("sharedassets0.assets",10)]={"passes":bad,"subshaders":1}
            with self.subTest(bad=bad),self.assertRaisesRegex(ValueError,"malformed_original_typed"):
                self.run_data(data)

    def test_source_type_and_renderer_owner_failure(self):
        for bad in (("level999",11,"MeshRenderer",None),
                    ("level0",0,"MeshRenderer",None),
                    ("level0",11,"RandomRenderer",None)):
            data=self.fixture()
            data[0][6]=bad
            with self.subTest(bad=bad),self.assertRaisesRegex(ValueError,"invalid_original_renderer"):
                self.run_data(data)

    def test_no_original_opaque_ids_names_or_shader_Guids_in_report(self):
        s=json.dumps(self.run_data(),sort_keys=True)
        for value in ("m_PathID","m_Shader","ShaderImporter","shader_name",
                      "0000000000000000",'"pid"', "234"):
            self.assertNotIn(value,s)
        self.assertFalse(self.run_data()["unity_or_android_drawcalls_white_pixels_verified"])


if __name__=="__main__":
    unittest.main()
