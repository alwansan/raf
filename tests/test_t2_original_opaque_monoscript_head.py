"""T2 source-free adversarial tests for exact original MonoBehaviour base m_Script PPtr."""
import unittest
from types import SimpleNamespace

from scripts.t2_original_opaque_monoscript_head import (
    EXPECTED_SCENES, EXPECTED_OPAQUE, EXPECTED_COMPONENTS, EXPECTED_PARSED,
    SOURCE_BYTES, MAX_HEADERS_CROSSCHECKED,
    script_header_ptr, source_owner_fileids,
    classify_opaque_script_links, aggregate_source_counts,
)


def header(f,p):
    return SimpleNamespace(m_Script=SimpleNamespace(m_FileID=f,m_PathID=p))


def row0():
    return classify_opaque_script_links(set(),[],set(),set())


class HeaderSourceProofTests(unittest.TestCase):
    def test_typed_script_fileid_pathid(self):
        self.assertEqual(script_header_ptr(header(1,2420)),(1,2420))

    def test_zero_script_pointer_valid_and_separate(self):
        self.assertEqual(script_header_ptr(header(0,0)),(0,0))

    def test_bools_or_missing_fields_do_not_count_as_original_header(self):
        for x in [header(True,2),header(1,False),
                  SimpleNamespace(m_Script=None),
                  SimpleNamespace(m_Script=SimpleNamespace(m_FileID=1)),
                  header(-1,2),header(1,-1)]:
            with self.subTest(which=str(x)[:80]),self.assertRaises(ValueError):
                script_header_ptr(x)

    def test_unique_original_owner_fileid_via_basename(self):
        ids=source_owner_fileids([
            "archive:/Raft_Data/sharedassets0.assets",
            "archive:/another.assets",
            r"archive:\Raft_Data\SHAREDASSETS0.ASSETS",
        ])
        self.assertEqual(ids,{1,3})

    def test_non_target_owner_is_not_original_Foam_source(self):
        self.assertEqual(source_owner_fileids(["sharedassets1.assets"]),set())

    def test_corrupt_original_external_name_rejected(self):
        for val in ["",None,"a\x00b","x"*1025]:
            with self.subTest(type=str(type(val))),self.assertRaises(ValueError):
                source_owner_fileids([val])


