"""T4 isolated negative and positive controls for queue-overflow evidence gating."""
import json
import tempfile
import unittest
from pathlib import Path
from scripts.t4_verify_device_world_save_log import summarize

def event(session, sequence, utc, operation, area="save", detail=""):
    return {"session":session,"sequence":sequence,"utc":utc,"area":area,
            "operation":operation,"detail":detail}

class OverflowEvidenceGate(unittest.TestCase):
    def run_case(self, overflow):
        records = [
            event("synthetic-A",1,"2026-11-05T10:00:00Z","Save.argumentFileSnapshot",
                  detail="exists_at_filename_argument=True;length_class=nonzero;"),
            event("synthetic-B",1,"2026-11-05T11:00:00Z","Load.argumentFileSnapshot",
                  detail="exists_at_filename_argument=True;length_class=nonzero;"),
        ]
        if overflow:
            records.insert(0,event("synthetic-A",2,"2026-11-05T10:01:00Z",
                                   "queue_overflow",area="logging"))
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory)/"synthetic.jsonl"
            file.write_text("".join(json.dumps(row)+"\n" for row in records),encoding="utf-8")
            return summarize([file])

    def test_complete_logs_allow_cross_session_hints_only(self):
        result=self.run_case(False)
        self.assertTrue(result["save_nonzero_in_earlier_session"])
        self.assertTrue(result["load_nonzero_in_later_session"])
        self.assertFalse(result["logging_queue_overflow_observed"])
        self.assertFalse(result["real_rgd_durability_or_reopen_proven"])

    def test_global_queue_overflow_suppresses_both_positive_hints(self):
        result=self.run_case(True)
        self.assertFalse(result["save_nonzero_in_earlier_session"])
        self.assertFalse(result["load_nonzero_in_later_session"])
        self.assertTrue(result["logging_queue_overflow_observed"])
        self.assertFalse(result["local005_device_confirmed"])

if __name__=="__main__":
    unittest.main()
