#!/usr/bin/env python3
"""Source + geometry regression for the three right-side diagnostic actions.

This is a CPU-only contract check; it does not claim Unity/device acceptance.
"""
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[2] / "android-port/Runtime/Platform/AndroidTouchUiPanel.cs"


def fitted_bounds(screen_height, safe_width, safe_height):
    canvas_scale = screen_height / 720.0
    width = safe_width / canvas_scale
    height = safe_height / canvas_scale
    factor = max(0.0, min(1.0, height / 224.0, width / 166.0))
    # Right-aligned button: inset=8, width=150, top offsets 78/126/174, height=42.
    return factor, [(8 * factor, 158 * factor, y * factor, (y + 42) * factor)
                    for y in (78, 126, 174)], width, height


class RightButtonSafeWidthTest(unittest.TestCase):
    def test_source_uses_both_dimensions(self):
        source = SOURCE.read_text()
        method = source.split("private void FitRightButtonsToSafeArea(Rect safe)", 1)[1].split(
            "private static void FitPanel", 1)[0]
        self.assertIn("safeWidth / 166f", method)
        self.assertIn("safeHeight / 224f", method)
        self.assertIn("Mathf.Clamp01", method)
        self.assertNotIn("safeHeight / 224f, 0.1f", method)

    def test_geometry_varied_safe_areas(self):
        for screen_h, safe_w, safe_h in [
            (1080, 2400, 1080), (1080, 100, 1080),
            (720, 166, 224), (720, 50, 70),
            (1440, 140, 400), (720, 1, 1),
        ]:
            with self.subTest(screen_h=screen_h, safe_w=safe_w, safe_h=safe_h):
                factor, boxes, width, height = fitted_bounds(screen_h, safe_w, safe_h)
                self.assertGreaterEqual(factor, 0)
                for left, right, top, bottom in boxes:
                    self.assertGreaterEqual(left, 0)
                    self.assertLessEqual(right, width + 1e-6)
                    self.assertGreaterEqual(top, 0)
                    self.assertLessEqual(bottom, height + 1e-6)


if __name__ == "__main__":
    unittest.main()
