"""No-source negative tests for exact Spectrum owner/PPtr and index4 materials."""
import copy
import unittest

from scripts.gt_spectrum_original_material_keyword_link import (
    matching_target, count_owners
)

KW="_SYNTHETIC_INDEX4"
NAMES=["K0","K1","K2","K3",KW]
OWNER="Raft_Data/sharedassets0.assets"


def material(fid=0,pid=2432,valid=None,invalid=None):
    return {"m_Shader":{"m_FileID":fid,"m_PathID":pid},
            "m_ValidKeywords":[] if valid is None else valid,
            "m_InvalidKeywords":[] if invalid is None else invalid}


def fake_owner_rows():
    rows=[{"owner":f"Raft_Data/sharedassets{i}.assets",
           "externals":["foo/sharedassets0.assets"],
           "materials":[]} for i in range(40)]
    rows[0]["materials"]=[material(valid=[KW]),material(invalid=[KW])]
    rows[1]["materials"]=[material(1,2432,[],[]),
                           material(1,2432,[KW],[KW]),
                           material(1,2432,["MISMATCH"],[]),
                           material(0,2432,[KW],[]),
                           material(1,99,[KW],[])]
    return rows


class SourceSpectrumMaterialTests(unittest.TestCase):
    def test_exact_same_owner_local_ptr(self):
        self.assertEqual(matching_target(OWNER,[],{"m_FileID":0,"m_PathID":2432}),"local")

    def test_same_path_id_in_another_owner_not_equivalent(self):
        self.assertEqual(matching_target("Raft_Data/sharedassets7.assets",[],
                       {"m_FileID":0,"m_PathID":2432}),"other")

    def test_one_based_external_owner_path(self):
        self.assertEqual(matching_target("Raft_Data/sharedassets9.assets",
                       ["other","foo/sharedassets0.assets"],
                       {"m_FileID":2,"m_PathID":2432}),"external")
        self.assertEqual(matching_target("Raft_Data/sharedassets9.assets",
                       ["sharedassets00.assets"],{"m_FileID":1,"m_PathID":2432}),"other")

    def test_bad_external_fileid_rejected(self):
        with self.assertRaisesRegex(ValueError,"out_of_range"):
            matching_target(OWNER,[],{"m_FileID":1,"m_PathID":2432})

    def test_bad_pointer_or_negative_rejected(self):
        for bad in ({"m_FileID":True,"m_PathID":2432},
                    {"m_FileID":-1,"m_PathID":2432},
                    {"m_FileID":0,"m_PathID":-1},
                    {"m_FileID":0,"m_PathID":2432,"x":0}):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    matching_target(OWNER,[],bad)

    def test_aggregate_partial_scope_and_active_on_off_without_identity_leak(self):
        report=count_owners(fake_owner_rows(),KW,NAMES)
        self.assertEqual(report["original_sharedassets_owners"],40)
        self.assertEqual(report["all_materials"],7)
        self.assertEqual(report["matched_local"],2)
        self.assertEqual(report["matched_external"],3)
        self.assertEqual(report["matched_keyword_index4_valid"],1)
        self.assertEqual(report["matched_keyword_index4_invalid"],1)
        self.assertEqual(report["matched_keyword_index4_both"],1)
        self.assertEqual(report["matched_keyword_index4_neither"],2)
        self.assertEqual(report["matched_valid_names_outside_original_table"],1)
        self.assertTrue(report["not_full_82_owner_or_runtime_material_census"])
        self.assertFalse(report["original_exported_guid_or_android_runtime_verified"])
        self.assertNotIn(KW,str(report))

    def test_missing_material_keyword_array_counted_not_guessed(self):
        rows=fake_owner_rows()
        rows[0]["materials"][0].pop("m_ValidKeywords")
        r=count_owners(rows,KW,NAMES)
        self.assertEqual(r["matched_materials_without_keyword_arrays"],1)

    def test_original_keyword_table_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError,"scope_invalid"):
            count_owners(fake_owner_rows(),KW,["K0","K1","K2","K3","not4"])

    def test_keyword_container_malformed_rejected(self):
        rows=fake_owner_rows()
        rows[1]["materials"][0]["m_ValidKeywords"]=True
        with self.assertRaisesRegex(ValueError,"arrays_untrusted"):
            count_owners(rows,KW,NAMES)


if __name__=="__main__":
    unittest.main()
