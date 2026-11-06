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

    def _savegame_cycle(self, swapped=False, user_snapshot=True,
                        repeated_world_snapshot=False, unchecked_extra_save=False,
                        fault=None):
        # An original SaveGame event-count parity is not evidence of authored
        # SaveWorld -> SaveUser order: each completed phase must have its own
        # nonzero Save.argumentFileSnapshot before reporting a full cycle.
        order = ["SaveUser", "SaveWorld"] if swapped else ["SaveWorld", "SaveUser"]
        events = [("SaveGame.enter", "")]
        for phase in order:
            events.append((phase + ".enter", ""))
            if phase == "SaveWorld" and unchecked_extra_save:
                # An unrelated Save() exit cannot borrow a later Save() snapshot.
                events.extend([("Save.enter", ""), ("Save.exit", "")])
            events.append(("Save.enter", ""))
            if phase == "SaveWorld" or user_snapshot:
                events.append(("Save.argumentFileSnapshot",
                               "exists_at_filename_argument=True; length_class=nonzero; durable_RGD_unverified=true"))
                if phase == "SaveWorld" and repeated_world_snapshot:
                    # Equal SaveGame/phase counts do not guarantee per-call trace integrity.
                    events.append(("Save.argumentFileSnapshot",
                                   "exists_at_filename_argument=True; length_class=nonzero; durable_RGD_unverified=true"))
            if phase == "SaveWorld" and fault == "Save.argumentFileSnapshot.unavailable":
                events.append(("Save.argumentFileSnapshot.unavailable", "probe_error_type=IOException"))
            if phase == "SaveWorld" and fault == "Save.exception":
                events.append(("Save.exception", "synthetic private exception"))
            events.append(("Save.exit",
                           "exceptionEscaped=True; elapsed_ms=0.000"
                           if phase == "SaveWorld" and fault == "Save.exit.escaped"
                           else "exceptionEscaped=False; elapsed_ms=0.000"))
            if phase == "SaveWorld" and fault == "SaveWorld.exception":
                events.append(("SaveWorld.exception", "synthetic private exception"))
            events.append((phase + ".exit",
                           "exceptionEscaped=True; elapsed_ms=0.000"
                           if phase == "SaveWorld" and fault == "SaveWorld.exit.escaped"
                           else "exceptionEscaped=False; elapsed_ms=0.000"))
        if fault == "SaveGame.exception":
            events.append(("SaveGame.exception", "synthetic private exception"))
        events.append(("SaveGame.exit",
                       "exceptionEscaped=True; elapsed_ms=0.000"
                       if fault == "SaveGame.exit.escaped"
                       else "exceptionEscaped=False; elapsed_ms=0.000"))
        return self.put("savegame.jsonl", [
            row("original-synthetic", seq, "save", op,
                "2026-11-05T12:00:%02dZ" % seq, detail)
            for seq, (op, detail) in enumerate(events, start=1)
        ])

    def test_one_full_original_world_then_user_save_cycle_requires_two_snapshots(self):
        result = analyze([self._savegame_cycle()])
        stage = result["sessions"][0]
        self.assertEqual(stage["fully_traced_original_savegame_cycles"], 1)
        self.assertEqual(stage["incomplete_or_misordered_savegame_cycles"], 0)
        self.assertTrue(stage["all_savegame_cycles_have_ordered_world_and_user_snapshots"])
        self.assertFalse(result["durable_rgd_reopen_proven"])

    def test_equal_marker_counts_with_saveuser_before_saveworld_are_not_complete(self):
        stage = analyze([self._savegame_cycle(swapped=True)])["sessions"][0]
        self.assertEqual(stage["original_operation_counts"]["savegame_enter"], 1)
        self.assertEqual(stage["original_operation_counts"]["saveworld_exit"], 1)
        self.assertEqual(stage["original_operation_counts"]["saveuser_exit"], 1)
        self.assertEqual(stage["fully_traced_original_savegame_cycles"], 0)
        self.assertGreater(stage["incomplete_or_misordered_savegame_cycles"], 0)
        self.assertFalse(stage["all_savegame_cycles_have_ordered_world_and_user_snapshots"])

    def test_world_user_call_counts_without_user_snapshot_are_incomplete(self):
        stage = analyze([self._savegame_cycle(user_snapshot=False)])["sessions"][0]
        self.assertEqual(stage["original_operation_counts"]["savegame_enter"], 1)
        self.assertEqual(stage["original_operation_counts"]["saveworld_enter"], 1)
        self.assertEqual(stage["original_operation_counts"]["saveuser_enter"], 1)
        self.assertEqual(stage["fully_traced_original_savegame_cycles"], 0)
        self.assertFalse(stage["all_savegame_cycles_have_ordered_world_and_user_snapshots"])

    def test_savegame_per_save_call_requires_exactly_one_snapshot(self):
        # Existing stage-level booleans can be satisfied by a duplicate
        # snapshot from one call or a second Save() call without any snapshot.
        for fault in ("repeated_world_snapshot", "unchecked_extra_save"):
            with self.subTest(fault=fault):
                record = analyze([self._savegame_cycle(**{fault: True})])["sessions"][0]
                self.assertEqual(record["original_operation_counts"]["savegame_enter"], 1)
                self.assertEqual(record["original_operation_counts"]["savegame_exit"], 1)
                self.assertEqual(record["original_operation_counts"]["saveworld_exit"], 1)
                self.assertEqual(record["original_operation_counts"]["saveuser_exit"], 1)
                self.assertEqual(record["fully_traced_original_savegame_cycles"], 0)
                self.assertGreater(record["incomplete_or_misordered_savegame_cycles"], 0)
                self.assertFalse(record["all_savegame_cycles_have_ordered_world_and_user_snapshots"])

    def test_original_savegame_exceptions_and_escaped_exits_disqualify_traced_cycle(self):
        # Nonzero file snapshots in finally do not establish Save() success.
        # Original wrappers emit operation.exception and exceptionEscaped=True
        # even when SaveWorld/User methods ultimately unwind.
        faults = ("Save.exception", "SaveWorld.exception", "SaveGame.exception",
                  "Save.argumentFileSnapshot.unavailable", "Save.exit.escaped",
                  "SaveWorld.exit.escaped", "SaveGame.exit.escaped")
        for fault in faults:
            with self.subTest(fault=fault):
                record = analyze([self._savegame_cycle(fault=fault)])["sessions"][0]
                self.assertEqual(record["original_operation_counts"]["savegame_enter"], 1)
                self.assertEqual(record["original_operation_counts"]["savegame_exit"], 1)
                self.assertEqual(record["save_nonzero_file_snapshots"], 2)
                self.assertEqual(record["fully_traced_original_savegame_cycles"], 0)
                self.assertGreater(record["incomplete_or_misordered_savegame_cycles"], 0)
                self.assertFalse(record["all_savegame_cycles_have_ordered_world_and_user_snapshots"])

    def _loadt_trace(self, operations, exit_detail="exceptionEscaped=False; elapsed_ms=0.000"):
        return self.put("loadt.jsonl", [
            row("synthetic-load-session", seq, "save", op,
                "2026-11-05T13:00:%02dZ" % seq,
                ("exists_at_filename_argument=True; length_class=nonzero; "
                 "readback_and_deserialization_unverified=true")
                if op == "Load.argumentFileSnapshot"
                else (exit_detail if op == "Load<T>.exit" else ""))
            for seq, op in enumerate(operations, start=1)
        ])

    def test_one_original_loadt_call_has_one_nonzero_file_snapshot_and_exit(self):
        path = self._loadt_trace([
            "Load<T>.enter", "Load.argumentFileSnapshot", "Load<T>.exit",
        ])
        record = analyze([path])["sessions"][0]
        self.assertEqual(record["fully_traced_original_loadt_calls"], 1)
        self.assertEqual(record["incomplete_or_ambiguous_original_loadt_calls"], 0)
        self.assertTrue(
            record["all_original_loadt_calls_have_one_nonzero_snapshot_no_caught"])
        self.assertFalse(analyze([path])["original_rgd_deserialization_success_proven"])

    def test_equal_loadt_counts_but_snapshot_before_entry_does_not_prove_load(self):
        record = analyze([self._loadt_trace([
            "Load.argumentFileSnapshot", "Load<T>.enter", "Load<T>.exit",
        ])])["sessions"][0]
        self.assertEqual(record["original_operation_counts"]["load_enter"], 1)
        self.assertEqual(record["original_operation_counts"]["load_file_snapshot"], 1)
        self.assertEqual(record["original_operation_counts"]["load_exit"], 1)
        self.assertEqual(record["fully_traced_original_loadt_calls"], 0)
        self.assertGreater(record["incomplete_or_ambiguous_original_loadt_calls"], 0)

    def test_loadt_with_two_or_missing_snapshots_must_not_look_complete(self):
        cases = [
            ["Load<T>.enter", "Load<T>.exit"],
            ["Load<T>.enter", "Load.argumentFileSnapshot",
             "Load.argumentFileSnapshot", "Load<T>.exit"],
            ["Load<T>.enter", "Load.argumentFileSnapshot.unavailable",
             "Load<T>.exit"],
        ]
        for operations in cases:
            with self.subTest(operations=operations):
                record = analyze([self._loadt_trace(operations)])["sessions"][0]
                self.assertEqual(record["fully_traced_original_loadt_calls"], 0)
                self.assertFalse(
                    record["all_original_loadt_calls_have_one_nonzero_snapshot_no_caught"])

    def test_original_loadt_escaped_or_malformed_exit_disqualifies_nonzero_snapshot(self):
        # The genuine original Android instrumented Load<T> has an explicit
        # exceptionEscaped status on *every* finally exit. A nonzero file does
        # not make an escaped or missing original exit detail a clean load.
        for detail in (
                "exceptionEscaped=True; elapsed_ms=0.000",
                "exceptionEscaped=True; elapsed_ms=999.999",
                "",
                "exceptionEscaped=false; elapsed_ms=0.000",
                "exceptionEscaped=False; elapsed_ms=unknown"):
            with self.subTest(detail=detail):
                stage = analyze([self._loadt_trace([
                    "Load<T>.enter", "Load.argumentFileSnapshot", "Load<T>.exit",
                ], exit_detail=detail)])["sessions"][0]
                self.assertEqual(stage["fully_traced_original_loadt_calls"], 0)
                self.assertGreater(stage["incomplete_or_ambiguous_original_loadt_calls"], 0)
                self.assertFalse(stage["all_original_loadt_calls_have_one_nonzero_snapshot_no_caught"])

    def test_original_loadt_exception_marker_cannot_be_counted_as_clean_load(self):
        stage = analyze([self._loadt_trace([
            "Load<T>.enter", "Load.argumentFileSnapshot",
            "Load<T>.exception", "Load<T>.exit",
        ])])["sessions"][0]
        self.assertEqual(stage["fully_traced_original_loadt_calls"], 0)
        self.assertFalse(stage["all_original_loadt_calls_have_one_nonzero_snapshot_no_caught"])

    def test_loadt_caught_exception_disqualifies_even_with_nonzero_path(self):
        record = analyze([self._loadt_trace([
            "Load<T>.enter", "Load.caughtException",
            "Load.argumentFileSnapshot", "Load<T>.exit",
        ])])["sessions"][0]
        self.assertEqual(record["fully_traced_original_loadt_calls"], 0)
        self.assertGreater(record["incomplete_or_ambiguous_original_loadt_calls"], 0)
        self.assertFalse(
            record["all_original_loadt_calls_have_one_nonzero_snapshot_no_caught"])

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

    def test_same_size_fake_jsonl_cannot_claim_pinned_owner_log_provenance(self):
        # Exact byte length alone is not content identity. A forged three-file
        # fixture matching every expected size must still fail its Git blob
        # integrity check, rather than claiming to be CL@520c4c phone logs.
        from unittest.mock import patch
        from scripts import t4_owner5nov_jsonl_lifecycle as owner
        paths = []
        for i in range(3):
            paths.append(self.put(str(i) + ".jsonl", [
                row("synthetic-" + str(i), 1, "startup", "logger.ready",
                    "2026-11-05T10:00:00Z"),
            ]))
        fake_sizes = tuple(p.stat().st_size for p in sorted(paths))
        with patch.object(owner, "PINNED_BYTES", fake_sizes):
            with self.assertRaisesRegex(EvidenceInputError, "unverified_pinned_owner_log_git_blob"):
                analyze(paths, pinned=True)

    def test_pinned_git_blob_cannot_be_followed_by_unverified_second_read(self):
        # A file is mutable even after its Git blob SHA has been checked.
        # Simulate the source changing AFTER the base verifier parsed it and
        # BEFORE the detailed original Load<T> chronology reopens it.
        import hashlib
        from unittest.mock import patch
        from scripts import t4_owner5nov_jsonl_lifecycle as owner

        operations = ("Load<T>.enter", "Load.argumentFileSnapshot", "Load<T>.exit")
        original = [
            row("original-synthetic", i, "save", operation,
                "2026-11-05T13:00:%02dZ" % i,
                ("exists_at_filename_argument=True; length_class=nonzero; "
                 "readback_and_deserialization_unverified=true")
                if operation == "Load.argumentFileSnapshot"
                else ("exceptionEscaped=False; elapsed_ms=0.000"
                      if operation == "Load<T>.exit" else ""))
            for i, operation in enumerate(operations, 1)
        ]
        changed = [dict(item) for item in original]
        changed[0]["operation"] = "Load<T>.exit"  # exactly same source byte count
        files = [self.put("a.jsonl", original)]
        files.extend([
            self.put("b.jsonl", [row("other1", 1, "startup", "logger.ready",
                                     "2026-11-05T14:00:00Z")]),
            self.put("c.jsonl", [row("other2", 1, "startup", "logger.ready",
                                     "2026-11-05T15:00:00Z")]),
        ])
        payloads = [p.read_bytes() for p in files]
        blob = lambda data: hashlib.sha1(
            b"blob " + str(len(data)).encode("ascii") + b"\\0" + data
        ).hexdigest()
        base_summarize = owner.summarize

        def rewrite_after_base_read(inputs):
            result = base_summarize(inputs)
            files[0].write_text("".join(json.dumps(r) + "\\n" for r in changed),
                                encoding="utf-8")
            self.assertEqual(files[0].stat().st_size, len(payloads[0]))
            return result

        with (patch.object(owner, "PINNED_BYTES", tuple(map(len, payloads))),
              patch.object(owner, "PINNED_GIT_BLOBS",
                           tuple(blob(data) for data in payloads)),
              patch.object(owner, "summarize", side_effect=rewrite_after_base_read)):
            evidence = analyze(files, pinned=True)
        self.assertEqual(evidence["source_pin"], "CL_520c4cf_2026_11_05")
        # The parsed evidence must correspond to the SAME authenticated
        # bytes, not the mutated path content. No raw record is returned.
        original_session = next(x for x in evidence["sessions"]
                                if x["original_operation_counts"].get("load_enter"))
        self.assertEqual(original_session["fully_traced_original_loadt_calls"], 1)
        self.assertEqual(original_session["original_operation_counts"]["load_enter"], 1)
        self.assertEqual(original_session["original_operation_counts"]["load_exit"], 1)
        self.assertFalse(evidence["original_rgd_deserialization_success_proven"])

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
