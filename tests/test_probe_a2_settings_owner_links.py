"""Synthetic-only Settings controller PPtr and native Canvas ancestry tests."""
import struct
import tempfile
from pathlib import Path
import unittest
from scripts.probe_a2_settings_owner_links import (
    SETTINGS_SHA, MAX_MATCHES, scan_candidates, native_graph,
    ancestry, audit_scene, source_pin,
)

class O:
    def __init__(self, kind, pid, tree=None, data=b""):
        self.type = type("Type", (), {"name": kind})()
        self.path_id, self.tree, self.data = pid, tree or {}, data
    def read_typetree(self, **kwargs):
        return self.tree
    def get_raw_data(self):
        return self.data

class File:
    def __init__(self, objects):
        self.objects = {o.path_id: o for o in objects}
        self.externals = [type("External", (), {"path": "globalgamemanagers.assets"})()]

def pptr(fid, pid):
    return {"m_FileID": fid, "m_PathID": pid}

def sample():
    header = (struct.pack("<iq", 0, 3) + b"\x01\x00\x00\x00"
              + struct.pack("<iq", 1, 21) + struct.pack("<i", 0))
    return File([
        O("GameObject", 2), O("GameObject", 3), O("GameObject", 8),
        O("RectTransform", 9, {"m_GameObject": pptr(0, 8), "m_Father": pptr(0, 10)}),
        O("RectTransform", 10, {"m_GameObject": pptr(0, 2), "m_Father": pptr(0, 0)}),
        O("Canvas", 11, {"m_GameObject": pptr(0, 2)}),
        O("MonoBehaviour", 12, {"m_GameObject": pptr(0, 2), "m_Script": pptr(1, 22)}),
        O("MonoBehaviour", 13, {"m_GameObject": pptr(0, 3), "m_Script": pptr(1, 21)},
          header + struct.pack("<iq", 0, 8)),
    ])

REGISTRY = {21: "matching_original_game_class_unverified_Settings",
            22: "verified_unity_ui_canvas_scaler"}

class A2OwnerLinks(unittest.TestCase):
    def test_candidate_aligned_and_not_base_header(self):
        raw = b"\0" * 32 + struct.pack("<iq", 0, 9)
        self.assertEqual(scan_candidates(raw, {9}), [(32, 9)])
        self.assertEqual(scan_candidates(raw, {10}), [])
        self.assertEqual(scan_candidates(b"\0" * 32 + b"X" + struct.pack("<iq", 0, 9), {9}), [])

    def test_candidate_ancestor_is_native_canvas_scaler(self):
        s = sample()
        graph = native_graph(list(s.objects.values()), [e.path for e in s.externals], {}, REGISTRY)
        self.assertEqual(ancestry(8, graph), "candidate_with_verified_scaler_ancestor")
        self.assertEqual(ancestry(9, graph), "candidate_with_verified_scaler_ancestor")
        self.assertEqual(ancestry(3, graph), "target_transform_missing")

    def test_settings_owner_raw_link_is_only_candidate(self):
        result = audit_scene(sample(), REGISTRY)
        self.assertEqual(result["settings_owner_count"], 1)
        self.assertEqual(result["raw_local_pptr_candidate_count"], 1)
        self.assertEqual(result["candidate_target_types"]["GameObject"], 1)
        self.assertEqual(result["authentic_scaler_canvas_owners"], 1)
        self.assertFalse(result["candidate_custom_field_typing_verified"])
        self.assertFalse(result["displayed_settings_panel_to_canvas_proven"])

    def test_mismatch_or_foreign_script_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "one original Settings"):
            audit_scene(sample(), {22: REGISTRY[22], 21: "unrelated"})
        s = sample()
        s.objects[13].tree["m_GameObject"] = pptr(0, 4)
        with self.assertRaisesRegex(ValueError, "base PPtr mismatch"):
            audit_scene(s, REGISTRY)

    def test_cycle_external_parent_and_missing_are_unknown(self):
        s = sample()
        for new_parent in (pptr(0, 999), pptr(0, 9), pptr(1, 10)):
            s.objects[9].tree["m_Father"] = new_parent
            graph = native_graph(list(s.objects.values()), ["globalgamemanagers.assets"], {}, REGISTRY)
            self.assertEqual(ancestry(8, graph), "unknown_ancestry")

    def test_unbounded_matches_and_truncated_records(self):
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            scan_candidates(b"\0" * 31, {7})
        raw = b"\0" * 32 + struct.pack("<iq", 0, 7) * (MAX_MATCHES + 1)
        with self.assertRaisesRegex(ValueError, "Unbounded"):
            scan_candidates(raw, {7})

    def test_source_sha_drift_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            src = root / "Settings.cs"
            src.write_text("class Settings {}")
            with self.assertRaisesRegex(ValueError, "SHA drift"):
                source_pin(root)
            src.unlink()
            with self.assertRaisesRegex(ValueError, "missing"):
                source_pin(root)
            self.assertEqual(len(SETTINGS_SHA), 64)


    def test_dense_48_pointer_stride_is_structural_not_typed_field(self):
        from scripts.probe_a2_settings_owner_links import strict_pointer_stride_shape
        body = b"".join(struct.pack("<iq", 0, 100+i) for i in range(48))
        raw = b"\0" * 32 + body + b"\x00\x00\x00\x00"
        candidates = scan_candidates(raw, {100+i for i in range(48)})
        data = strict_pointer_stride_shape(raw, candidates)
        self.assertTrue(data["exact_48_pointer_stride"])
        self.assertTrue(data["tail_is_bool_plus_zero_padding"])
        self.assertFalse(data["source_declared_field_names_mapped"])
        bad = strict_pointer_stride_shape(raw, candidates[:-1])
        self.assertFalse(bad["exact_48_pointer_stride"])
        replaced = raw[:-2] + b"\x01\x03"
        bad = strict_pointer_stride_shape(replaced, candidates)
        self.assertFalse(bad["tail_is_bool_plus_zero_padding"])



    def test_ambiguous_overlapping_pointer_windows_need_disjoint_bounds(self):
        from scripts.probe_a2_settings_owner_links import nonoverlap_profile
        candidates = [(32, 1), (40, 2), (52, 3), (64, 4)]
        profile = nonoverlap_profile(candidates, [True, False, True, True])
        self.assertEqual(profile["total_overlapping_raw_patterns"], 4)
        self.assertEqual(profile["maximum_disjoint_12byte_candidate_windows"], 3)
        self.assertEqual(profile["patterns_not_simultaneously_placeable"], 1)
        self.assertEqual(profile["minimum_verified_scaler_ancestor_hits_among_maximal_disjoint_sets"], 2)
        self.assertEqual(profile["maximum_verified_scaler_ancestor_hits_among_maximal_disjoint_sets"], 3)
        self.assertEqual(profile["candidate_windows_present_in_every_maximal_disjoint_set"], 2)
        self.assertTrue(profile["no_custom_serialized_field_types_inferred"])
        with self.assertRaisesRegex(ValueError, "Unpaired"):
            nonoverlap_profile(candidates, [True])

    def test_nonoverlap_single_and_empty_scenarios(self):
        from scripts.probe_a2_settings_owner_links import nonoverlap_profile
        self.assertEqual(nonoverlap_profile([], [])["maximum_disjoint_12byte_candidate_windows"], 0)
        one = nonoverlap_profile([(32, 1)], [True])
        self.assertEqual(one["maximum_disjoint_12byte_candidate_windows"], 1)
        self.assertEqual(one["candidate_windows_present_in_every_maximal_disjoint_set"], 1)


if __name__ == "__main__":
    unittest.main()
