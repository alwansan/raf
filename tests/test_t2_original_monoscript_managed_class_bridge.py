"""T2: non-proprietary negative controls for exact original MonoScript managed TypeDef join."""
import unittest
from collections import Counter

from scripts.t2_original_monoscript_managed_class_bridge import (
    classify_script_metadata, normalized_script_record, type_catalog,
    unique_original_source_rows, MONO_OWNER_BYTES, MANAGED_BYTES,
)


def row(path, size):
    return {"path": path, "bytes": size, "sha256": "a" * 64, "kind": "plain"}


def manifest():
    files = [
        row("Raft_Data/resource-owner.assets", MONO_OWNER_BYTES),
        row("Raft_Data/Managed/Assembly-CSharp.dll", MANAGED_BYTES),
    ]
    files.extend(row(f"Raft_Data/dummy-{i}.assets", i + 1) for i in range(364))
    return files


def raw(name="WaterComponent", ns="Game", asm="Assembly-CSharp.dll"):
    return {"m_ClassName": name, "m_Namespace": ns, "m_AssemblyName": asm}


class MonoManagedJoinTests(unittest.TestCase):
    def test_manifest_unique_small_source_files(self):
        a, b = unique_original_source_rows(manifest())
        self.assertEqual((a["bytes"], b["bytes"]), (MONO_OWNER_BYTES, MANAGED_BYTES))

    def test_manifest_duplicate_size_is_ambiguous_not_guessed(self):
        rows = manifest()
        rows[7]["bytes"] = MONO_OWNER_BYTES
        with self.assertRaises(ValueError):
            unique_original_source_rows(rows)

    def test_manifest_false_assembly_location_rejected(self):
        rows = manifest()
        rows[1]["path"] = "Other/Assembly-CSharp.dll"
        with self.assertRaises(ValueError):
            unique_original_source_rows(rows)

    def test_manifest_wrong_target_assembly_name_rejected(self):
        rows = manifest()
        rows[1]["path"] = "Raft_Data/Managed/SomeOther.dll"
        with self.assertRaises(ValueError):
            unique_original_source_rows(rows)

    def test_manifest_wrong_kind_rejected(self):
        rows = manifest()
        rows[0]["kind"] = "split"
        with self.assertRaises(ValueError):
            unique_original_source_rows(rows)

    def test_normalization_exact_class_and_namespace(self):
        self.assertEqual(normalized_script_record(raw()), ("Assembly-CSharp.dll", "Game", "WaterComponent"))

    def test_empty_namespace_allowed(self):
        self.assertEqual(normalized_script_record(raw(ns="")), ("Assembly-CSharp.dll", "", "WaterComponent"))

    def test_malformed_metadata_is_unknown(self):
        for value in [None, {}, raw(name=""), raw(name="A\x00B"), raw(asm=""), raw(ns="a\nb")]:
            with self.subTest(value=str(value)[:30]):
                self.assertIsNone(normalized_script_record(value))

    def test_managed_class_join_requires_exact_namespace(self):
        rows = type_catalog([("Game", "WaterComponent"), ("Other", "WaterComponent")])
        r = classify_script_metadata([("Assembly-CSharp.dll", "Game", "WaterComponent")], rows)
        self.assertEqual(r["original_MonoScript_Assembly_CSharp_unique_TypeDef"], 1)

    def test_namespace_mismatch_remains_missing(self):
        rows = type_catalog([("Other", "WaterComponent")])
        r = classify_script_metadata([("Assembly-CSharp.dll", "Game", "WaterComponent")], rows)
        self.assertEqual(r["original_MonoScript_Assembly_CSharp_missing_TypeDef"], 1)

    def test_exact_case_no_guess(self):
        rows = type_catalog([("Game", "WaterComponent")])
        r = classify_script_metadata([("Assembly-CSharp.dll", "Game", "watercomponent")], rows)
        self.assertEqual(r["original_MonoScript_Assembly_CSharp_missing_TypeDef"], 1)

    def test_duplicate_managed_types_ambiguous(self):
        rows = type_catalog([("Game", "WaterComponent"), ("Game", "WaterComponent")])
        r = classify_script_metadata([("Assembly-CSharp.dll", "Game", "WaterComponent")], rows)
        self.assertEqual(r["original_MonoScript_Assembly_CSharp_ambiguous_TypeDef"], 1)

    def test_other_assembly_not_treated_as_missing_Assembly_CSharp(self):
        rows = type_catalog([("Game", "WaterComponent")])
        r = classify_script_metadata([("UnityEngine.dll", "Game", "WaterComponent")], rows)
        self.assertEqual(r["original_MonoScript_other_assembly"], 1)
        self.assertEqual(r["original_MonoScript_Assembly_CSharp_missing_TypeDef"], 0)

    def test_empty_and_unknown_metadata_explicit(self):
        rows = type_catalog([("Game", "WaterComponent")])
        r = classify_script_metadata([None, ("Assembly-CSharp", "Game", "WaterComponent")], rows)
        self.assertEqual(r["original_MonoScript_class_metadata_unreadable"], 1)
        self.assertEqual(r["original_MonoScript_Assembly_CSharp_unique_TypeDef"], 1)

    def test_mixed_source_partition_exact(self):
        rows = type_catalog([("Game", "WaterComponent"), ("Game", "WaterComponent"), ("", "OtherScript")])
        r = classify_script_metadata([None, ("Foo.dll", "", "OtherScript"),
            ("Assembly-CSharp.dll", "Game", "WaterComponent"),
            ("Assembly-CSharp.dll", "", "OtherScript"),
            ("Assembly-CSharp.dll", "", "Missing")], rows)
        self.assertEqual(r["original_typed_MonoScript_objects_total"], 5)
        self.assertEqual(r["original_MonoScript_Assembly_CSharp_candidate"], 3)
        self.assertEqual(r["original_MonoScript_Assembly_CSharp_ambiguous_TypeDef"], 1)
        self.assertEqual(r["original_MonoScript_Assembly_CSharp_unique_TypeDef"], 1)
        self.assertEqual(r["original_MonoScript_Assembly_CSharp_missing_TypeDef"], 1)

    def test_empty_managed_type_table_rejected(self):
        with self.assertRaises(ValueError):
            type_catalog([])

    def test_malformed_typedef_rows_rejected(self):
        for item in [(None, "T"), ("Good", ""), ("Good", True)]:
            with self.subTest(item=item), self.assertRaises(ValueError):
                type_catalog([item])

    def test_unbounded_script_rows_rejected(self):
        with self.assertRaises(ValueError):
            classify_script_metadata([], Counter())


if __name__ == "__main__":
    unittest.main()
