"""T4 input policy: static integration guard, not Android device acceptance."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = (ROOT / "android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs").read_text()
DELTA = (ROOT / "android-port/Runtime/Platform/PhysicalMouseDeltaAccumulator.cs").read_text()
BOOTSTRAP = (ROOT / "android-port/Runtime/Platform/AndroidTestDiagnostics.cs").read_text()
INPUT_PATCH = (ROOT / "scripts/t4_adapt_original_mouse_axes.py").read_text()
NATIVE = (ROOT / ".github/workflows/raft-unity-editor-android-import.yml").read_text()
COMPILER = (ROOT / "scripts/verify_android_offline_candidate.py").read_text()
TOUCH = (ROOT / "android-port/Runtime/Platform/AndroidTouchPointer.cs").read_text()


class AndroidPhysicalMouseIntegrationPolicy(unittest.TestCase):
    def test_original_axis_and_cursor_assignment_gates(self):
        self.assertIn('EXPECTED = {"mouse_x": 4, "mouse_y": 4, "cursor_lock": 2}', INPUT_PATCH)
        self.assertIn("assert_original(original_dll)", INPUT_PATCH)
        self.assertIn("if counts != EXPECTED:", INPUT_PATCH)
        self.assertIn("if project_assets and \"Assembly-CSharp\" not in", INPUT_PATCH)
        self.assertIn("ApplyCursorLock", BRIDGE)
        self.assertIn("Input.GetAxisRaw(axis) : Input.GetAxis(axis)", BRIDGE)

    def test_bridge_copies_into_native_unity_staging_and_managed_check(self):
        self.assertEqual(NATIVE.count("python3 -m scripts.t4_adapt_original_mouse_axes"), 1)
        self.assertIn("AndroidPhysicalMouseCapture.cs PhysicalMouseDeltaAccumulator.cs", NATIVE)
        self.assertIn("host.AddComponent<AndroidPhysicalMouseCapture>();", BOOTSTRAP)
        self.assertIn("'AndroidPhysicalMouseCapture.cs', 'PhysicalMouseDeltaAccumulator.cs'", COMPILER)
        self.assertIn("--original-dll \"$GITHUB_WORKSPACE/Raft/Raft_Data/Managed/Assembly-CSharp.dll\"", NATIVE)
        self.assertLess(NATIVE.index("python3 -m scripts.instrument_android_runtime_operations"),
                        NATIVE.index("python3 -m scripts.t4_adapt_original_mouse_axes"))

    def test_pointer_capture_only_on_android_API26_and_gameplay_lock(self):
        self.assertIn('version.GetStatic<int>("SDK_INT") >= 26', BRIDGE)
        self.assertIn("originalLockIntent", BRIDGE)
        self.assertIn("PhysicalMousePresent()", BRIDGE)
        self.assertIn("view.Call(\"requestPointerCapture\")", BRIDGE)
        self.assertIn("view.Call(\"releasePointerCapture\")", BRIDGE)
        self.assertIn("if (!value) ReleaseCapture();", BRIDGE)
        self.assertIn("if (value) ReleaseCapture();", BRIDGE)
        self.assertIn("Input.GetKeyDown(KeyCode.Escape)", BRIDGE)

    def test_input_events_preserve_touch_and_physical_mouse_clicks(self):
        self.assertIn('base("android.view.View$OnCapturedPointerListener")', BRIDGE)
        self.assertIn('getActionMasked") != 2', BRIDGE)
        self.assertIn("return false; // ACTION_MOVE only.", BRIDGE)
        self.assertIn("return false; // Fail open to Unity", BRIDGE)
        self.assertIn('mouse.name != VirtualTouchMouse', BRIDGE)
        self.assertIn('Input.simulateMouseWithTouches = false;', TOUCH)
        self.assertIn('MouseButton.Left', TOUCH)
        self.assertNotIn('InputSystem.RemoveDevice', BRIDGE)
        self.assertNotIn('InputSystem.QueueStateEvent', BRIDGE)

    def test_ui_callback_closes_transient_jni_handles(self):
        self.assertIn("motionEvent.Dispose()", BRIDGE)
        self.assertIn("view.Dispose()", BRIDGE)
        self.assertIn("new AndroidJavaRunnable(() => work())", BRIDGE)
        self.assertIn("Math.Abs(x) > 10000f", DELTA)

    def test_no_gameplay_claim_in_native_source(self):
        self.assertIn("deviceDirectionVerified=false", BRIDGE)
        self.assertIn("requiresDeviceConfirmation=true", BRIDGE)
        self.assertNotIn("WorldHasBeenRecieved", BRIDGE)


    def test_unconfirmed_capture_never_hijacks_legacy_axes(self):
        axis = BRIDGE.split("private static float Axis(string axis, bool raw)", 1)[1].split(
            "private void OnEnable", 1)[0]
        self.assertIn("lock (current.captureGate)", axis)
        self.assertIn("current.requested && current.nativeCaptured && current.nativeHasMotion", axis)
        self.assertIn("return raw ? Input.GetAxisRaw(axis) : Input.GetAxis(axis);", axis)

    def test_native_revocation_clears_relative_motion_atomically(self):
        observed = BRIDGE.split("private void ObserveNativeCapture(int token, bool captured)", 1)[1].split(
            "private void ProbeCapturedPointer()", 1)[0]
        self.assertIn("lock (captureGate)", observed)
        self.assertIn("!requested || epoch != token", observed)
        self.assertIn("nativeCaptured = captured;", observed)
        self.assertIn("nativeHasMotion = false;", observed)
        self.assertIn("deltas.Reset();", observed)
        self.assertIn("if (lost) Interlocked.Increment(ref captureLossCount);", observed)

    def test_capture_status_probed_on_android_ui_thread(self):
        probe = BRIDGE.split("private void ProbeCapturedPointer()", 1)[1].split(
            "private void RequestCapture()", 1)[0]
        self.assertIn("OnAndroidUi(() =>", probe)
        self.assertIn('activity.Call<AndroidJavaObject>("getCurrentFocus")', probe)
        self.assertIn('view.Call<bool>("hasPointerCapture")', probe)
        self.assertIn("ObserveNativeCapture(token, active)", probe)
        self.assertIn("ObserveNativeCapture(token, false)", probe)
        self.assertIn("token != Volatile.Read(ref epoch)", probe)

    def test_loss_retries_and_release_cancels_stale_updates(self):
        update = BRIDGE.split("private void Update()", 1)[1].split(
            "private static void OnAndroidUi", 1)[0]
        release = BRIDGE.split("private void ReleaseCapture()", 1)[1].split(
            "private void OnApplicationPause", 1)[0]
        self.assertIn("if (!nativeCaptured && Time.unscaledTime >= nextRequestTime)", update)
        self.assertIn("nextProbeTime = Time.unscaledTime + 0.15f;", update)
        self.assertIn("ProbeCapturedPointer();", update)
        self.assertIn("physical_mouse_capture_lost", update)
        self.assertIn("lock (captureGate)", release)
        self.assertIn("epoch++;", release)
        self.assertIn("requested = nativeHasMotion = nativeCaptured = false;", release)
        self.assertIn("deltas.Reset();", release)



if __name__ == "__main__":
    unittest.main()