class OriginalScriptTargetCategoryTests(unittest.TestCase):
    def test_recover_typed_monoscipt_through_external_owner(self):
        x=classify_opaque_script_links(
            {1},[(1,500,2),(1,500,2),(1,501,2)],{500},{})
        self.assertEqual(x["opaque_MonoBehaviour_header_parsed"],3)
        self.assertEqual(x["opaque_MonoBehaviour_script_to_external_owner"],3)
        self.assertEqual(x["opaque_MonoBehaviour_script_to_external_typed_MonoScript"],2)
        self.assertEqual(x["opaque_MonoBehaviour_script_to_external_not_typed_MonoScript"],1)
        self.assertEqual(x["opaque_MonoBehaviour_distinct_external_typed_script_targets"],1)

    def test_do_not_elevate_local_same_pathid_to_original_owner(self):
        x=classify_opaque_script_links({1},[(0,500,2)],{500},set())
        self.assertEqual(x["opaque_MonoBehaviour_script_to_local_not_typed_MonoScript"],1)
        self.assertEqual(x["opaque_MonoBehaviour_script_to_external_owner"],0)

    def test_local_script_type_validated_separately(self):
        x=classify_opaque_script_links(set(),[(0,5,0)],set(),{5})
        self.assertEqual(x["opaque_MonoBehaviour_script_to_local_typed_MonoScript"],1)

    def test_other_external_is_not_original_foam_owner(self):
        x=classify_opaque_script_links({2},[(1,50,2)],{50},set())
        self.assertEqual(x["opaque_MonoBehaviour_script_to_other_external_owner"],1)

    def test_opaque_and_null_are_not_false_negative(self):
        x=classify_opaque_script_links(set(),[None,(0,0,0)],set(),set())
        self.assertEqual(x["opaque_MonoBehaviour_header_unparsed"],1)
        self.assertEqual(x["opaque_MonoBehaviour_header_null_script"],1)

    def test_invalid_external_fileid_counted_without_deref(self):
        x=classify_opaque_script_links({2},[(5,50,2)],{50},set())
        self.assertEqual(x["opaque_MonoBehaviour_script_invalid_external_fileID"],1)
        self.assertEqual(x["opaque_MonoBehaviour_script_to_external_owner"],0)

    def test_only_exact_int_fileid_and_script_id(self):
        for r in [[(True,2,3)],[(1,True,3)],[(1,2,False)],
                  [(-1,2,3)],[(1,-2,3)],[(1,2,-3)],[(1,2)]]:
            with self.subTest(r=str(r)), self.assertRaises(ValueError):
                classify_opaque_script_links({1},r,{2},set())

    def test_typed_source_script_id_must_be_positive_int(self):
        for ids in [{0},{True},{"22"}]:
            with self.subTest(ids=ids),self.assertRaises(ValueError):
                classify_opaque_script_links(set(),[],ids,set())

    def test_same_source_target_multiple_scene_components_not_unique_global(self):
        rows=[row0() for _ in range(EXPECTED_SCENES)]
        rows[0]=classify_opaque_script_links({1},[(1,42,1)],{42},set())
        rows[1]=classify_opaque_script_links({1},[(1,42,1)],{42},set())
        s=aggregate_source_counts(rows,EXPECTED_COMPONENTS,EXPECTED_PARSED,
                                  EXPECTED_OPAQUE-2,SOURCE_BYTES,1,0)
        self.assertEqual(s["sum_per_scene_distinct_external_typed_script_targets"],2)
        self.assertNotIn("opaque_MonoBehaviour_distinct_external_typed_script_targets",s)
        self.assertFalse(s["script_PPtr_is_original_Foam_Shader_runtime_identity_proven"])
        self.assertFalse(s["opaque_custom_fields_recovered"])
        self.assertFalse(s["Android_Adreno_water_pixels_verified"])

    def test_source_coverage_baseline_failure_on_opaque_gap(self):
        rows=[row0() for _ in range(EXPECTED_SCENES)]
        with self.assertRaisesRegex(ValueError,"coverage_incomplete"):
            aggregate_source_counts(rows,EXPECTED_COMPONENTS,EXPECTED_PARSED,
                                    EXPECTED_OPAQUE-1,SOURCE_BYTES,0,0)

    def test_source_sha_staged_total_must_match(self):
        rows=[row0() for _ in range(EXPECTED_SCENES)]
        with self.assertRaisesRegex(ValueError,"baseline_or_sha_drift"):
            aggregate_source_counts(rows,EXPECTED_COMPONENTS,EXPECTED_PARSED,
                                    EXPECTED_OPAQUE,SOURCE_BYTES-1,0,0)

    def test_scene_count_must_be_exact(self):
        rows=[row0() for _ in range(EXPECTED_SCENES-1)]
        with self.assertRaisesRegex(ValueError,"baseline_or_sha_drift"):
            aggregate_source_counts(rows,EXPECTED_COMPONENTS,EXPECTED_PARSED,
                                    EXPECTED_OPAQUE,SOURCE_BYTES,0,0)

    def test_crosscheck_guard_bounded(self):
        rows=[row0() for _ in range(EXPECTED_SCENES)]
        with self.assertRaisesRegex(ValueError,"baseline_or_sha_drift"):
            aggregate_source_counts(rows,EXPECTED_COMPONENTS,EXPECTED_PARSED,
                                    EXPECTED_OPAQUE,SOURCE_BYTES,0,
                                    MAX_HEADERS_CROSSCHECKED+1)

if __name__=="__main__":
    unittest.main()
