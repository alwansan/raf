"""Synthetic-only tests for safe classification of real owner-world JSONL markers."""
import json
import tempfile
from pathlib import Path
import unittest

from scripts.t4_owner5nov_jsonl_lifecycle import analyze
from scripts.t4_verify_device_world_save_log import EvidenceInputError


def row(session, seq, area, op, utc, detail=""):
    return {"session": session, "sequence": seq, "utc": utc, "thread": 1,
            "area": area, "operation": op, "detail": detail}


class OwnerWorldLifecycleEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def put(self, name, records):
        path = self.root / name
        path.write_text("".join(json.dumps(r) + "\n" for r in records), encoding="utf-8")
        return path

    def test_original_world_save_then_later_load_but_not_proven_same_world(self):
        previous = [
            row("PRIVATE_ORIGINAL_SESSION", 1, "world", "WorldHasBeenLoaded.firstMoveNext",
                "2026-11-05T12:00:00Z"),
            row("PRIVATE_ORIGINAL_SESSION", 2, "save", "SaveGame.enter",
                "2026-11-05T12:00:01Z"),
            row("PRIVATE_ORIGINAL_SESSION", 3, "save", "SaveWorld.enter",
                "2026-11-05T12:00:02Z"),
            row("PRIVATE_ORIGINAL_SESSION", 4, "save", "Save.argumentFileSnapshot",
                "2026-11-05T12:00:03Z",
                "exists_at_filename_argument=True; length_class=nonzero; durable_RGD_unverified=true"),
            row("PRIVATE_ORIGINAL_SESSION", 5, "save", "SaveWorld.exit",
                "2026-11-05T12:00:04Z"),
            row("PRIVATE_ORIGINAL_SESSION", 6, "save", "SaveUser.enter",
                "2026-11-05T12:00:05Z"),
            row("PRIVATE_ORIGINAL_SESSION", 7, "save", "SaveUser.exit",
                "2026-11-05T12:00:06Z"),
            row("PRIVATE_ORIGINAL_SESSION", 8, "save", "SaveGame.exit",
                "2026-11-05T12:00:07Z"),
            row("PRIVATE_ORIGINAL_SESSION", 9, "world", "WorldHasBeenLoaded.originalCompletionAssigned",
                "2026-11-05T12:00:08Z"),
        ]
        next_session = [
            row("PRIVATE_REOPEN_SESSION", 1, "save", "Load<T>.enter",
                "2026-11-05T13:00:00Z"),
            row("PRIVATE_REOPEN_SESSION", 2, "save", "Load.argumentFileSnapshot",
                "2026-11-05T13:00:01Z",
                "exists_at_filename_argument=True; length_class=nonzero; readback_and_deserialization_unverified=true"),
            row("PRIVATE_REOPEN_SESSION", 3, "save", "Load<T>.exit",
                "2026-11-05T13:00:02Z"),
            row("PRIVATE_REOPEN_SESSION", 4, "save", "RestoreRGDGame.enter",
                "2026-11-05T13:00:03Z"),
            row("PRIVATE_REOPEN_SESSION", 5, "save", "RestoreRGDGame.exit",
                "2026-11-05T13:00:04Z"),
        ]
        first = self.put("first.jsonl", previous)
        second = self.put("second.jsonl", next_session)
        summary = analyze([first, second])
        self.assertTrue(summary["save_nonzero_in_earlier_session_hint"])
        self.assertTrue(summary["load_nonzero_in_later_session_hint"])
        self.assertEqual(summary["session_count"], 2)
        self.assertTrue(summary["sessions"][0]["original_stage_order_hints"][
            "iterator_first_move_next_before_world_ready_assignment"])
        self.assertTrue(summary["sessions"][1]["original_stage_order_hints"][
            "restore_world_enter_before_restore_world_exit"])
        self.assertEqual(summary["sessions"][0]["save_nonzero_file_snapshots"], 1)
        self.assertEqual(summary["sessions"][1]["load_nonzero_file_snapshots"], 1)
        for proof in ("same_world_proven", "process_restart_proven",
                      "original_rgd_deserialization_success_proven", "durable_rgd_reopen_proven",
                      "current_android_device_acceptance_proven", "raw_owner_data_published"):
            self.assertFalse(summary[proof])
        rendered = json.dumps(summary)
        self.assertNotIn("PRIVATE_", rendered)
        self.assertNotIn(str(self.root), rendered)
        self.assertNotIn("durable_RGD_unverified", rendered)

    def test_duplicate_startup_segment_is_counted_once(self):
        event = row("synthetic", 1, "save", "SaveGame.enter", "2026-11-05T12:00:00Z")
        one = self.put("first.jsonl", [event])
        two = self.put("second.jsonl", [event])
        result = analyze([one, two])
        self.assertEqual(result["session_count"], 1)
        self.assertEqual(result["sessions"][0]["original_operation_counts"]["savegame_enter"], 1)
        self.assertFalse(result["save_nonzero_in_earlier_session_hint"])

    def test_true_queue_overflow_suppresses_cross_session_hint(self):
        first = self.put("first.jsonl", [
            row("a", 1, "save", "Save.argumentFileSnapshot",
                "2026-11-05T10:00:00Z",
                "exists_at_filename_argument=True; length_class=nonzero"),
            {"area": "logging", "operation": "queue_overflow", "dropped": 4},
        ])
        second = self.put("second.jsonl", [
            row("b", 1, "save", "Load.argumentFileSnapshot",
                "2026-11-05T11:00:00Z",
                "exists_at_filename_argument=True; length_class=nonzero"),
        ])
        result = analyze([first, second])
        self.assertTrue(result["logging_queue_overflow_observed"])
        self.assertFalse(result["save_nonzero_in_earlier_session_hint"])
        self.assertFalse(result["load_nonzero_in_later_session_hint"])

    def test_log_sequence_gap_is_not_full_device_evidence(self):
        source = self.put("gap.jsonl", [
            row("gap", 1, "save", "SaveGame.enter", "2026-11-05T11:00:00Z"),
            row("gap", 3, "save", "SaveGame.exit", "2026-11-05T11:00:02Z"),
        ])
        result = analyze([source])
        self.assertTrue(result["sessions"][0]["queue_or_sequence_warning"])
        self.assertFalse(result["sessions"][0]["complete_sequence"])
        self.assertFalse(result["current_android_device_acceptance_proven"])

    def test_conflicting_duplicate_sequences_fail_closed(self):
        first = self.put("first.jsonl", [
            row("s", 1, "save", "SaveWorld.enter", "2026-11-05T10:00:00Z")])
        second = self.put("second.jsonl", [
            row("s", 1, "save", "SaveUser.enter", "2026-11-05T10:00:00Z")])
        with self.assertRaisesRegex(EvidenceInputError, "conflicting_replayed_sequence"):
            analyze([first, second])

    def test_wrong_immutable_three_log_provenance_refused(self):
        path = self.put("first.jsonl", [
            row("x", 1, "startup", "logger.ready", "2026-11-05T10:00:00Z")])
        with self.assertRaisesRegex(EvidenceInputError, "unverified_pinned_owner_log_bytes"):
            analyze([path], pinned=True)

    def test_reject_unknown_extra_log_file_in_owner_experiment(self):
        paths = [self.put(str(i) + ".jsonl", [
            row(str(i), 1, "startup", "logger.ready", "2026-11-05T10:00:00Z")
        ]) for i in range(4)]
        with self.assertRaisesRegex(EvidenceInputError, "invalid_owner_log_files"):
            analyze(paths)


if __name__ == "__main__":
    unittest.main()
