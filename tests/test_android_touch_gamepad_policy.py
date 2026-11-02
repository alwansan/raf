"""Source contract for an opt-in, reversible touch-to-original-gamepad bridge.

This does not prove a Unity import, gameplay mapping, multitouch, or device behavior.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "android-port/Runtime/Platform/AndroidTouchGamepadOverlay.cs").read_text(encoding="utf-8")
DIAGNOSTICS = (ROOT / "android-port/Runtime/Platform/AndroidTestDiagnostics.cs").read_text(encoding="utf-8")
WORKFLOW = (ROOT / ".github/workflows/raft-unity-editor-android-import.yml").read_text(encoding="utf-8")


class TouchGamepadContract(unittest.TestCase):
    def test_android_only_and_opt_in(self):
        self.assertTrue(SOURCE.startswith("#if UNITY_ANDROID && !UNITY_EDITOR"))
        self.assertIn("public bool SetVisible(bool enabled)", SOURCE)
        self.assertIn("canvasObject.SetActive(false);", SOURCE)
        self.assertIn("host.AddComponent<AndroidTouchGamepadOverlay>();", DIAGNOSTICS)
        self.assertIn("touchGamepad.SetVisible(!touchGamepad.Visible);", DIAGNOSTICS)
        self.assertIn("AndroidTouchGamepadOverlay.cs", WORKFLOW)
        original_compile = (ROOT / "scripts/verify_android_offline_candidate.py").read_text(encoding="utf-8")
        self.assertIn("\'AndroidTouchGamepadOverlay.cs\'", original_compile)

    def test_original_input_module_and_external_peripherals_preserved(self):
        self.assertIn("GetComponent<InputSystemUIInputModule>()", SOURCE)
        self.assertNotIn("new GameObject(\"EventSystem\"", SOURCE)
        self.assertNotIn("AddComponent<PlayerInput>", SOURCE)
        self.assertNotIn("InputSystem.RemoveDevice", SOURCE)
        self.assertNotIn("StandaloneInputModule", SOURCE)
        self.assertIn("SetVisible(false);", SOURCE)

    def test_gamepad_paths_and_notch_safe_area(self):
        for path in ("<Gamepad>/leftStick", "<Gamepad>/rightStick",
                     "<Gamepad>/buttonSouth", "<Gamepad>/buttonNorth",
                     "<Gamepad>/buttonWest", "<Gamepad>/rightTrigger",
                     "<Gamepad>/start"):
            self.assertIn(path, SOURCE)
        self.assertIn("typeof(GraphicRaycaster)", SOURCE)
        self.assertIn("image.raycastTarget = true;", SOURCE)
        self.assertIn("text.raycastTarget = false;", SOURCE)
        self.assertIn("Screen.safeArea", SOURCE)
        self.assertIn("stick.useIsolatedInputActions = true;", SOURCE)
        self.assertIn("area.xMin / Screen.width", SOURCE)
        self.assertIn("area.yMax / Screen.height", SOURCE)


if __name__ == "__main__":
    unittest.main()
