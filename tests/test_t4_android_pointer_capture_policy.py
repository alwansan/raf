"""T4 input policy: static integration guard, not Android device acceptance."""
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BRIDGE = (ROOT / "android-port/Runtime/Platform/AndroidPhysicalMouseCapture.cs").read_text()
DELTA = (ROOT / "android-port/Runtime/Platform/PhysicalMouseDeltaAccumulator.cs").read_text()
BOOTSTRAP = (ROOT / "android-port/Runtime/Platform/AndroidTestDiagnostics.cs").read_text()
INPUT_PATCH = (ROOT / "scripts/t4_adapt_original_mouse_axes.py").read_text()
BUTTON_PATCH = (ROOT / "scripts/t4_adapt_original_mouse_buttons_wheel.py").read_text()
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

    def test_original_legacy_button_wheel_sites_are_exactly_staged(self):
        # Authentic immutable ZIP2 call census: four Down, six Held, two Up,
        # six Mouse ScrollWheel axis and two mouseScrollDelta property reads.
        self.assertIn('EXPECTED = {"down": 4, "held": 6, "up": 2, "wheel_axis": 6, "scroll_delta": 2}', BUTTON_PATCH)
        self.assertIn("assert_original(original_dll)", BUTTON_PATCH)
        self.assertIn("if count != EXPECTED or not replacements:", BUTTON_PATCH)
        self.assertEqual(NATIVE.count("python3 -m scripts.t4_adapt_original_mouse_buttons_wheel"), 1)
        self.assertLess(NATIVE.index("python3 -m scripts.t4_adapt_original_mouse_axes"),
                        NATIVE.index("python3 -m scripts.t4_adapt_original_mouse_buttons_wheel"))
        for api in ("GetMouseButton(int index)", "GetMouseButtonDown(int index)",
                    "GetMouseButtonUp(int index)", "GetMouseScrollDelta()"):
            self.assertIn("public static " + ("Vector2 " if api == "GetMouseScrollDelta()" else "bool ") + api, BRIDGE)
        self.assertIn('axis == "Mouse ScrollWheel"', BRIDGE)
        self.assertIn("return TryCapturedFrame(out frame) && frame.Down(index);", BRIDGE)
        self.assertIn("if (legacy) return true;", BRIDGE)
        self.assertIn("if (legacy.x != 0f || legacy.y != 0f) return legacy;", BRIDGE)
        self.assertIn("buttonWheel.Reset();", BRIDGE)
        self.assertNotIn("InputSystem.QueueStateEvent", BRIDGE)
        self.assertIn("if (buttonWheel.Record(action,source,changedButton,heldButton,vertical,horizontal))", BRIDGE)
        self.assertIn("nativeCaptured = true;", BRIDGE)
        self.assertIn("PhysicalMouseButtonWheelFrame.SourceIsPhysical(source)", (ROOT / "android-port/Runtime/Platform/PhysicalMouseMotionSource.cs").read_text())

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
        self.assertIn('int action = motionEvent.Call<int>("getActionMasked");', BRIDGE)
        # Mouse movement still enters the original relative-delta path only.
        self.assertIn("if (action != PhysicalMouseMotionSource.ActionMove)", BRIDGE)
        # Button/wheel callbacks are observed, never consumed or converted to
        # synthetic Unity mouse button/scroll state in this diagnostic change.
        listener = BRIDGE.split("public bool onCapturedPointer(", 1)[1].split(
            "private bool RecordCapturedMotion", 1
        )[0]
        nonmove = listener.split("if (action != PhysicalMouseMotionSource.ActionMove)", 1)[1].split(
            "int source = motionEvent.Call<int>(\"getSource\");", 1
        )[0]
        self.assertIn("PhysicalMouseActionEvidence.IsAction(action)", nonmove)
        self.assertIn("owner.RecordCapturedAction(", nonmove)
        self.assertIn("return false;", nonmove)
        self.assertNotIn("QueueStateEvent", nonmove)
        self.assertNotIn("deltas.Push", nonmove)
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



    def test_stale_queued_release_cannot_revoke_new_capture(self):
        release = BRIDGE.split("private void ReleaseCapture()", 1)[1].split(
            "private void OnApplicationPause", 1)[0]
        self.assertIn("int releaseEpoch = Volatile.Read(ref epoch);", release)
        self.assertIn("OnAndroidUi(() =>", release)
        self.assertIn(
            "if (releaseEpoch != Volatile.Read(ref epoch) || requested)",
            release,
        )
        guard = release.index("if (releaseEpoch != Volatile.Read(ref epoch) || requested)")
        diagnostic = release.index('ReportReleaseOutcome("superseded_generation")', guard)
        exit_stale = release.index("return;", diagnostic)
        native_call = release.index('view.Call("releasePointerCapture")')
        self.assertLess(guard, diagnostic)
        self.assertLess(diagnostic, exit_stale)
        self.assertLess(exit_stale, native_call)

    def test_captured_packet_source_contract_matches_android_api26(self):
        source = (ROOT / "android-port/Runtime/Platform/PhysicalMouseMotionSource.cs").read_text()
        self.assertIn("public const int MouseRelative = 131076;", source)
        self.assertIn("public const int Touchpad = 1048584;", source)
        self.assertIn("public const int AxisRelativeX = 27;", source)
        self.assertIn("public const int AxisRelativeY = 28;", source)
        self.assertIn("return Kind.Ignore;", source)
        self.assertIn("Math.Abs(x) <= 10000f", source)

    def test_captured_mouse_uses_relative_getx_and_batched_samples(self):
        listener = BRIDGE.split("public bool onCapturedPointer(AndroidJavaObject view, AndroidJavaObject motionEvent)", 1)[1].split(
            "private bool RecordCapturedMotion", 1)[0]
        self.assertIn('motionEvent.Call<int>("getSource")', listener)
        self.assertIn("PhysicalMouseMotionSource.Classify(source, deviceSources)", listener)
        self.assertIn("kind == PhysicalMouseMotionSource.Kind.Ignore", listener)
        self.assertIn("PhysicalMouseMotionSource.ValidHistory(historyCount)", listener)
        self.assertIn("for (int h = 0; h < historyCount; h++)", listener)
        self.assertIn('motionEvent.Call<float>("getHistoricalX", h)', listener)
        self.assertIn('motionEvent.Call<float>("getHistoricalY", h)', listener)
        self.assertIn('motionEvent.Call<float>("getX")', listener)
        self.assertIn('motionEvent.Call<float>("getY")', listener)

    def test_touchpad_uses_relative_axes_not_absolute_position(self):
        listener = BRIDGE.split("public bool onCapturedPointer(AndroidJavaObject view, AndroidJavaObject motionEvent)", 1)[1].split(
            "private bool RecordCapturedMotion", 1)[0]
        self.assertIn("kind == PhysicalMouseMotionSource.Kind.Mouse", listener)
        self.assertIn('motionEvent.Call<float>("getHistoricalAxisValue",', listener)
        self.assertIn('motionEvent.Call<float>("getAxisValue",', listener)
        self.assertIn("PhysicalMouseMotionSource.AxisRelativeX", listener)
        self.assertIn("PhysicalMouseMotionSource.AxisRelativeY", listener)
        self.assertIn("return owner.RecordCapturedMotion(listenerEpoch, dx, dy);", listener)
        record = BRIDGE.split("private bool RecordCapturedMotion(int listenerEpoch, float dx, float dy)", 1)[1].split(
            "public static CursorLockMode ApplyCursorLock", 1)[0]
        self.assertIn("PhysicalMouseMotionSource.ValidDelta(dx, dy)", record)

    def test_new_source_is_in_both_managed_compilers_and_native_export(self):
        native = "AndroidPhysicalMouseCapture.cs PhysicalMouseDeltaAccumulator.cs PhysicalMouseMotionSource.cs"
        self.assertIn(native, NATIVE)
        self.assertIn("'PhysicalMouseMotionSource.cs'", COMPILER)
        project = (ROOT / "android-port/Tests/PhysicalMouse/PhysicalMouse.csproj").read_text()
        abi_project = (ROOT / "android-port/Tests/PhysicalMouse/UnityBridgeCompile.csproj").read_text()
        self.assertIn("PhysicalMouseMotionSource.cs", project)
        self.assertIn("PhysicalMouseMotionSource.cs", abi_project)



    def test_old_android_move_cannot_cross_request_generation(self):
        source = (ROOT / "android-port/Runtime/Platform/PhysicalMouseMotionSource.cs").read_text()
        self.assertIn("public static bool AcceptEpoch(", source)
        self.assertIn("requested && listenerEpoch == activeEpoch", source)
        self.assertIn("private readonly int listenerEpoch;", BRIDGE)
        self.assertIn("new CapturedListener(this, currentEpoch)", BRIDGE)
        self.assertIn("listener = requestListener;", BRIDGE)
        self.assertIn('view.Call("setOnCapturedPointerListener", requestListener)', BRIDGE)

    def test_callback_prefilters_generation_and_rechecks_inside_capture_lock(self):
        listener = BRIDGE.split(
            "public bool onCapturedPointer(AndroidJavaObject view, AndroidJavaObject motionEvent)", 1
        )[1].split("private bool RecordCapturedMotion", 1)[0]
        self.assertIn("PhysicalMouseMotionSource.AcceptEpoch(listenerEpoch,", listener)
        self.assertIn("Volatile.Read(ref owner.epoch)", listener)
        self.assertIn("owner.RecordCapturedMotion(listenerEpoch, dx, dy)", listener)
        record = BRIDGE.split(
            "private bool RecordCapturedMotion(int listenerEpoch, float dx, float dy)", 1
        )[1].split("public static CursorLockMode ApplyCursorLock", 1)[0]
        self.assertIn("lock (captureGate)", record)
        self.assertIn("PhysicalMouseMotionSource.AcceptEpoch(listenerEpoch, epoch, requested)", record)
        self.assertIn("deltas.Push(dx, dy);", record)
        self.assertLess(record.index("AcceptEpoch"), record.index("deltas.Push"))

    def test_prior_queued_release_implementation_is_retained(self):
        release = BRIDGE.split("private void ReleaseCapture()", 1)[1].split(
            "private void OnApplicationPause", 1
        )[0]
        self.assertIn("int releaseEpoch = Volatile.Read(ref epoch);", release)
        self.assertIn("if (releaseEpoch != Volatile.Read(ref epoch) || requested)", release)



    def test_touchpad_event_must_cross_check_device_sources(self):
        source = (ROOT / "android-port/Runtime/Platform/PhysicalMouseMotionSource.cs").read_text()
        self.assertIn("public const int Mouse = 8194;", source)
        self.assertIn("public static Kind Classify(int eventSource, int deviceSources)", source)
        self.assertIn("if (eventSource == Mouse && deviceSources >= 0 &&", source)
        self.assertIn("(deviceSources & Touchpad) == Touchpad", source)
        self.assertIn("if (direct != Kind.Ignore) return direct;", source)

    def test_native_touchpad_getdevice_is_bounded_to_mouse_event(self):
        listener = BRIDGE.split(
            "public bool onCapturedPointer(AndroidJavaObject view, AndroidJavaObject motionEvent)", 1
        )[1].split("private bool RecordCapturedMotion", 1)[0]
        self.assertIn('int source = motionEvent.Call<int>("getSource");', listener)
        self.assertIn("if (source == PhysicalMouseMotionSource.Mouse)", listener)
        self.assertIn('using (var device = motionEvent.Call<AndroidJavaObject>("getDevice"))', listener)
        self.assertIn('deviceSources = device.Call<int>("getSources");', listener)
        self.assertIn("PhysicalMouseMotionSource.Classify(source, deviceSources)", listener)
        self.assertLess(
            listener.index('if (source == PhysicalMouseMotionSource.Mouse)'),
            listener.index('deviceSources = device.Call<int>("getSources");'),
        )
        self.assertLess(
            listener.index("PhysicalMouseMotionSource.Classify(source, deviceSources)"),
            listener.index("if (kind == PhysicalMouseMotionSource.Kind.Ignore)"),
        )

    def test_touchpad_source_guard_preserves_original_mouse_and_screen(self):
        listener = BRIDGE.split(
            "public bool onCapturedPointer(AndroidJavaObject view, AndroidJavaObject motionEvent)", 1
        )[1].split("private bool RecordCapturedMotion", 1)[0]
        self.assertIn("kind == PhysicalMouseMotionSource.Kind.Mouse", listener)
        self.assertIn("PhysicalMouseMotionSource.AxisRelativeX", listener)
        self.assertIn("PhysicalMouseMotionSource.AxisRelativeY", listener)
        self.assertIn("return owner.RecordCapturedMotion(listenerEpoch, dx, dy);", listener)
        self.assertIn("if (motionEvent != null) motionEvent.Dispose();", listener)
        self.assertIn("if (view != null) view.Dispose();", listener)



if __name__ == "__main__":
    unittest.main()
