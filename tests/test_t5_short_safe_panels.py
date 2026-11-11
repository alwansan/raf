"""Source-only regression for responsive diagnostic panels; not device proof."""
from pathlib import Path
import unittest

SOURCE = (Path(__file__).resolve().parents[1] /
          "android-port/Runtime/Platform/AndroidTouchUiPanel.cs")


class ShortSafePanelContract(unittest.TestCase):
    def test_safe_area_fit_is_called_after_anchor_update(self):
        s = SOURCE.read_text(encoding="utf-8")
        self.assertLess(s.index("safeRoot.offsetMin = safeRoot.offsetMax = Vector2.zero;"),
                        s.index("FitPanelsToSafeArea(safe);"))
        self.assertIn("float canvasScale = Screen.height / 720f", s)
        self.assertIn("safe.height / canvasScale", s)
        self.assertIn("safe.width / canvasScale", s)
        self.assertIn("FitPanel(editorObject, factor)", s)
        self.assertIn("FitPanel(reportObject, factor)", s)
        self.assertIn("rect.anchoredPosition = new Vector2(0f, -228f * factor)", s)

    def test_reference_and_short_safe_area_geometry(self):
        # 650x440 report starts 228 UI units below top; leave 16 margin.
        # This models the source formula, not a Unity layout render.
        for screen_w, screen_h, safe_w, safe_h in [
            (2400, 1080, 2400, 1080),
            (1600, 720, 1600, 720),
            (1280, 720, 1100, 580),
            (800, 600, 600, 480),
        ]:
            with self.subTest(screen=(screen_w, screen_h), safe=(safe_w, safe_h)):
                canvas_scale = screen_h / 720.0
                ui_w, ui_h = safe_w / canvas_scale, safe_h / canvas_scale
                factor = max(.1, min(1.0, ui_h / 684.0, ui_w / 666.0))
                self.assertLessEqual(668 * factor, ui_h - 0.01)
                self.assertLessEqual(650 * factor, ui_w - 0.01)


if __name__ == "__main__":
    unittest.main()
