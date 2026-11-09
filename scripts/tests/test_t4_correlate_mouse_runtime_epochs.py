"""Source-only safety regressions for original-game T4 epoch correlation."""
import importlib.util
from pathlib import Path
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "t4_correlate_mouse_runtime_epochs.py"
spec = importlib.util.spec_from_file_location("t4_runtime_epoch", SCRIPT)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def req(epoch):
    return f"physical_mouse_capture_requested epoch={epoch}; nativeAccepted=unknown"


def actions(epoch, events=3, press=1, release=1, v=1, h=0):
    return (f"physical_mouse_captured_action_callbacks epoch={epoch}; "
            f"capturedCallbackEvents={events}; pressCallbacks={press}; "
            f"releaseCallbacks={release}; verticalScrollCallbacks={v}; "
            f"horizontalScrollCallbacks={h}; unityButtonsAndWheelVerified=false")


def readers(epoch, calls=5, fallback=2, captured="true"):
    return (f"physical_mouse_legacy_reader_evidence epoch={epoch}; "
            f"captureRequested=true; captureObserved={captured}; "
            f"getterCalls={calls}; positiveLegacy=0; positiveFallback={fallback}; "
            f"positiveEdges=1; positiveScroll=1; "
            f"down0Calls=2,legacy=0,fallback=1; "
            f"countersAreGetterCallsNotClicks=true; unityGameplayVerified=false")


