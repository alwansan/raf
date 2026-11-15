"""Synthetic, source-free tests for high-impact residual Dummy material ranking."""
import hashlib
import unittest

from scripts.gt_rank_remaining_original_shader_by_export_materials import (
    correlate, EXPECTED_POSTNINE_DUMMY_MATERIALS, STATUS,
)


def digest(name):
    return hashlib.sha256(name.encode("utf-8")).hexdigest()


def fixture():
    weights=[921]+[1]*19+[693]
    assert len(weights)==21 and sum(weights)==1633
    names={("sharedassets0.assets",i):"SyntheticShader"+str(i)
           for i in range(1,22)}
    slots={k:weights[i-1] for i,k in enumerate(names,1)}
    residual={
        digest("SyntheticShader1"):48,
        digest("SyntheticShader2"):30,
        digest("NotInSource"):EXPECTED_POSTNINE_DUMMY_MATERIALS-78,
    }
    return names,slots,residual


class ResidualShaderPriorityTests(unittest.TestCase):
    def test_only_unambiguous_original_names_rank_and_no_private_metadata(self):
        names,slots,residual=fixture()
        private,public=correlate(names,slots,residual)
        self.assertEqual(public["status"],STATUS)
        self.assertEqual(public["matched_unambiguous_source_shader_targets"],2)
        self.assertEqual(public["matched_unambiguous_exported_dummy_material_documents"],78)
        self.assertEqual(public["matched_original_scene_renderer_slot_weights_in_export_material_priority_order"],[921,1])
        self.assertEqual(public["matched_original_export_dummy_material_link_weights_in_descending_order"],[48,30])
        self.assertEqual(public["remaining_unmatched_export_dummy_material_documents"],255)
        self.assertEqual(public["remaining_unmatched_export_name_digest_groups"],1)
        self.assertEqual(public["ambiguous_source_name_groups"],0)
        self.assertEqual(len(private),2)
        for secret in ("private_original_shader_owner","private_original_shader_path_id",
                       "private_original_shader_name_digest"):
            self.assertNotIn(secret,str(public))
        self.assertNotIn("sharedassets0",str(public))
        self.assertNotIn("SyntheticShader1",str(public))

    def test_repeated_original_name_does_not_guess_a_source_identity(self):
        names,slots,residual=fixture()
        names[("sharedassets0.assets",2)]="SyntheticShader1"
        _,public=correlate(names,slots,residual)
        self.assertEqual(public["matched_unambiguous_source_shader_targets"],0)
        self.assertEqual(public["ambiguous_source_name_groups"],1)
        self.assertEqual(public["ambiguous_source_name_exported_material_links"],48)
        self.assertEqual(public["remaining_unmatched_export_dummy_material_documents"],285)
        self.assertEqual(public["remaining_unmatched_export_name_digest_groups"],2)

    def test_bad_material_scope_and_missing_original_are_rejected(self):
        names,slots,residual=fixture()
        residual[digest("NotInSource")]-=1
        with self.assertRaisesRegex(ValueError,"incomplete_real_original_source_priority_scope"):
            correlate(names,slots,residual)
        names,slots,residual=fixture()
        names.pop(("sharedassets0.assets",21))
        with self.assertRaisesRegex(ValueError,"incomplete_real_original_source_priority_scope"):
            correlate(names,slots,residual)


if __name__=="__main__":
    unittest.main()
