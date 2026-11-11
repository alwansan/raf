#!/usr/bin/env python3
"""CPU-only regression for the existing Android safe-area panels."""
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[2] / "android-port/Runtime/Platform/AndroidTouchUiPanel.cs"


def bounds(screen_height, safe_width, safe_height):
    canvas_scale = screen_height / 720.0
    width = safe_width / canvas_scale
    height = safe_height / canvas_scale
    factor = max(0.0, min(1.0, height / 684.0, width / 666.0))
    # Largest panel: width 650; bottom = top 228 + height 440.
    return factor, 650 * factor, 668 * factor, width, height


class PanelSafeGeometryTest(unittest.TestCase):
    def test_source_has_no_forced_minimum(self):
        source = SOURCE.read_text()
        method = source.split("private void FitPanelsToSafeArea(Rect safe)", 1)[1].split(
            "private void FitRightButtonsToSafeArea", 1)[0]
        self.assertIn("Mathf.Clamp01", method)
        self.assertIn("safeHeight / 684f", method)
        self.assertIn("safeWidth / 666f", method)
        self.assertNotIn("0.1f, 1f", method)

    def test_panels_remain_within_safe_bounds(self):
        for screen_h, safe_w, safe_h in [
            (1080, 2400, 1080), (720, 666, 684), (1080, 100, 1080),
            (720, 50, 70), (1440, 140, 400), (720, 1, 1),
        ]:
            with self.subTest(screen_h=screen_h, safe_w=safe_w, safe_h=safe_h):
                factor, right, bottom, width, height = bounds(screen_h, safe_w, safe_h)
                self.assertGreaterEqual(factor, 0)
                self.assertLessEqual(right, width + 1e-6)
                self.assertLessEqual(bottom, height + 1e-6)


if __name__ == "__main__":
    unittest.main()
