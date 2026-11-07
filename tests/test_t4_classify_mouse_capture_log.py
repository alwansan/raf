import unittest
from scripts.t4_classify_mouse_capture_log import classify


class MouseCaptureTraceTests(unittest.TestCase):
    def test_empty(self):
        self.assertEqual(classify([])["findings"][0]["classification"], "NO_ESCAPE_SEQUENCE_OBSERVED")

    def test_missing_rearm(self):
        self.assertEqual(classify(["physical_mouse_lock_intent escape_release"])["findings"][0]["classification"], "NO_REARM_OBSERVED")

    def test_lock_without_request(self):
        events = ["physical_mouse_lock_intent escape_release", "physical_mouse_lock_intent authored_lock"]
        self.assertEqual(classify(events)["findings"][0]["classification"], "LOCK_WITHOUT_REQUEST_OBSERVED")

    def test_request_without_relative(self):
        events = ["physical_mouse_lock_intent escape_release", "physical_mouse_lock_intent authored_lock", "physical_mouse_capture_requested"]
        self.assertEqual(classify(events)["findings"][0]["classification"], "REQUEST_WITHOUT_RELATIVE_OBSERVED")

    def test_relative_not_device_proof(self):
        events = ["physical_mouse_lock_intent escape_release", "physical_mouse_lock_intent authored_lock", "physical_mouse_capture_requested", "physical_mouse_relative"]
        result = classify(events)
        self.assertEqual(result["findings"][0]["classification"], "RELATIVE_AFTER_REARM_OBSERVED")
        self.assertFalse(result["device_success_proven"])

    def test_second_escape_does_not_borrow_first_cycle(self):
        events = ["physical_mouse_lock_intent escape_release", "physical_mouse_lock_intent authored_lock", "physical_mouse_capture_requested", "physical_mouse_relative", "physical_mouse_lock_intent escape_release"]
        self.assertEqual(classify(events)["findings"][-1]["classification"], "NO_REARM_OBSERVED")


if __name__ == "__main__":
    unittest.main()
