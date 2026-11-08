"""Bounded source-contract tests; not Android device or Unity runtime proof."""
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs"


class MouseRetryTelemetryContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")

    def test_attempt_counter_is_reset_on_release(self):
        self.assertIn("captureRequestAttempts = 0;", self.source)
        self.assertIn("int attempt = ++captureRequestAttempts;", self.source)

    def test_retries_are_power_of_two_throttled(self):
        # The first request is logged in its own if branch. Retries are
        # necessarily >1 in the else-if branch, and use the same power-of-two gate.
        self.assertIn("if (attempt == 1)", self.source)
        self.assertIn("else if ((attempt & (attempt - 1)) == 0)", self.source)
        self.assertIn('"physical_mouse_capture_retry"', self.source)
        observed = [n for n in range(1, 1001) if n > 1 and (n & (n - 1)) == 0]
        self.assertEqual(observed, [2, 4, 8, 16, 32, 64, 128, 256, 512])

    def test_first_relative_event_is_visible_in_short_device_sessions(self):
        # No physical movement => no marker; first accepted event => marker.
        # Subsequent markers remain throttled by 120 received events.
        self.assertIn(
            "received > 0 && (lastLoggedCount == 0 || received >= lastLoggedCount + 120)",
            self.source)
        emitted = []
        last = 0
        for received in range(0, 251):
            if received > 0 and (last == 0 or received >= last + 120):
                emitted.append(received)
                last = received
        self.assertEqual(emitted, [1, 121, 241])

    def test_first_request_marker_remains(self):
        self.assertIn('"physical_mouse_capture_requested"', self.source)
        self.assertIn("nativeAccepted=unknown; requiresDeviceConfirmation=true", self.source)


if __name__ == "__main__":
    unittest.main()
