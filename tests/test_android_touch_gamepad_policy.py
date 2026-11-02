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
    def test_path_restore_never_re_registers_an_active_control(self):
        self.assertIn('if (widget.controlPath == path) return;', SOURCE)
        self.assertIn('bool wasEnabled = widget.enabled;', SOURCE)
        self.assertIn('if (wasEnabled) widget.enabled = false;', SOURCE)
        self.assertIn('if (wasEnabled) widget.enabled = true;', SOURCE)
        self.assertIn('ApplyControlPath(stick, IsAllowed(path, StickPaths)', SOURCE)
        self.assertIn('ApplyControlPath(button, IsAllowed(path, ButtonPaths)', SOURCE)
        creation=SOURCE.split('canvasObject = new GameObject',1)[1]
        self.assertLess(creation.index('canvasObject.SetActive(false);'),creation.index('AddStick("Move"'))

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

    def test_touch_layout_editor_contract(self):
        self.assertIn("public bool SetLayoutEditMode(bool enable)", SOURCE)
        self.assertIn("stick.enabled = !enable;", SOURCE)
        self.assertIn("button.enabled = !enable;", SOURCE)
        self.assertIn("ScreenPointToLocalPointInRectangle", SOURCE)
        self.assertIn("pointer.pressEventCamera", SOURCE)
        self.assertIn("PlayerPrefs.SetFloat(LayoutKey + label + \".x\"", SOURCE)
        self.assertIn("PlayerPrefs.SetFloat(LayoutKey + selected + \".size\"", SOURCE)
        self.assertIn("PlayerPrefs.SetFloat(LayoutKey + selected + \".opacity\"", SOURCE)
        self.assertIn("PlayerPrefs.DeleteKey", SOURCE)
        self.assertIn('PlayerPrefs.DeleteKey(key + "binding")', SOURCE)
        self.assertIn("public void CycleSelectedBinding(int delta)", SOURCE)
        self.assertIn("if (!editing || selected == null || !surfaces.ContainsKey(selected)) return;", SOURCE)
        self.assertIn('PlayerPrefs.SetString(LayoutKey + selected + ".binding"', SOURCE)
        self.assertIn('PlayerPrefs.GetString(LayoutKey + label + ".binding", defaultPaths[label])', SOURCE)
        self.assertIn("IsAllowed(path, StickPaths)", SOURCE)
        self.assertIn("IsAllowed(path, ButtonPaths)", SOURCE)
        self.assertIn("touchGamepad.CycleSelectedBinding(-1)", DIAGNOSTICS)
        self.assertIn("touchGamepad.CycleSelectedBinding(1)", DIAGNOSTICS)
        self.assertIn("float.IsNaN(value) || float.IsInfinity(value)", SOURCE)
        self.assertIn("private void ClampControlToSafeArea(string label)", SOURCE)
        self.assertIn("ClampAllControlsToSafeArea();", SOURCE)
        self.assertIn("Canvas.ForceUpdateCanvases();", SOURCE)
        self.assertIn("rect.rect.width / (2f * area.width)", SOURCE)
        self.assertIn("rect.rect.height / (2f * area.height)", SOURCE)
        self.assertIn("if (enabled)", SOURCE)
        self.assertIn("UpdateSafeArea();", SOURCE)
        self.assertIn("AuditVirtualBindings();", SOURCE)
        self.assertIn("opened = false; // Drag controls with report panel closed.", DIAGNOSTICS)
        self.assertIn("touchGamepad.SetLayoutEditMode(startEdit)", DIAGNOSTICS)

    def test_safe_area_cache_waits_for_first_active_canvas_layout(self):
        # EnsureCanvas creates an inactive root. ForceUpdateCanvases cannot
        # measure its RectTransform until SetVisible activates the hierarchy.
        update = SOURCE.split("private void UpdateSafeArea()", 1)[1].split(
            "// Read-only evidence", 1)[0]
        self.assertIn("!canvasObject.activeInHierarchy", update)
        self.assertLess(update.index("!canvasObject.activeInHierarchy"),
                        update.index("lastWidth = Screen.width;"))
        self.assertLess(update.index("lastWidth = Screen.width;"),
                        update.index("Canvas.ForceUpdateCanvases();"))
        show = SOURCE.split("public bool SetVisible(bool enabled)", 1)[1].split(
            "private bool EnsureCanvas()", 1)[0]
        self.assertLess(show.index("canvasObject.SetActive(enabled);"),
                        show.index("UpdateSafeArea();"))
        create = SOURCE.split("private bool EnsureCanvas()", 1)[1].split(
            "private RectTransform AddSurface", 1)[0]
        self.assertLess(create.index("canvasObject.SetActive(false);"),
                        create.index("UpdateSafeArea();"))

    def test_virtual_control_audit_reads_original_enabled_actions_without_rebinding(self):
        # The API exists in Input System 1.7.0. A source contract is NOT a
        # Unity compile or evidence of gameplay responding to touch.
        self.assertIn("InputSystem.ListEnabledActions(enabledActionAudit);", SOURCE)
        self.assertIn("widget.control", SOURCE)
        self.assertIn("current == virtualControl", SOURCE)
        self.assertIn("current = current.parent", SOURCE)
        self.assertIn("enabledActionMatches=", SOURCE)
        self.assertIn("controlsWithEnabledAction=", SOURCE)
        self.assertIn("gameplayResponseVerified=false", SOURCE)
        self.assertIn("if (!enable) AuditVirtualBindings();", SOURCE)
        self.assertIn("SceneManager.GetActiveScene().handle != lastAuditedSceneHandle", SOURCE)
        self.assertNotIn("InputSystem.DisableAllEnabledActions", SOURCE)
        self.assertNotIn("SwitchCurrentControlScheme", SOURCE)

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


    def test_mode_transition_releases_stale_pointer_capture(self):
        mode = SOURCE.split("public bool SetLayoutEditMode(bool enable)", 1)[1].split(
            "private static float SafeFloat", 1)[0]
        self.assertIn("if (editing != enable)", mode)
        self.assertIn("handle.CancelCapture();", mode)
        self.assertLess(mode.index("handle.CancelCapture();"), mode.index("editing = enable;"))
        handle = SOURCE.split("public sealed class AndroidTouchLayoutHandle", 1)[1]
        self.assertIn("internal void CancelCapture()", handle)
        self.assertIn("private void OnDisable()", handle)
        self.assertIn("CancelCapture();", handle)

    def test_reset_cancels_inflight_drag_before_restoring_defaults(self):
        reset = SOURCE.split("public void ResetLayout()", 1)[1].split(
            "public void AdjustSelectedSize", 1)[0]
        self.assertIn("handle.CancelCapture();", reset)
        self.assertLess(reset.index("handle.CancelCapture();"),
                        reset.index("PlayerPrefs.DeleteKey"))
        self.assertLess(reset.index("handle.CancelCapture();"),
                        reset.index("RestoreLayout();"))

    def test_selection_only_tap_does_not_destroy_default_anchor_offset(self):
        self.assertIn("internal bool Drag(string label, PointerEventData pointer)", SOURCE)
        self.assertIn("dragged |= overlay.Drag(label, pointer);", SOURCE)
        self.assertIn("if (dragged && overlay != null && overlay.Editing)", SOURCE)
        self.assertIn("dragged = false;", SOURCE)
        self.assertIn("return true;", SOURCE.split(
            "internal bool Drag(string label, PointerEventData pointer)", 1)[1].split(
            "internal void SavePosition", 1)[0])

    def test_edit_drag_pointer_capture_and_release_contract(self):
        self.assertIn("IEndDragHandler, IPointerUpHandler", SOURCE)
        self.assertIn("activePointerId != NoPointer", SOURCE)
        self.assertIn("activePointerId == pointer.pointerId", SOURCE)
        self.assertIn("if (activePointerId != pointer.pointerId) return;", SOURCE)
        # A selection-only tap must never persist a default anchor without its offset.
        # Only a successful drag may save the new position.
        self.assertIn("if (dragged && overlay != null && overlay.Editing) overlay.SavePosition(label);", SOURCE)
        self.assertIn("public void OnPointerUp(PointerEventData pointer)", SOURCE)
        self.assertIn("public void OnEndDrag(PointerEventData pointer)", SOURCE)
        self.assertEqual(SOURCE.count("FinishPointer(pointer);"), 2)
        self.assertIn("private void OnDisable()", SOURCE)
        self.assertIn("activePointerId = NoPointer;", SOURCE)


if __name__ == "__main__":
    unittest.main()
