"""Source contract and geometry regression for T5 right-side diagnostic actions."""
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "android-port/Runtime/Platform/AndroidTouchUiPanel.cs"


class RightDiagnosticSafeAreaTests(unittest.TestCase):
    def test_right_buttons_remain_safe_at_short_heights(self):
        for safe_height in (720, 360, 224, 180, 120):
            factor = max(.1, min(1., safe_height / 224.))
            # top of final button + its scaled height
            self.assertLessEqual((174 + 42) * factor, safe_height)
            self.assertGreaterEqual((126 - 78 - 42) * factor, 0)
            self.assertGreaterEqual((174 - 126 - 42) * factor, 0)

    def test_only_diagnostic_buttons_scaled(self):
        source = SOURCE.read_text()
        self.assertIn("FitRightButtonsToSafeArea(safe);", source)
        self.assertIn("private readonly RectTransform[] rightButtons = new RectTransform[3]", source)
        self.assertIn("RightButtonOffsets = { 78f, 126f, 174f }", source)
        self.assertIn("safe.height * 720f / Screen.height", source)
        self.assertIn("child.localScale = new Vector3(factor, factor, 1f)", source)
        self.assertIn("child.anchoredPosition = new Vector2(-8f * factor, -RightButtonOffsets[i] * factor)", source)
        self.assertIn("var child = rightButtons[i];", source)
        self.assertEqual(source.count("safeRoot.Find("), 3)
        update = source.split("private void Update()", 1)[1].split("private void Create()", 1)[0]
        fit = source.split("private void FitRightButtonsToSafeArea(", 1)[1].split("private static void FitPanel(", 1)[0]
        self.assertNotIn("new string[]", update + fit)
        self.assertNotIn("new float[]", update + fit)
        self.assertNotIn(".Find(", update + fit)


if __name__ == "__main__":
    unittest.main()
