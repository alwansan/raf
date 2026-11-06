"""T2 source-free controls for actual ZIP2 original MonoScript target file join."""
import unittest

from scripts.t2_original_monoscript_target_join import (
    match_private_external_to_original_manifest,
    typecheck_typed_MonoScript_target_ids,
    validated_safe_classification,
    choose_bounded_SHA_original_targets,
    MAX_TARGET_BYTES,
)
from scripts.t2_original_opaque_monoscript_head import EXPECTED_OPAQUE


def item(path,bytes_=1024):
    return dict(path=path, bytes=bytes_,sha256="a"*64,kind="plain")


def refs(path="archive:/Raft_Data/scriptfile.assets",pid=73):
    return [(path,pid) for _ in range(EXPECTED_OPAQUE)]


class OriginalFileIdentifierTargetTests(unittest.TestCase):
    def test_casefold_original_manifest_unique_candidate_only(self):
        typ,p=match_private_external_to_original_manifest(
            "archive:/Raft_Data/SCRIPTFILE.ASSETS",
            [item("Raft_Data/scriptfile.assets"),item("Raft_Data/other.assets")])
        self.assertEqual(typ,"unique")
        self.assertEqual(p["bytes"],1024)

    def test_unknown_original_provider_is_not_corrupt(self):
        typ,p=match_private_external_to_original_manifest(
            "archive:/Raft_Data/absent.assets",
            [item("Raft_Data/scriptfile.assets")])
        self.assertEqual(typ,"missing")
        self.assertIsNone(p)

    def test_duplicate_basename_source_targets_are_ambiguous(self):
        typ,p=match_private_external_to_original_manifest(
            "archive:/Raft_Data/scriptfile.assets",
            [item("Raft_Data/scriptfile.assets"),item("Other/scriptfile.assets")])
        self.assertEqual(typ,"ambiguous")
        self.assertIsNone(p)

    def test_malformed_source_original_paths_rejected(self):
        for p in ("",None,"x\x00y","x"*1100,"archive:/.."):
            with self.subTest(p=str(p)[:12]),self.assertRaises(ValueError):
                match_private_external_to_original_manifest(p,[])

    def test_bad_original_manifest_candidate_format_rejected(self):
        for r in [dict(path="a.assets",bytes="100",sha256="a"*64,kind="plain"),
                  dict(path="a.assets",bytes=1,sha256="a"*10,kind="plain"),
                  dict(path="a.assets",bytes=1,sha256="a"*64,kind="wrong")]:
            with self.subTest(kind=r["kind"]),self.assertRaises(ValueError):
                match_private_external_to_original_manifest("a.assets",[r])

    def test_typed_actual_MonoScript_PathID_proof(self):
        r=typecheck_typed_MonoScript_target_ids([3,3,9,10],{3,11})
        self.assertEqual(r["script_refs_to_SHA_original_typed_MonoScript_objects"],2)
        self.assertEqual(r["script_refs_to_SHA_original_absent_or_other_type_PathIDs"],2)
        self.assertEqual(r["distinct_referenced_typed_MonoScript_objects"],1)
        self.assertEqual(r["distinct_referenced_non_MonoScript_PathIDs"],2)

    def test_empty_MonoScript_set_is_unresolved_not_Foam_corrupt(self):
        r=typecheck_typed_MonoScript_target_ids([22],set())
        self.assertEqual(r["script_refs_to_SHA_original_typed_MonoScript_objects"],0)
        self.assertEqual(r["script_refs_to_SHA_original_absent_or_other_type_PathIDs"],1)

    def test_bad_or_boolean_path_id_fails_closed(self):
        for ids in [[True],[0],[-1],["1"]]:
            with self.subTest(ids=ids),self.assertRaises(ValueError):
                typecheck_typed_MonoScript_target_ids(ids,{1})

    def test_source_reference_cardinality_exact_and_safe(self):
        original=[item("Raft_Data/scriptfile.assets")]
        cats,grouped=validated_safe_classification(refs(),original)
        self.assertEqual(cats["original_unique_basename_candidate_ref_rows"],55328)
        self.assertEqual(cats["original_unique_manifest_candidate_target_files"],1)
        self.assertEqual(len(grouped),1)
        self.assertEqual(len(next(iter(grouped.values()))),55328)

    def test_all_manifest_missing_counted_not_classified_typed(self):
        cats,grouped=validated_safe_classification(refs(),[])
        self.assertEqual(cats["original_missing_manifest_candidate_ref_rows"],55328)
        self.assertEqual(grouped,{})

    def test_manifest_ambiguous_counted(self):
        original=[item("Raft_Data/scriptfile.assets"),
                  item("Other/scriptfile.assets")]
        cats,grouped=validated_safe_classification(refs(),original)
        self.assertEqual(cats["original_ambiguous_manifest_candidate_ref_rows"],55328)
        self.assertEqual(grouped,{})

    def test_original_cardinality_drift_refused(self):
        with self.assertRaisesRegex(ValueError,"count_drift"):
            validated_safe_classification([("x",1)],[])

    def test_untrusted_original_script_target_pathid_refused(self):
        r=refs()
        r[-1]=("a.assets",True)
        with self.assertRaisesRegex(ValueError,"row_invalid"):
            validated_safe_classification(r,[item("a.assets")])

    def test_SHA_target_budget_accepted_for_sufficient_manifest(self):
        r={"Raft_Data/scriptfile.assets":[1,2,3]}
        manifest=[item("Raft_Data/scriptfile.assets",1024)]
        staged,skipped,used=choose_bounded_SHA_original_targets(r,manifest)
        self.assertEqual((len(staged),skipped,used),(1,0,1024))

    def test_SHA_target_over_budget_remains_skipped(self):
        r={"Raft_Data/huge.assets":[1,2,3]}
        manifest=[item("Raft_Data/huge.assets",MAX_TARGET_BYTES+1)]
        staged,skipped,used=choose_bounded_SHA_original_targets(r,manifest)
        self.assertEqual((staged,skipped,used),({},3,0))

    def test_target_selected_by_manifest_path_not_fake_basename(self):
        with self.assertRaisesRegex(ValueError,"not_authenticated"):
            choose_bounded_SHA_original_targets(
                {"Raft_Data/fake.assets":[1]},[item("Raft_Data/authentic.assets")])

if __name__=="__main__":
    unittest.main()
