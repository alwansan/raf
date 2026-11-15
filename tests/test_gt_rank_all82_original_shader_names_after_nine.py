"""Synthetic deterministic original-name-hash census across 82 owners with no asset bytes."""
import unittest

from scripts.gt_rank_all82_original_shader_names_after_nine import (
    STATUS, rank_name_hashes,
)


class OriginalAll82NamePriorityTests(unittest.TestCase):
    def test_uniquely_matched_ambiguous_and_missing_weights_separate(self):
        originals={
            ("resources.assets",1):"a"*64,
            ("sharedassets0.assets",2):"b"*64,
            ("sharedassets1.assets",3):"b"*64,
            ("level0",4):"d"*64,
        }
        outstanding={
            "a"*64:48,
            "b"*64:26,
            "c"*64:259,
        }
        report=rank_name_hashes(originals,outstanding)
        self.assertEqual(report["status"],STATUS)
        self.assertEqual(report["source_original_Shader48_objects_Sha_verified"],4)
        self.assertEqual(report["dummy_shader_names_uniquely_resolved_to_original_Shader48"],1)
        self.assertEqual(report["dummy_material_links_uniquely_resolved_to_original_Shader48"],48)
        self.assertEqual(report["dummy_material_links_ambiguous_original_Shader48"],26)
        self.assertEqual(report["dummy_material_links_not_in_verified_all82_original_Shader48"],259)
        self.assertEqual(report["original_Shader48_name_collision_candidate_count_bands"],{2:1})
        self.assertEqual(report["uniquely_named_source_Shader48_dummy_Material_priority_descending"],[48])
        self.assertFalse(report["same_export_Shader48_GUID_identity_proven_by_name"])
        for private in ("resources.assets","level0", "aaaa", "bbbb"):
            self.assertNotIn(private,str(report))

    def test_no_silent_missing_material_scope_or_malformed_digest(self):
        originals={("resources.assets",1):"a"*64}
        wrong={"a"*64:332}
        with self.assertRaisesRegex(ValueError,"invalid_original_82_shader_to_dummy_material_scope"):
            rank_name_hashes(originals,wrong)
        malformed={"a"*64:332,"garbage":1}
        with self.assertRaisesRegex(ValueError,"invalid_actual_exported_shader_name_digest"):
            rank_name_hashes(originals,malformed)

    def test_post13_exact_246_dummy_materials_accepts_only_246(self):
        originals={("resources.assets",1):"a"*64,
                   ("sharedassets0.assets",2):"b"*64}
        result=rank_name_hashes(originals,{"a"*64:30,"b"*64:216},
                                expected_dummy_materials=246)
        self.assertEqual(result["exporter_actual_dummy_Material_documents"],246)
        self.assertEqual(result["dummy_material_links_uniquely_resolved_to_original_Shader48"],246)
        with self.assertRaisesRegex(ValueError,"invalid_original_82_shader_to_dummy_material_scope"):
            rank_name_hashes(originals,{"a"*64:333},expected_dummy_materials=246)

    def test_full_scope_unique_and_no_guess(self):
        originals={("resources.assets",1):"b"*64}
        result=rank_name_hashes(originals,{"b"*64:333})
        self.assertEqual(result["dummy_shader_names_uniquely_resolved_to_original_Shader48"],1)
        self.assertEqual(result["dummy_material_links_uniquely_resolved_to_original_Shader48"],333)
        self.assertEqual(result["dummy_material_links_not_in_verified_all82_original_Shader48"],0)


if __name__=="__main__":
    unittest.main()
