"""Source-free negative and positive controls for T2 original Foam Material host census."""
import unittest

from scripts.t2_original_foam_material_host_scan import (
    EXPECTED_BYTES, EXPECTED_COUNT, FOAM_OWNER,
    material_shader_edges, safe_summary, select_sharedowners,
)
from scripts.w1_stage_zip2_owners import PINS


def synthetic_manifest():
    leftover = EXPECTED_BYTES - PINS[FOAM_OWNER][0]
    per = leftover // (EXPECTED_COUNT - 1)
    rows = [{
        "path": FOAM_OWNER, "sha256": PINS[FOAM_OWNER][1],
        "bytes": PINS[FOAM_OWNER][0], "kind": "split"
    }]
    for i in range(1, EXPECTED_COUNT):
        amount = per + (leftover % (EXPECTED_COUNT - 1) if i == EXPECTED_COUNT - 1 else 0)
        rows.append({
            "path": f"Raft_Data/sharedassets{i}.assets",
            "sha256": "a"*64,
            "bytes": amount, "kind": "plain"
        })
    return rows


def empty_result():
    return material_shader_edges(FOAM_OWNER, [], [])


class PinnedSelectionTests(unittest.TestCase):
    def test_full_40_owner_census_budget(self):
        items = select_sharedowners(synthetic_manifest())
        self.assertEqual(len(items), EXPECTED_COUNT)
        self.assertEqual(sum(x["bytes"] for x in items), EXPECTED_BYTES)

    def test_missing_any_owner_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "count_drift"):
            select_sharedowners(synthetic_manifest()[:-1])

    def test_original_foam_owner_pin_mismatch_fails(self):
        m=synthetic_manifest()
        m[0]["sha256"]="b"*64
        with self.assertRaisesRegex(ValueError, "pin_drift"):
            select_sharedowners(m)

    def test_duplicate_owner_fails_closed(self):
        m=synthetic_manifest()
        m[1]["path"]=m[2]["path"]
        with self.assertRaisesRegex(ValueError, "duplicate"):
            select_sharedowners(m)

    def test_manifest_total_budget_drift_fails(self):
        m=synthetic_manifest()
        m[1]["bytes"]+=1
        with self.assertRaisesRegex(ValueError, "budget_drift"):
            select_sharedowners(m)


class FoamPPtrGraphTests(unittest.TestCase):
    def test_genuine_same_owner_foam_local_pathid(self):
        r=material_shader_edges(FOAM_OWNER,[],[(0,2420),(0,100)])
        self.assertEqual(r["local_foam_material_refs"],1)
        self.assertEqual(r["foreign_local_PathID2420_not_foam"],0)

    def test_foreign_local_same_pathid_is_not_foam(self):
        r=material_shader_edges("Raft_Data/sharedassets7.assets",[],[(0,2420)])
        self.assertEqual(r["foreign_local_PathID2420_not_foam"],1)
        self.assertEqual(r["local_foam_material_refs"],0)

    def test_external_foam_basename_pathid_is_candidate_not_GUID(self):
        r=material_shader_edges("Raft_Data/sharedassets7.assets",[
            "archive:/Raft_Data/sharedassets0.assets"
        ], [(1,2420),(1,55),(0,2420)])
        self.assertEqual(r["external_foam_basename_pathid_candidates"],1)
        self.assertEqual(r["external_foam_basename_other_pathids"],1)
        self.assertEqual(r["foreign_local_PathID2420_not_foam"],1)

    def test_external_foam_basename_is_case_insensitive(self):
        r=material_shader_edges("Raft_Data/sharedassets7.assets",
                                [r"archive:\Raft_Data\Sharedassets0.Assets"],
                                [(1,2420)])
        self.assertEqual(r["external_foam_basename_pathid_candidates"],1)

    def test_other_external_pathid_2420_not_a_foam_candidate(self):
        r=material_shader_edges("Raft_Data/sharedassets7.assets",
                                ["unrelated.assets"],[(1,2420)])
        self.assertEqual(r["external_foam_basename_pathid_candidates"],0)

    def test_missing_or_bad_fileID_separately_recorded(self):
        r=material_shader_edges(FOAM_OWNER,["other.assets"],[(2,2420)])
        self.assertEqual(r["malformed_external_fileIDs"],1)
        self.assertEqual(r["local_foam_material_refs"],0)

    def test_unparsed_material_does_not_count_as_negative(self):
        r=material_shader_edges(FOAM_OWNER,[],[None,(0,2420)])
        self.assertEqual((r["material_unparsed"],r["material_parsed"]),(1,1))
        self.assertEqual(r["local_foam_material_refs"],1)

    def test_wrong_path_fileid_types_rejected(self):
        for ptr in [(-1,2420),(1,-1),(True,2420),("1",2420),(1,),123]:
            with self.subTest(ptr=str(ptr)),self.assertRaises(ValueError):
                material_shader_edges(FOAM_OWNER,[],[ptr])

    def test_external_path_null_and_untrusted_shapes_rejected(self):
        for path in ["",None,"x\x00y","a"*1025]:
            with self.subTest(path=str(path)[:10]),self.assertRaises(ValueError):
                material_shader_edges(FOAM_OWNER,[path],[])

    def test_bad_original_owner_name_rejected(self):
        for owner in ["../sharedassets0.assets","Raft_Data/other.assets",None]:
            with self.subTest(owner=owner),self.assertRaises(ValueError):
                material_shader_edges(owner,[],[])

    def test_safe_summary_count_and_nonready_flags(self):
        r=safe_summary([empty_result() for _ in range(EXPECTED_COUNT)],
                       EXPECTED_COUNT,EXPECTED_BYTES)
        self.assertEqual(r["sharedassets_original_files_SHA_verified"],40)
        self.assertEqual(r["sharedassets_original_bytes_SHA_verified"],EXPECTED_BYTES)
        self.assertEqual(r["owners_with_local_foam_material_refs"],0)
        self.assertFalse(r["basename_candidate_is_original_Unity_GUID_verified"])
        self.assertFalse(r["Foam_actual_CB0_runtime_binding_verified"])
        self.assertFalse(r["Android_water_render_pixels_verified"])

    def test_safe_summary_reject_incomplete_sources(self):
        with self.assertRaises(ValueError):
            safe_summary([empty_result()],1,EXPECTED_BYTES)

    def test_safe_summary_reject_missing_material_rows(self):
        rows=[empty_result() for _ in range(EXPECTED_COUNT)]
        rows[0]["material_rows"]=1
        with self.assertRaisesRegex(ValueError,"shape_invalid"):
            safe_summary(rows,EXPECTED_COUNT,EXPECTED_BYTES)


if __name__=="__main__":
    unittest.main()
