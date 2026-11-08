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
        self.assertIn("attempt > 1 && (attempt & (attempt - 1)) == 0", self.source)
        self.assertIn('"physical_mouse_capture_retry"', self.source)
        observed = [n for n in range(1, 1001) if n > 1 and (n & (n - 1)) == 0]
        self.assertEqual(observed, [2, 4, 8, 16, 32, 64, 128, 256, 512])

    def test_first_request_marker_remains(self):
        self.assertIn('"physical_mouse_capture_requested"', self.source)
        self.assertIn("nativeAccepted=unknown; requiresDeviceConfirmation=true", self.source)


if __name__ == "__main__":
    unittest.main()
