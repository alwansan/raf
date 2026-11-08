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


    def test_relative_after_release_is_not_capture_success(self):
        events = ["physical_mouse_lock_intent escape_release", "physical_mouse_lock_intent authored_lock",
                  "physical_mouse_capture_requested", "physical_mouse_capture_released", "physical_mouse_relative"]
        self.assertEqual(classify(events)["findings"][0]["classification"], "RELEASED_BEFORE_RELATIVE_OBSERVED")

    def test_relative_before_release_is_observed(self):
        events = ["physical_mouse_lock_intent escape_release", "physical_mouse_lock_intent authored_lock",
                  "physical_mouse_capture_requested", "physical_mouse_relative", "physical_mouse_capture_released"]
        self.assertEqual(classify(events)["findings"][0]["classification"], "RELATIVE_AFTER_REARM_OBSERVED")

    def test_release_without_relative_is_distinct(self):
        events = ["physical_mouse_lock_intent escape_release", "physical_mouse_lock_intent authored_lock",
                  "physical_mouse_capture_requested", "physical_mouse_capture_released"]
        self.assertEqual(classify(events)["findings"][0]["classification"], "RELEASED_BEFORE_RELATIVE_OBSERVED")

    def test_authored_unlock_ends_valid_relative_window(self):
        events = ["physical_mouse_lock_intent escape_release", "physical_mouse_lock_intent authored_lock",
                  "physical_mouse_capture_requested", "physical_mouse_lock_intent authored_unlock",
                  "physical_mouse_relative"]
        self.assertEqual(classify(events)["findings"][0]["classification"], "RELEASED_BEFORE_RELATIVE_OBSERVED")

    def test_relative_before_authored_unlock_remains_observed(self):
        events = ["physical_mouse_lock_intent escape_release", "physical_mouse_lock_intent authored_lock",
                  "physical_mouse_capture_requested", "physical_mouse_relative",
                  "physical_mouse_lock_intent authored_unlock"]
        self.assertEqual(classify(events)["findings"][0]["classification"], "RELATIVE_AFTER_REARM_OBSERVED")

    def test_cancelled_lock_cannot_borrow_late_request(self):
        events = ["physical_mouse_lock_intent escape_release",
                  "physical_mouse_lock_intent authored_lock",
                  "physical_mouse_lock_intent authored_unlock",
                  "physical_mouse_capture_requested", "physical_mouse_relative"]
        self.assertEqual(classify(events)["findings"][0]["classification"],
                         "LOCK_WITHOUT_REQUEST_OBSERVED")

    def test_fresh_lock_after_unlock_can_rearm(self):
        events = ["physical_mouse_lock_intent escape_release",
                  "physical_mouse_lock_intent authored_lock",
                  "physical_mouse_lock_intent authored_unlock",
                  "physical_mouse_lock_intent authored_lock",
                  "physical_mouse_capture_requested", "physical_mouse_relative"]
        self.assertEqual(classify(events)["findings"][0]["classification"],
                         "RELATIVE_AFTER_REARM_OBSERVED")

    def test_new_lock_supersedes_previous_attempt_without_release(self):
        events = ["physical_mouse_lock_intent escape_release",
                  "physical_mouse_lock_intent authored_lock",
                  "physical_mouse_lock_intent authored_lock",
                  "physical_mouse_capture_requested", "physical_mouse_relative"]
        result = classify(events)
        self.assertEqual(result["findings"][0]["classification"],
                         "RELATIVE_AFTER_REARM_OBSERVED")
        self.assertFalse(result["device_success_proven"])

    def test_superseded_lock_with_no_new_request_does_not_borrow_old_request(self):
        events = ["physical_mouse_lock_intent escape_release",
                  "physical_mouse_lock_intent authored_lock",
                  "physical_mouse_capture_requested",
                  "physical_mouse_lock_intent authored_lock",
                  "physical_mouse_relative"]
        self.assertEqual(classify(events)["findings"][0]["classification"],
                         "REQUEST_WITHOUT_RELATIVE_OBSERVED")

    def test_second_valid_rearm_succeeds_after_first_release(self):
        events = ["physical_mouse_lock_intent escape_release",
                  "physical_mouse_lock_intent authored_lock",
                  "physical_mouse_capture_requested",
                  "physical_mouse_capture_released",
                  "physical_mouse_lock_intent authored_lock",
                  "physical_mouse_capture_requested",
                  "physical_mouse_relative"]
        self.assertEqual(classify(events)["findings"][0]["classification"],
                         "RELATIVE_AFTER_REARM_OBSERVED")

    def test_release_does_not_allow_unlocked_late_request(self):
        events = ["physical_mouse_lock_intent escape_release",
                  "physical_mouse_lock_intent authored_lock",
                  "physical_mouse_capture_requested",
                  "physical_mouse_capture_released",
                  "physical_mouse_capture_requested",
                  "physical_mouse_relative"]
        self.assertEqual(classify(events)["findings"][0]["classification"],
                         "RELEASED_BEFORE_RELATIVE_OBSERVED")

    def test_retry_only_after_new_lock_is_attempt_not_proof(self):
        events = ["physical_mouse_lock_intent escape_release",
                  "physical_mouse_lock_intent authored_lock",
                  "physical_mouse_capture_retry attempt=2"]
        result = classify(events)
        self.assertEqual(result["findings"][0]["classification"],
                         "REQUEST_WITHOUT_RELATIVE_OBSERVED")
        self.assertEqual(result["counts"]["physical_mouse_capture_retry"], 1)
        self.assertFalse(result["device_success_proven"])

    def test_retry_after_release_cannot_borrow_relative(self):
        events = ["physical_mouse_lock_intent escape_release",
                  "physical_mouse_lock_intent authored_lock",
                  "physical_mouse_capture_retry attempt=2",
                  "physical_mouse_capture_released",
                  "physical_mouse_relative"]
        self.assertEqual(classify(events)["findings"][0]["classification"],
                         "RELEASED_BEFORE_RELATIVE_OBSERVED")

    def test_cross_epoch_relative_does_not_prove_rearm(self):
        events = ["physical_mouse_lock_intent escape_release",
                  "physical_mouse_lock_intent authored_lock",
                  "physical_mouse_capture_requested epoch=10",
                  "physical_mouse_capture_retry epoch=11 attempt=2",
                  "physical_mouse_relative epoch=9 events=1"]
        self.assertEqual(classify(events)["findings"][0]["classification"],
                         "REQUEST_WITHOUT_RELATIVE_OBSERVED")

    def test_matching_retry_epoch_is_observed(self):
        events = ["physical_mouse_lock_intent escape_release",
                  "physical_mouse_lock_intent authored_lock",
                  "physical_mouse_capture_requested epoch=10",
                  "physical_mouse_capture_retry epoch=11 attempt=2",
                  "physical_mouse_relative epoch=11 events=1"]
        self.assertEqual(classify(events)["findings"][0]["classification"],
                         "RELATIVE_AFTER_REARM_OBSERVED")

    def test_mixed_tagged_untagged_does_not_claim_correlation(self):
        events = ["physical_mouse_lock_intent escape_release",
                  "physical_mouse_lock_intent authored_lock",
                  "physical_mouse_capture_requested epoch=10",
                  "physical_mouse_relative events=1"]
        self.assertEqual(classify(events)["findings"][0]["classification"],
                         "REQUEST_WITHOUT_RELATIVE_OBSERVED")

if __name__ == "__main__":
    unittest.main()
