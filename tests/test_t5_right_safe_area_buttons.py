"""Source contract for the owner's three right-side diagnostic buttons.

This is NOT an Android rendering/device test. It protects the safe-area
anchor and original callbacks from accidental layout regressions.
"""
from pathlib import Path
import re
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "android-port/Runtime/Platform/AndroidTouchUiPanel.cs"


class RightSideDiagnosticButtons(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source = SOURCE.read_text(encoding="utf-8")

    def test_three_buttons_use_right_helper_once(self):
        for label in ("Show Xbox", "Xbox layout", "Test report"):
            pattern = r'AddRightButton\\(safeRoot,\\s*"' + re.escape(label) + r'"'
            self.assertEqual(len(re.findall(pattern, self.source)), 1, label)

    def test_helper_anchors_right_inside_safe_root(self):
        s = self.source
        helper = s[s.index("private static void AddRightButton(Transform parent, string caption, float inset, float y, float width, Action pressed, out Text label)") :]
        helper = helper[:helper.index("private static void AddRightButton(Transform parent, string caption, float inset, float y, float width, Action pressed)")]
        self.assertIn("new Vector2(1, 1)", helper)
        self.assertIn("new Vector2(-inset, -y)", helper)
        self.assertIn("captionRect.anchorMin = Vector2.zero", helper)
        self.assertIn("captionRect.anchorMax = Vector2.one", helper)
        self.assertIn("captionRect.offsetMin = captionRect.offsetMax = Vector2.zero", helper)
        self.assertIn("safeRoot.anchorMin = new Vector2(safe.xMin / Screen.width", s)
        self.assertIn("safeRoot.anchorMax = new Vector2(safe.xMax / Screen.width", s)

    def test_buttons_preserve_original_callbacks(self):
        s = self.source
        self.assertIn("gamepad.SetVisible(!gamepad.Visible)", s)
        self.assertIn("gamepad.SetLayoutEditMode(!gamepad.Editing)", s)
        self.assertIn("reportOpen = !reportOpen", s)


if __name__ == "__main__":
    unittest.main()
