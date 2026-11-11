"""Regression: a completed Foam pair must not mask a leaked captured token."""
import json
import unittest
from scripts.t2_foam_rt_lifetime_gate import check

SHA = "a" * 40
def payload(events):
    return json.dumps({"schema":"t2-foam-rt-lifetime-v1",
        "capture_id":"capture-001","source_commit":SHA,"frame":12,
        "events":[{"seq":i+1,"kind":kind,"token":token}
                  for i,(kind,token) in enumerate(events)]}).encode()

PAIR = [("allocate","texture-001"),("pass0_write","texture-001"),
        ("pass1_read","texture-001"),("release","texture-001")]

class LifetimeTerminalTest(unittest.TestCase):
    def test_completed_pair(self):
        self.assertEqual(check(payload(PAIR))["lifetime_order_evidence"],
                         "CAPTURE_ORDER_CONSISTENT")

    def test_extra_unreleased_allocation_rejected(self):
        with self.assertRaisesRegex(ValueError,"unreleased_capture_resource"):
            check(payload(PAIR+[("allocate","texture-002")]))

    def test_extra_written_unreleased_rejected(self):
        with self.assertRaisesRegex(ValueError,"unreleased_capture_resource"):
            check(payload(PAIR+[("allocate","texture-002"),
                                ("pass0_write","texture-002")]))

    def test_extra_released_allocation_allowed(self):
        result = check(payload(PAIR+[("allocate","texture-002"),
                                     ("release","texture-002")]))
        self.assertFalse(result["original_foam_runtime_provenance_verified"])

if __name__ == "__main__":
    unittest.main()