class RuntimeMouseEpochTests(unittest.TestCase):
    def test_same_epoch_both_is_observation_only(self):
        v = gate.triage([req(8), actions(8), readers(8)])
        self.assertEqual(v["status"], "SAME_EPOCH_CAPTURED_CALLBACK_AND_FALLBACK_GETTER")
        self.assertEqual(v["epochs_with_both"], [8])
        self.assertFalse(v["device_pass"])
        self.assertFalse(v["unity_gameplay_verified"])

    def test_reader_log_before_action_log_same_update_is_valid(self):
        # Unity Update writes reader marker before callback marker.
        v = gate.triage([req(9), readers(9), actions(9)])
        self.assertEqual(v["same_epoch_positive_fallback_attempts"], 1)

    def test_same_line_json_log_envelope_supported(self):
        v = gate.triage([
            {"operation": "physical_mouse_capture_requested", "detail": "epoch=10"},
            {"operation": "physical_mouse_captured_action_callbacks",
             "detail": actions(10).split(" ", 1)[1]},
            {"operation": "physical_mouse_legacy_reader_evidence",
             "detail": readers(10).split(" ", 1)[1]},
        ])
        self.assertEqual(v["same_epoch_callback_and_getter_attempts"], 1)

    def test_epoch_drift_cannot_borrow_reader(self):
        v = gate.triage([req(11), actions(11), req(12), readers(12)])
        self.assertEqual(v["same_epoch_callback_and_getter_attempts"], 0)
        self.assertEqual(v["status"], "CAPTURED_CALLBACK_WITHOUT_SAME_EPOCH_GETTER")

    def test_pre_request_cannot_be_reused(self):
        v = gate.triage([actions(13), req(13), readers(13)])
        self.assertEqual(v["same_epoch_callback_and_getter_attempts"], 0)
        self.assertEqual(v["unpaired_epoch_markers"], 1)

    def test_release_delimits_generation(self):
        v = gate.triage([req(14), actions(14),
                         "physical_mouse_capture_released focus=true",
                         readers(14)])
        self.assertEqual(v["same_epoch_callback_and_getter_attempts"], 0)

    def test_retries_with_same_epoch_do_not_merge_snapshots(self):
        v = gate.triage([req(15), actions(15),
                         "physical_mouse_capture_retry epoch=15; attempt=2",
                         readers(15)])
        self.assertEqual(v["same_epoch_callback_and_getter_attempts"], 0)

    def test_callback_only_not_unity(self):
        v = gate.triage([req(16), actions(16)])
        self.assertEqual(v["status"], "CAPTURED_CALLBACK_WITHOUT_SAME_EPOCH_GETTER")

    def test_positive_native_without_fallback_not_claimed_as_fallback(self):
        v = gate.triage([req(17), actions(17), readers(17, fallback=0)])
        self.assertEqual(v["status"], "SAME_EPOCH_CALLBACK_AND_GETTER_NO_FALLBACK")

    def test_capture_observed_false_cannot_prove_legacy_bridge(self):
        v = gate.triage([req(18), actions(18), readers(18, captured="false")])
        self.assertEqual(v["same_epoch_positive_fallback_attempts"], 0)
        self.assertGreater(v["invalid_markers"], 0)

    def test_impossible_count_rejected(self):
        v = gate.triage([req(19), actions(19), readers(19, calls=2, fallback=3)])
        self.assertEqual(v["status"], "INVALID_OR_INCOMPLETE_CAPTURE_PROVENANCE")

    def test_rollback_counter_invalidates_attempt(self):
        v = gate.triage([req(20), actions(20, events=12), actions(20, events=3),
                         readers(20)])
        self.assertEqual(v["same_epoch_callback_and_getter_attempts"], 0)
        self.assertGreater(v["invalid_markers"], 0)

    def test_native_and_fallback_combined_cannot_exceed_getters(self):
        impossible = readers(22, calls=5, fallback=2).replace(
            "positiveLegacy=0", "positiveLegacy=4")
        v = gate.triage([req(22), actions(22), impossible])
        self.assertEqual(v["status"], "INVALID_OR_INCOMPLETE_CAPTURE_PROVENANCE")
        self.assertGreater(v["invalid_markers"], 0)

    def test_reader_snapshot_decrease_invalidates_generation(self):
        v = gate.triage([req(23), actions(23),
                         readers(23, calls=8, fallback=2),
                         readers(23, calls=5, fallback=1)])
        self.assertEqual(v["same_epoch_callback_and_getter_attempts"], 0)
        self.assertGreater(v["invalid_markers"], 0)

    def test_missing_epoch_rejected(self):
        v = gate.triage([req(21), actions(21).replace("epoch=21", "epoch=bad"),
                         readers(21)])
        self.assertEqual(v["same_epoch_callback_and_getter_attempts"], 0)
        self.assertGreater(v["invalid_markers"], 0)

    @staticmethod
    def logger(operation, detail, session, sequence, area="input"):
        # Faithful subset of actual PersistentDiagnosticLog JSONL:
        # utc/session/sequence/thread/area/operation/detail.
        return {"utc": "2026-11-09T19:12:00+00:00", "session": session,
                "sequence": sequence, "thread": 1, "area": area,
                "operation": operation, "detail": detail}

    def test_real_logger_one_session_same_epoch(self):
        name = "20261109T191200123-abcdef12"
        v = gate.triage([
            self.logger("physical_mouse_capture_requested", "epoch=30", name, 1),
            self.logger("physical_mouse_captured_action_callbacks",
                        actions(30).split(" ", 1)[1], name, 6),
            self.logger("physical_mouse_legacy_reader_evidence",
                        readers(30).split(" ", 1)[1], name, 9),
        ])
        self.assertEqual(v["same_epoch_positive_fallback_attempts"], 1)
        self.assertEqual(v["matched_jsonl_scoped_attempts"], 1)
        self.assertEqual(v["logger_sessions_scanned"], 1)
        self.assertFalse(v["device_pass"])

    def test_restart_with_reused_epoch_not_a_join(self):
        a, b = "20261109T191200123-aaaabbbb", "20261109T191201123-ccccdddd"
        v = gate.triage([
            self.logger("physical_mouse_capture_requested", "epoch=31", a, 1),
            self.logger("physical_mouse_captured_action_callbacks",
                        actions(31).split(" ", 1)[1], a, 2),
            self.logger("physical_mouse_legacy_reader_evidence",
                        readers(31).split(" ", 1)[1], b, 1),
        ])
        self.assertEqual(v["same_epoch_callback_and_getter_attempts"], 0)
        self.assertGreater(v["provenance_scope_mismatches"], 0)

    def test_valid_second_logger_only_not_borrow_first(self):
        a, b = "20261109T191200123-aaaabbbb", "20261109T191201123-ccccdddd"
        v = gate.triage([
            self.logger("physical_mouse_capture_requested", "epoch=32", a, 1),
            self.logger("physical_mouse_captured_action_callbacks",
                        actions(32).split(" ", 1)[1], a, 2),
            self.logger("physical_mouse_capture_requested", "epoch=32", b, 1),
            self.logger("physical_mouse_captured_action_callbacks",
                        actions(32).split(" ", 1)[1], b, 2),
            self.logger("physical_mouse_legacy_reader_evidence",
                        readers(32).split(" ", 1)[1], b, 3),
        ])
        self.assertEqual(v["same_epoch_callback_and_getter_attempts"], 1)
        self.assertEqual(v["matched_jsonl_scoped_attempts"], 1)
        self.assertEqual(v["logger_sessions_scanned"], 2)

    def test_duplicate_startup_segment_sequence_poison_session(self):
        name = "20261109T191200123-aabbccdd"
        v = gate.triage([
            self.logger("physical_mouse_capture_requested", "epoch=33", name, 3),
            self.logger("physical_mouse_captured_action_callbacks",
                        actions(33).split(" ", 1)[1], name, 4),
            self.logger("physical_mouse_legacy_reader_evidence",
                        readers(33).split(" ", 1)[1], name, 5),
            # Startup replay was appended out of order from another copy.
            self.logger("logger.ready", "version=1", name, 1, "startup"),
        ])
        self.assertEqual(v["same_epoch_positive_fallback_attempts"], 0)
        self.assertEqual(v["poisoned_logger_sessions"], 1)
        self.assertGreater(v["invalid_markers"], 0)

    def test_poisoned_logger_reader_only_cannot_claim_getter(self):
        name = "20261109T193900123-poisoned"
        v = gate.triage([
            self.logger("physical_mouse_capture_requested", "epoch=41", name, 4),
            self.logger("physical_mouse_legacy_reader_evidence",
                        readers(41).split(" ", 1)[1], name, 5),
            # A duplicate/out-of-order record poisons the entire logger.
            self.logger("logger.ready", "version=1", name, 2, "startup"),
        ])
        self.assertEqual(v["poisoned_logger_sessions"], 1)
        self.assertEqual(v["getter_only_attempts"], 0)
        self.assertEqual(v["status"], "INVALID_OR_INCOMPLETE_CAPTURE_PROVENANCE")
        self.assertFalse(v["device_pass"])

    def test_missing_or_invalid_logger_sequence_cannot_borrow(self):
        name = "20261109T191200123-aabbccdd"
        bad = self.logger("physical_mouse_legacy_reader_evidence",
                          readers(34).split(" ", 1)[1], name, 3)
        bad["sequence"] = True  # bool is not a valid integer sequence.
        v = gate.triage([
            self.logger("physical_mouse_capture_requested", "epoch=34", name, 1),
            self.logger("physical_mouse_captured_action_callbacks",
                        actions(34).split(" ", 1)[1], name, 2),
            bad,
        ])
        self.assertEqual(v["same_epoch_callback_and_getter_attempts"], 0)

    def test_unattributed_legacy_record_cannot_complete_jsonl(self):
        name = "20261109T191200123-aabbccdd"
        v = gate.triage([
            self.logger("physical_mouse_capture_requested", "epoch=35", name, 1),
            self.logger("physical_mouse_captured_action_callbacks",
                        actions(35).split(" ", 1)[1], name, 2),
            readers(35),
        ])
        self.assertEqual(v["same_epoch_callback_and_getter_attempts"], 0)

    def test_unity_area_imitating_mouse_operation_is_not_input(self):
        name = "20261109T191200123-aabbccdd"
        v = gate.triage([
            self.logger("physical_mouse_capture_requested", "epoch=36", name, 1),
            self.logger("physical_mouse_captured_action_callbacks",
                        actions(36).split(" ", 1)[1], name, 2, "unity"),
            self.logger("physical_mouse_legacy_reader_evidence",
                        readers(36).split(" ", 1)[1], name, 3),
        ])
        self.assertEqual(v["same_epoch_callback_and_getter_attempts"], 0)
        self.assertGreater(v["invalid_markers"], 0)

    def test_serialized_real_jsonl_strings_are_recognized(self):
        import json
        name = "20261109T191200123-aabbccdd"
        rows = [
            self.logger("physical_mouse_capture_requested", "epoch=37", name, 1),
            self.logger("physical_mouse_legacy_reader_evidence",
                        readers(37).split(" ", 1)[1], name, 2),
            self.logger("physical_mouse_captured_action_callbacks",
                        actions(37).split(" ", 1)[1], name, 3),
        ]
        v = gate.triage([json.dumps(row) for row in rows])
        self.assertEqual(v["matched_jsonl_scoped_attempts"], 1)
        self.assertFalse(v["device_pass"])

    def test_mixed_process_risk_stays_disclosed(self):
        v = gate.triage([])
        self.assertFalse(v["device_pass"])
        self.assertIn("epoch may repeat across", v["limitations"])
        self.assertFalse(v["device_pass"])


if __name__ == "__main__":
    unittest.main()
