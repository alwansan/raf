"""Reject forged/incomplete attributed mouse telemetry; source-only."""
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "t4_epochs", Path(__file__).resolve().parents[1] /
    "t4_correlate_mouse_runtime_epochs.py")
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


class AttributedEnvelopeTests(unittest.TestCase):
    def record(self, **changes):
        row = dict(utc="2026-11-09T21:36:00Z", session="original-session",
                   sequence=1, thread=1, area="input",
                   operation="physical_mouse_capture_requested",
                   detail="epoch=7")
        row.update(changes)
        return row

    def test_complete_original_envelope_accepted(self):
        op, _, scope, seq, valid = mod.decode_record(self.record())
        self.assertTrue(valid)
        self.assertEqual(scope, ("jsonl", "original-session"))
        self.assertEqual(seq, 1)
        self.assertEqual(op, "physical_mouse_capture_requested")

    def test_missing_timestamp_is_not_attributed(self):
        row = self.record()
        del row["utc"]
        self.assertFalse(mod.decode_record(row)[4])

    def test_missing_thread_is_not_attributed(self):
        row = self.record()
        del row["thread"]
        self.assertFalse(mod.decode_record(row)[4])

    def test_non_input_area_cannot_claim_capture(self):
        self.assertFalse(mod.decode_record(self.record(area="render"))[4])

    def test_bool_thread_is_not_integer_thread(self):
        self.assertFalse(mod.decode_record(self.record(thread=True))[4])

    def test_missing_fields_cannot_form_positive_attempt(self):
        request = self.record()
        del request["utc"]
        result = mod.triage([request])
        self.assertEqual(result["matched_jsonl_scoped_attempts"], 0)
        self.assertFalse(result["device_pass"])


if __name__ == "__main__":
    unittest.main()
