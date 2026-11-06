"""Source-free negative controls for Android JSONL evidence classification."""
import json
import tempfile
import unittest
from pathlib import Path
from scripts.t4_verify_device_world_save_log import EvidenceInputError, summarize, _paths

def row(session, seq, area, operation, detail="", utc=None):
    return {"session": session, "sequence": seq, "utc": utc or "2026-11-05T13:00:00.0000000Z",
            "thread": 1, "area": area, "operation": operation, "detail": detail}

class DeviceWorldSaveLogTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def put(self, name, events):
        p = self.root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("".join(json.dumps(e) + "\n" for e in events), encoding="utf-8")
        return p

    def test_mouse_release_outcomes_are_static_and_never_prove_android_os_state(self):
        outcomes = (
            "superseded_generation", "unbound_request_view",
            "focus_view_unavailable", "focused_view_changed",
            "target_not_captured", "release_call_returned",
            "jni_exception", "ui_dispatch_exception",
        )
        events = [
            row("test-s1", 1, "input", "physical_mouse_capture_requested"),
            row("test-s1", 2, "input", "physical_mouse_capture_released"),
        ]
        events += [
            row("test-s1", i + 3, "input",
                "physical_mouse_capture_release_outcome",
                "result=" + status + "; native_release_confirmed=false")
            for i, status in enumerate(outcomes)
        ]
        self.put("mouse.jsonl", events)
        result = summarize(_paths(self.root))
        entry = result["sessions"][0]
        self.assertEqual(entry["marker_counts"]["mouse_release_requested"], 1)
        self.assertEqual(entry["marker_counts"]["mouse_capture_requested"], 1)
        self.assertEqual(entry["marker_counts"]["mouse_release_outcome"], 8)
        self.assertEqual(entry["mouse_release_outcome_classes"],
                         {name: 1 for name in outcomes})
        self.assertTrue(entry["native_release_call_returned_observed"])
        self.assertFalse(entry["native_mouse_release_by_os_proven"])
        self.assertTrue(result["mouse_release_call_returned_observed"])
        self.assertFalse(result["native_mouse_release_by_os_proven"])
        self.assertFalse(result["hardware_mouse_360_camera_proven"])
        self.assertFalse(result["local005_device_confirmed"])

    def test_mouse_view_loss_relative_counts_cannot_claim_camera(self):
        self.put("mouse.jsonl", [
            row("s1", 1, "input", "physical_mouse_capture_view_changed"),
            row("s1", 2, "input", "physical_mouse_capture_lost"),
            row("s1", 3, "input", "physical_mouse_relative"),
        ])
        report = summarize(_paths(self.root))
        counts = report["sessions"][0]["marker_counts"]
        for label in ("mouse_view_changed", "mouse_capture_lost", "mouse_relative"):
            self.assertEqual(counts[label], 1)
        self.assertFalse(report["mouse_release_call_returned_observed"])
        self.assertFalse(report["hardware_mouse_360_camera_proven"])

    def test_forged_or_extra_mouse_release_detail_never_echoed_or_trusted(self):
        secret = "/storage/emulated/0/PrivateWorldOwner.rgd"
        details = [
            "result=release_call_returned; native_release_confirmed=true",
            "result=release_call_returned; native_release_confirmed=false; " + secret,
            "result=unknown_input; native_release_confirmed=false",
            "result=release_call_returned",
        ]
        self.put("mouse.jsonl", [
            row("SENSITIVE_SESSION_ID", i + 1, "input",
                "physical_mouse_capture_release_outcome", detail)
            for i, detail in enumerate(details)
        ])
        report = summarize(_paths(self.root))
        entry = report["sessions"][0]
        self.assertEqual(entry["mouse_release_outcome_classes"], {"unparseable": 4})
        self.assertIn("unparseable_mouse_release_outcome", entry["anomalies"])
        self.assertFalse(entry["native_release_call_returned_observed"])
        self.assertFalse(report["native_mouse_release_by_os_proven"])
        rendered = json.dumps(report)
        self.assertNotIn(secret, rendered)
        self.assertNotIn("SENSITIVE_SESSION_ID", rendered)
        self.assertNotIn("native_release_confirmed=true", rendered)

    def test_non_string_mouse_release_detail_is_rejected_not_partly_accepted(self):
        self.put("mouse.jsonl", [
            row("s1", 1, "input", "physical_mouse_capture_release_outcome",
                {"result": "release_call_returned"}),
        ])
        with self.assertRaisesRegex(EvidenceInputError, "invalid_mouse_release_detail_type"):
            summarize(_paths(self.root))

    def test_duplicate_source_log_does_not_double_count_release_outcome(self):
        events = [row("test-s1", 1, "input",
                      "physical_mouse_capture_release_outcome",
                      "result=target_not_captured; native_release_confirmed=false")]
        self.put("startup/startup-first.jsonl", events)
        self.put("raft-first.jsonl", events)
        result = summarize(_paths(self.root))
        self.assertEqual(result["sessions"][0]["deduplicated_replay_lines"], 1)
        self.assertEqual(result["sessions"][0]["mouse_release_outcome_classes"],
                         {"target_not_captured": 1})

    def test_single_session_never_claims_acceptance(self):
        self.put("raft-one.jsonl", [
            row("s1", 1, "startup", "logger.ready"),
            row("s1", 2, "world", "WorldHasBeenLoaded.firstMoveNext"),
            row("s1", 3, "world", "WorldHasBeenLoaded.originalCompletionAssigned"),
            row("s1", 4, "save", "Save.argumentFileSnapshot",
                "exists_at_filename_argument=True; length_class=nonzero; durable_RGD_unverified=true"),
        ])
        report = summarize(_paths(self.root))
        self.assertTrue(report["sessions"][0]["sequence_complete"])
        self.assertFalse(report["cross_session_same_world_proven"])
        self.assertFalse(report["local005_device_confirmed"])
        self.assertFalse(report["real_rgd_durability_or_reopen_proven"])

    def test_two_sessions_never_prove_same_world_or_process_restart(self):
        old = [row("a", 1, "save", "Save.argumentFileSnapshot",
                   "exists_at_filename_argument=True; length_class=nonzero")]
        new = [row("b", 1, "save", "Load<T>.enter", utc="2026-11-05T14:00:00Z"),
               row("b", 2, "save", "Load.argumentFileSnapshot",
                   "exists_at_filename_argument=True; length_class=nonzero",
                   utc="2026-11-05T14:00:01Z"),
               row("b", 3, "save", "Load<T>.exit", utc="2026-11-05T14:00:02Z")]
        self.put("segment-one.jsonl", old)
        self.put("segment-two.jsonl", new)
        report = summarize(_paths(self.root))
        self.assertTrue(report["save_nonzero_in_earlier_session"])
        self.assertTrue(report["load_nonzero_in_later_session"])
        self.assertFalse(report["process_restart_proven"])
        self.assertFalse(report["cross_session_same_world_proven"])
        self.assertFalse(report["local005_device_confirmed"])

    def test_duplicate_startup_copy_is_deduplicated(self):
        events = [row("x", 1, "startup", "logger.ready"),
                  row("x", 2, "save", "Load.caughtException")]
        self.put("startup/startup-synthetic.jsonl", events)
        self.put("raft-synthetic.jsonl", events)
        summary = summarize(_paths(self.root))
        self.assertEqual(summary["sessions"][0]["deduplicated_replay_lines"], 2)
        self.assertEqual(summary["sessions"][0]["marker_counts"]["load_caught"], 1)

    def test_conflicting_duplicate_rejected(self):
        self.put("one.jsonl", [row("x", 1, "save", "Load.caughtException")])
        self.put("two.jsonl", [row("x", 1, "save", "SaveWorld.enter")])
        with self.assertRaisesRegex(EvidenceInputError, "conflicting"):
            summarize(_paths(self.root))

    def test_missing_sequence_disables_completeness(self):
        self.put("loss.jsonl", [row("x", 1, "startup", "logger.ready"),
                                row("x", 3, "world", "WorldHasBeenLoaded.originalCompletionAssigned")])
        summary = summarize(_paths(self.root))
        self.assertFalse(summary["sessions"][0]["sequence_complete"])
        self.assertIn("missing_or_rotated_sequence", summary["sessions"][0]["anomalies"])

    def test_nonzero_plus_caught_does_not_establish_rgd(self):
        self.put("log.jsonl", [
            row("x", 1, "save", "Load<T>.enter"),
            row("x", 2, "save", "Load.caughtException"),
            row("x", 3, "save", "Load.argumentFileSnapshot",
                "exists_at_filename_argument=True; length_class=nonzero"),
        ])
        summary = summarize(_paths(self.root))
        self.assertEqual(summary["sessions"][0]["load_argument_file_classes"], {"nonzero": 1})
        self.assertFalse(summary["real_rgd_durability_or_reopen_proven"])

    def test_contradictory_snapshot_flagged(self):
        self.put("log.jsonl", [
            row("x", 1, "save", "Load.argumentFileSnapshot",
                "exists_at_filename_argument=False; length_class=nonzero"),
        ])
        summary = summarize(_paths(self.root))
        self.assertIn("unparseable_snapshot", summary["sessions"][0]["anomalies"])

    def test_unknown_log_detail_not_echoed(self):
        sensitive = "/storage/emulated/0/private-worldname.rgd"
        self.put("log.jsonl", [row("PRIVATE_SESSION_IDENTIFIER", 1,
                                    "save", "Load.caughtException", sensitive)])
        rendered = json.dumps(summarize(_paths(self.root)))
        self.assertNotIn(sensitive, rendered)
        self.assertNotIn("PRIVATE_SESSION_IDENTIFIER", rendered)
        self.assertNotIn(str(self.root), rendered)

    def test_invalid_json_rejected_not_partially_accepted(self):
        p = self.root / "bad.jsonl"
        p.write_text('{"session":')
        with self.assertRaisesRegex(EvidenceInputError, "invalid_jsonl"):
            summarize(_paths(self.root))

    def test_reject_linked_file(self):
        original = self.put("original.jsonl", [row("x", 1, "startup", "logger.ready")])
        (self.root / "alias.jsonl").symlink_to(original)
        with self.assertRaisesRegex(EvidenceInputError, "linked_or_invalid_file"):
            _paths(self.root)

    def test_assignment_before_iterator_is_anomaly_not_success(self):
        self.put("log.jsonl", [row("x", 1, "world", "WorldHasBeenLoaded.originalCompletionAssigned"),
                                row("x", 2, "world", "WorldHasBeenLoaded.firstMoveNext")])
        summary = summarize(_paths(self.root))
        self.assertIn("assignment_precedes_iterator", summary["sessions"][0]["anomalies"])
        self.assertFalse(summary["world_playability_proven"])

    def test_three_sessions_load_before_save_is_not_reordered_as_success(self):
        self.put("one.jsonl", [row("first", 1, "save", "Load.argumentFileSnapshot",
                                     "exists_at_filename_argument=True; length_class=nonzero",
                                     utc="2026-11-05T12:00:00Z")])
        self.put("two.jsonl", [row("second", 1, "save", "Save.argumentFileSnapshot",
                                     "exists_at_filename_argument=True; length_class=nonzero",
                                     utc="2026-11-05T13:00:00Z")])
        self.put("three.jsonl", [row("third", 1, "startup", "logger.ready",
                                       utc="2026-11-05T14:00:00Z")])
        result = summarize(_paths(self.root))
        self.assertFalse(result["save_nonzero_in_earlier_session"])
        self.assertFalse(result["load_nonzero_in_later_session"])
        self.assertFalse(result["local005_device_confirmed"])

    def test_overlapping_logger_sessions_are_not_a_restart_pair(self):
        self.put("one.jsonl", [
            row("first", 1, "save", "Save.argumentFileSnapshot",
                "exists_at_filename_argument=True; length_class=nonzero",
                utc="2026-11-05T12:00:00Z"),
            row("first", 2, "startup", "logger.ready",
                utc="2026-11-05T14:00:00Z")])
        self.put("two.jsonl", [
            row("second", 1, "save", "Load.argumentFileSnapshot",
                "exists_at_filename_argument=True; length_class=nonzero",
                utc="2026-11-05T13:00:00Z")])
        result = summarize(_paths(self.root))
        self.assertFalse(result["save_nonzero_in_earlier_session"])
        self.assertFalse(result["load_nonzero_in_later_session"])
        self.assertFalse(result["process_restart_proven"])


    def test_utc_rollback_disables_cross_session_hint(self):
        self.put("save.jsonl", [
            row("first", 1, "save", "Save.argumentFileSnapshot",
                "exists_at_filename_argument=True; length_class=nonzero",
                utc="2026-11-05T12:00:01Z"),
            row("first", 2, "startup", "logger.ready",
                utc="2026-11-05T12:00:00Z")])
        self.put("load.jsonl", [
            row("second", 1, "save", "Load.argumentFileSnapshot",
                "exists_at_filename_argument=True; length_class=nonzero",
                utc="2026-11-05T13:00:00Z")])
        result = summarize(_paths(self.root))
        self.assertIn("utc_reverses_sequence", result["sessions"][0]["anomalies"])
        self.assertFalse(result["sessions"][0]["utc_monotonic"])
        self.assertFalse(result["save_nonzero_in_earlier_session"])
        self.assertFalse(result["load_nonzero_in_later_session"])

    def test_monotonic_utc_allows_hint_but_not_device_acceptance(self):
        self.put("save.jsonl", [
            row("first", 1, "save", "Save.argumentFileSnapshot",
                "exists_at_filename_argument=True; length_class=nonzero",
                utc="2026-11-05T12:00:00Z"),
            row("first", 2, "startup", "logger.ready",
                utc="2026-11-05T12:00:01Z")])
        self.put("load.jsonl", [
            row("second", 1, "save", "Load.argumentFileSnapshot",
                "exists_at_filename_argument=True; length_class=nonzero",
                utc="2026-11-05T13:00:00Z")])
        result = summarize(_paths(self.root))
        self.assertTrue(result["sessions"][0]["utc_monotonic"])
        self.assertTrue(result["save_nonzero_in_earlier_session"])
        self.assertFalse(result["local005_device_confirmed"])

if __name__ == "__main__":
    unittest.main()
