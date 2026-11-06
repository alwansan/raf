"""T2 source-free adversarial scene MonoBehaviour PPtr scanner controls."""
import unittest
from scripts.t2_original_scene_foam_component_scan import (
    EXPECTED_SCENES,EXPECTED_BYTES,select_original_levels,
    walk_tree_pptrs,classify_scene_foam,safe_scene_summary,
)


def items():
    base=EXPECTED_BYTES//EXPECTED_SCENES
    return [
        {"path":f"Raft_Data/level{i}", "bytes":base+(EXPECTED_BYTES%EXPECTED_SCENES if i==EXPECTED_SCENES-1 else 0),
         "sha256":"a"*64, "kind":"split" if i in (0,20) else "plain"}
        for i in range(EXPECTED_SCENES)
    ]


class OriginalLevelManifestTests(unittest.TestCase):
    def test_exact_all_40_levels_sha_manifest_scope(self):
        rows=select_original_levels(items())
        self.assertEqual(len(rows),40)
        self.assertEqual(sum(x["bytes"] for x in rows),EXPECTED_BYTES)
        self.assertEqual(rows[3]["path"],"Raft_Data/level3")

    def test_missing_level_fails(self):
        with self.assertRaisesRegex(ValueError,"level_count"):
            select_original_levels(items()[:-1])

    def test_extra_non_level_ignored(self):
        rows=items()+[{"path":"Raft_Data/sharedassets0.assets","bytes":999,"sha256":"b"*64,"kind":"plain"}]
        self.assertEqual(len(select_original_levels(rows)),40)

    def test_duplicate_level_rejected(self):
        rows=items()
        rows[1]["path"]=rows[2]["path"]
        with self.assertRaisesRegex(ValueError,"duplicate"):
            select_original_levels(rows)

    def test_size_budget_drift_rejected(self):
        rows=items()
        rows[5]["bytes"]+=1
        with self.assertRaisesRegex(ValueError,"byte_budget"):
            select_original_levels(rows)


class StructuredPPtrTraversalTests(unittest.TestCase):
    def test_nested_list_dict_exact_pptrs(self):
        a={"source":{"items":[
            {"fileRef":{"m_FileID":1,"m_PathID":2420}},
            {"refs":[{"m_FileID":0,"m_PathID":100}]},
        ]}}
        self.assertCountEqual(list(walk_tree_pptrs(a)),[(1,2420),(0,100)])

    def test_non_pair_and_unrelated_fields_ignored(self):
        self.assertEqual(list(walk_tree_pptrs({
            "m_PathID":2420,"one":{"m_FileID":1},
            "badshape": {"m_FileID":2,"PathId":2420}
        })),[])

    def test_bool_pptr_value_rejected(self):
        with self.assertRaisesRegex(ValueError,"type"):
            list(walk_tree_pptrs({"m_FileID":True,"m_PathID":2420}))

    def test_explicit_recursion_depth_guard(self):
        node={"m_FileID":1,"m_PathID":2420}
        for _ in range(30):
            node={"child":node}
        with self.assertRaisesRegex(ValueError,"complexity"):
            list(walk_tree_pptrs(node))


class OriginalSceneOwnerResolutionTests(unittest.TestCase):
    def test_material_exact_external_foam_candidate(self):
        c=classify_scene_foam("Raft_Data/level1",[
            "archive:/Raft_Data/sharedassets0.assets"
        ],[(1,2420)],[])
        self.assertEqual(c["scene_foam_Material_Shader_PPtr_candidates"],1)
        self.assertEqual(c["scene_Material_parsed"],1)

    def test_mono_nested_original_foam_candidate(self):
        c=classify_scene_foam("Raft_Data/level5",[
            "archive:/Raft_Data/sharedassets0.assets"
        ],[],[[(1,2420),(0,2420),(1,9)]])
        self.assertEqual(c["scene_foam_Component_PPtr_candidates"],1)
        self.assertEqual(c["scene_foreign_local_PathID2420_not_foam"],1)
        self.assertEqual(c["scene_other_Component_PPtrs_to_foam_owner"],1)
        self.assertEqual(c["scene_Component_structural_PPtrs_examined"],3)

    def test_same_pathid_other_external_not_foam(self):
        c=classify_scene_foam("Raft_Data/level2",["elsewhere.assets"],[(1,2420)],
                               [[(1,2420)]])
        self.assertEqual(c["scene_foam_Component_PPtr_candidates"],0)
        self.assertEqual(c["scene_foam_Material_Shader_PPtr_candidates"],0)

    def test_foreign_local_pathid_not_original_foam(self):
        c=classify_scene_foam("Raft_Data/level7",[],[(0,2420)],[[(0,2420)]])
        self.assertEqual(c["scene_foreign_local_PathID2420_not_foam"],2)

    def test_negative_invalid_external_indices_counted(self):
        c=classify_scene_foam("Raft_Data/level7",["a.assets"],[(2,100)],[[(3,4)]])
        self.assertEqual(c["scene_external_fileID_out_of_range"],2)

    def test_opaque_mono_must_not_be_false_negative(self):
        c=classify_scene_foam("Raft_Data/level4",[],[None],[None, []])
        self.assertEqual(c["scene_Component_unparsed"],1)
        self.assertEqual(c["scene_Component_parsed"],1)
        self.assertEqual(c["scene_Material_unparsed"],1)

    def test_path_rejects_null(self):
        with self.assertRaisesRegex(ValueError,"malformed"):
            classify_scene_foam("Raft_Data/level3",["bad\x00path"],[],[])

    def test_malformed_pptr_value_rejected(self):
        with self.assertRaisesRegex(ValueError,"PPtr_shape"):
            classify_scene_foam("Raft_Data/level3",[],[(True,2420)],[])

    def test_non_level_owner_rejected(self):
        with self.assertRaisesRegex(ValueError,"non_scene"):
            classify_scene_foam("Raft_Data/sharedassets0.assets",[],[],[])

    def test_summaries_never_prove_device(self):
        rows=[classify_scene_foam(f"Raft_Data/level{i}",[],[],[]) for i in range(40)]
        out=safe_scene_summary(rows,EXPECTED_BYTES)
        self.assertEqual(out["original_scene_SHA_authenticated_file_count"],40)
        self.assertFalse(out["original_Foam_Shader_asset_SHA_authenticated_this_run"])
        self.assertTrue(out["original_Foam_Shader_asset_SHA_attested_previous_CI"])
        self.assertFalse(out["Android_Adreno_water_pixels_verified"])
        self.assertFalse(out["source_external_basename_proves_Unity_GUID"])

    def test_summary_incomplete_files_rejected(self):
        rows=[classify_scene_foam(f"Raft_Data/level{i}",[],[],[]) for i in range(39)]
        with self.assertRaisesRegex(ValueError,"count_not_complete"):
            safe_scene_summary(rows,EXPECTED_BYTES)

    def test_summary_bad_count_structural_rejected(self):
        rows=[classify_scene_foam(f"Raft_Data/level{i}",[],[],[]) for i in range(40)]
        rows[0]["scene_Component_records"]=1
        with self.assertRaisesRegex(ValueError,"counts_invalid"):
            safe_scene_summary(rows,EXPECTED_BYTES)


if __name__ == "__main__":
    unittest.main()
