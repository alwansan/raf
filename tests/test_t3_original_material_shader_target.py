"""T3 original Shader PPtr one-based authenticated owner dependency controls."""
import unittest
from scripts import t3_original_material_shader_target as m

class OriginalShaderOwnerDependency(unittest.TestCase):
    def fixture(self):
        material={(m.OWNER,i):{"m_FileID":1,"m_PathID":i} for i in range(1,42)}
        external=["archive:/Raft_Data/sharedassets0.assets",
                  "archive:/Raft_Data/sharedassets1.assets",
                  "archive:/Resources/unity_builtin_extra"]
        index={"sharedassets0.assets":1,"sharedassets1.assets":1,"sharedassets6.assets":1}
        return material,external,index
    def call(self,values=None):
        return m.census(*(values or self.fixture()))
    def test_real_41_source_count_without_guessed_target_type(self):
        r=self.call()
        self.assertEqual(r["original_materials"],41)
        self.assertEqual(r["shader_pointer_kind_counts"]["original_external_shader"],41)
        self.assertEqual(r["original_shader_owner_link_occurrences"],{"sharedassets0.assets":41})
        self.assertFalse(r["source_shader_owner_object_types_verified"])
        self.assertFalse(r["shader_export_identity_or_device_pixels_verified"])
    def test_one_based_external_table_never_zero_based(self):
        data=list(self.fixture())
        data[0][(m.OWNER,1)]={"m_FileID":2,"m_PathID":7}
        r=self.call(data)
        self.assertEqual(r["original_shader_owner_link_occurrences"],{
            "sharedassets0.assets":40,"sharedassets1.assets":1})
    def test_engine_shader_dependencies_stay_engine_scoped(self):
        data=list(self.fixture())
        data[0][(m.OWNER,1)]={"m_FileID":3,"m_PathID":7}
        r=self.call(data)
        self.assertEqual(r["shader_pointer_kind_counts"]["source_engine_resource_shader_refs"],1)
        self.assertEqual(r["shader_pointer_kind_counts"]["source_shader_owner_unlisted_or_ambiguous_in_manifest"],0)
    def test_nonlisted_shader_owner_not_claimed_authenticated(self):
        data=list(self.fixture())
        data[1][0]="archive:/Raft_Data/not-shipped.assets"
        r=self.call(data)
        self.assertEqual(r["shader_pointer_kind_counts"]["source_shader_owner_unlisted_or_ambiguous_in_manifest"],41)
    def test_original_null_nonzero_fileid_is_rejected(self):
        data=list(self.fixture())
        data[0][(m.OWNER,1)]={"m_FileID":1,"m_PathID":0}
        with self.assertRaisesRegex(ValueError,"invalid_source_null"):self.call(data)
    def test_original_null_shader_is_reported_not_fabricated(self):
        data=list(self.fixture())
        data[0][(m.OWNER,1)]={"m_FileID":0,"m_PathID":0}
        r=self.call(data)
        self.assertEqual(r["shader_pointer_kind_counts"]["original_null_shader"],1)
    def test_out_of_bounds_external_fileid_rejected(self):
        data=list(self.fixture())
        data[0][(m.OWNER,1)]={"m_FileID":99,"m_PathID":123}
        with self.assertRaisesRegex(ValueError,"outside_authentic_source_table"):self.call(data)
    def test_boolean_or_negative_component_rejected(self):
        for item in ({"m_FileID":True,"m_PathID":1},{"m_FileID":-1,"m_PathID":1},
                     {"m_FileID":1,"m_PathID":-1},{"m_FileID":1,"m_PathID":"1"}):
            data=list(self.fixture())
            data[0][(m.OWNER,1)]=item
            with self.subTest(item=item),self.assertRaisesRegex(ValueError,"untrusted_original_material_shader_pptr"):
                self.call(data)
    def test_wrong_material_count_or_duplicate_identity_refused(self):
        data=list(self.fixture())
        data[0].pop((m.OWNER,1))
        with self.assertRaisesRegex(ValueError,"untrusted_original_41"):self.call(data)
        data=list(self.fixture())
        data[0][("wrongOwner",1)]=data[0].pop((m.OWNER,1))
        with self.assertRaisesRegex(ValueError,"untrusted_original_material_shader_record"):self.call(data)
    def test_original_private_object_paths_not_leaked(self):
        r=str(self.call())
        self.assertNotIn("archive:",r)
        self.assertNotIn("m_PathID",r)
        self.assertNotIn("m_Shader",r)
        self.assertIn("SCOPED_SHA_AUTHENTIC_ORIGINAL_SHADER_DEPENDENCIES_ONLY",r)
if __name__=="__main__":unittest.main()
