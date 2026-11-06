"""Source-free negative/positive gates for exact 473-scene script subset."""
import unittest
from scripts.t2_original_scene_managed_subset import (
    exact_private_referenced_targets, select_class_records_by_exact_pathid,
)
from scripts.t2_original_monoscript_managed_class_bridge import (
    type_catalog, classify_script_metadata,
)


def item(path):
    return dict(path=path, bytes=758412, sha256="a"*64, kind="plain")


class OriginalSceneSubsetTests(unittest.TestCase):
    def test_exact_external_owner_and_distinct_ids(self):
        x = exact_private_referenced_targets(
            [("archive:/x/source.assets", 11), ("archive:/x/source.assets", 11),
             ("archive:/x/source.assets", 23)],
            [item("Raft_Data/source.assets")], "Raft_Data/source.assets")
        self.assertEqual(x, {11, 23})

    def test_ambiguous_filename_not_accepted(self):
        with self.assertRaises(ValueError):
            exact_private_referenced_targets(
                [("archive:/a/a.assets", 2)],
                [item("Raft_Data/a.assets"), item("Other/a.assets")],
                "Raft_Data/a.assets")

    def test_foreign_owner_rejected(self):
        with self.assertRaises(ValueError):
            exact_private_referenced_targets(
                [("archive:/x/other.assets", 2)],
                [item("Raft_Data/one.assets"), item("Other/other.assets")],
                "Raft_Data/one.assets")

    def test_manifest_missing_rejected(self):
        with self.assertRaises(ValueError):
            exact_private_referenced_targets(
                [("archive:/x/missing.assets", 2)],
                [item("Raft_Data/a.assets")], "Raft_Data/a.assets")

    def test_bad_pid_types_fail_closed(self):
        for pid in (0, -1, True, False, "1", 1.0, None):
            with self.subTest(pid=pid), self.assertRaises(ValueError):
                exact_private_referenced_targets(
                    [("archive:/x/a.assets", pid)], [item("Raft_Data/a.assets")],
                    "Raft_Data/a.assets")

    def test_malformed_reference_rows_rejected(self):
        for val in (None, [], [12], [("a",)], [(True, 1)]):
            with self.subTest(val=str(val)), self.assertRaises(ValueError):
                exact_private_referenced_targets(val, [item("Raft_Data/a.assets")],
                                                 "Raft_Data/a.assets")

    def test_selection_excludes_other_assembly_unreferenced(self):
        records = {1: ("Assembly-CSharp.dll", "Water", "One"),
                   2: ("Assembly-CSharp.dll", "Water", "Two"),
                   3: ("Other.dll", "", "Unused")}
        selected = select_class_records_by_exact_pathid({1, 2}, records)
        r = classify_script_metadata(selected, type_catalog([
            ("Water", "One"), ("Water", "Two")]))
        self.assertEqual(len(selected), 2)
        self.assertEqual(r["original_MonoScript_Assembly_CSharp_unique_TypeDef"], 2)

    def test_missing_typed_script_is_not_silent(self):
        with self.assertRaises(ValueError):
            select_class_records_by_exact_pathid({1, 7},
                                                 {1: ("Assembly-CSharp.dll", "", "A")})

    def test_opaque_metadata_explicitly_unknown(self):
        self.assertEqual(select_class_records_by_exact_pathid({3}, {3: None}), [None])

    def test_unreferenced_owner_metadata_not_implicitly_selected(self):
        selected = select_class_records_by_exact_pathid(
            {3}, {3: ("Assembly-CSharp.dll", "", "A"),
                  4: ("Assembly-CSharp.dll", "", "B")})
        self.assertEqual(len(selected), 1)

    def test_invalid_selected_pathid_fails(self):
        with self.assertRaises(ValueError):
            select_class_records_by_exact_pathid({True}, {True: None})

    def test_empty_selected_set_fails(self):
        with self.assertRaises(ValueError):
            select_class_records_by_exact_pathid(set(), {})

    def test_repeated_source_rows_count_once(self):
        ids = exact_private_referenced_targets(
            [("archive:/a/a.assets", 3)]*100,
            [item("Raft_Data/a.assets")], "Raft_Data/a.assets")
        self.assertEqual(ids, {3})

    def test_exact_class_name_not_casefolded(self):
        chosen = select_class_records_by_exact_pathid(
            {4}, {4: ("Assembly-CSharp.dll", "Game", "a")})
        r = classify_script_metadata(chosen, type_catalog([("Game", "A")]))
        self.assertEqual(r["original_MonoScript_Assembly_CSharp_missing_TypeDef"], 1)

    def test_duplicate_TypeDef_stays_ambiguous(self):
        chosen = select_class_records_by_exact_pathid(
            {4}, {4: ("Assembly-CSharp.dll", "Game", "A")})
        r = classify_script_metadata(chosen, type_catalog([
            ("Game", "A"), ("Game", "A")]))
        self.assertEqual(r["original_MonoScript_Assembly_CSharp_ambiguous_TypeDef"], 1)


if __name__ == "__main__":
    unittest.main()
