"""T4 source-only Android immersive bars integration and safety checks.

These checks do NOT establish that Android hid any bars on real hardware.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
POLICY = (ROOT / "android-port/Runtime/Platform/AndroidSystemBarPolicy.cs").read_text()
RUNTIME = (ROOT / "android-port/Runtime/Platform/AndroidImmersiveSystemBars.cs").read_text()
NATIVE = (ROOT / ".github/workflows/raft-unity-editor-android-import.yml").read_text()
VERIFY = (ROOT / "scripts/verify_android_offline_candidate.py").read_text()


class ImmersiveSystemBarsPolicyTests(unittest.TestCase):
    def test_android_only_and_initialization_without_touch_overlay(self):
        self.assertTrue(RUNTIME.startswith("#if UNITY_ANDROID && !UNITY_EDITOR"))
        self.assertIn("[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]", RUNTIME)
        self.assertIn('new GameObject("RaftAndroidImmersiveSystemBars")', RUNTIME)
        self.assertIn("Object.DontDestroyOnLoad(host);", RUNTIME)
        self.assertIn("host.AddComponent<AndroidImmersiveSystemBars>();", RUNTIME)

    def test_modern_insets_exact_os_controller(self):
        self.assertIn('new AndroidJavaClass("android.view.WindowInsets$Type")', RUNTIME)
        self.assertIn('window.Call<AndroidJavaObject>("getInsetsController")', RUNTIME)
        self.assertIn('types.CallStatic<int>("systemBars")', RUNTIME)
        self.assertIn('controller.Call("setSystemBarsBehavior",', RUNTIME)
        self.assertIn("AndroidSystemBarPolicy.TransientBarsBySwipe", RUNTIME)
        self.assertIn('controller.Call("hide", bars);', RUNTIME)
        self.assertIn("return sdk >= 30;", POLICY)

    def test_legacy_flags_only_add_and_preserve_unity_flags(self):
        self.assertIn('decor.Call<int>("getSystemUiVisibility")', RUNTIME)
        self.assertIn('decor.Call("setSystemUiVisibility", merged)', RUNTIME)
        self.assertIn("return existing | LegacyFullscreen", POLICY)
        self.assertIn("LegacyImmersiveSticky", POLICY)
        self.assertIn("LegacyHideNavigation", POLICY)
        self.assertIn("LegacyLayoutStable", POLICY)
        self.assertIn("LegacyLayoutFullscreen", POLICY)
        self.assertIn("LegacyLayoutHideNavigation", POLICY)
        self.assertNotIn("setFlags", RUNTIME)

    def test_focused_foreground_and_ui_thread_only(self):
        self.assertIn("AndroidSystemBarPolicy.ShouldApply(active, focused, paused)", RUNTIME)
        self.assertIn('activity.Call("runOnUiThread"', RUNTIME)
        self.assertIn("nextRefresh = Time.unscaledTime + 15f;", RUNTIME)
        self.assertIn("private void OnApplicationFocus(bool value)", RUNTIME)
        self.assertIn("private void OnApplicationPause(bool value)", RUNTIME)
        self.assertIn("private void OnDisable()", RUNTIME)
        self.assertIn("if (!value) ScheduleHide();", RUNTIME)

    def test_pending_runnable_never_hides_another_activity(self):
        self.assertIn("using System.Threading;", RUNTIME)
        self.assertIn('system.CallStatic<int>("identityHashCode", activity)', RUNTIME)
        self.assertIn("int queuedGeneration = Interlocked.Increment(ref hideGeneration);", RUNTIME)
        self.assertIn("int queuedActivityIdentity = ActivityIdentity(activity);", RUNTIME)
        self.assertIn("queuedGeneration != Volatile.Read(ref hideGeneration)", RUNTIME)
        self.assertIn("AndroidSystemBarPolicy.CanApplyQueuedHide(", RUNTIME)
        self.assertIn("queuedActivityIdentity, ActivityIdentity(current)", RUNTIME)
        self.assertLess(RUNTIME.index("AndroidSystemBarPolicy.CanApplyQueuedHide("),
                        RUNTIME.index('current.Call<AndroidJavaObject>("getWindow")'))
        self.assertIn("queuedGeneration != 0 && queuedGeneration == currentGeneration", POLICY)
        self.assertIn("queuedActivityIdentity != 0", POLICY)
        self.assertIn("queuedActivityIdentity == currentActivityIdentity", POLICY)

    def test_lifecycle_invalidates_old_queued_generation(self):
        for start, end in (("OnEnable()", "Update()"),
                           ("OnApplicationFocus(bool value)", "OnApplicationPause(bool value)"),
                           ("OnApplicationPause(bool value)", "OnDisable()")):
            body = RUNTIME.split("private void " + start, 1)[1].split("private void " + end, 1)[0]
            self.assertIn("Interlocked.Increment(ref hideGeneration);", body)
        self.assertIn("Interlocked.Increment(ref hideGeneration);",
                      RUNTIME.split("private void OnDisable()", 1)[1])
        self.assertNotIn("setSystemGestureExclusionRects", RUNTIME)

    def test_no_forced_os_escapes_and_no_display_changes(self):
        for forbidden in ("SetResolution", "Screen.fullScreen", "Screen.orientation",
                          "setSystemGestureExclusionRects", "disableBack", "disableHome",
                          'controller.Call("show"', "setPointerIcon", "Cursor.lockState",
                          "requestPointerCapture", "InputSystem", "MouseButton.Left"):
            self.assertNotIn(forbidden, RUNTIME)

    def test_native_project_and_managed_candidate_both_stage(self):
        self.assertIn("AndroidImmersiveSystemBars.cs AndroidSystemBarPolicy.cs", NATIVE)
        self.assertIn("'AndroidImmersiveSystemBars.cs', 'AndroidSystemBarPolicy.cs'", VERIFY)
        self.assertEqual(NATIVE.count("AndroidImmersiveSystemBars.cs"), 1)

    def test_own_dotnet_projects_test_policy_and_original_unity_abi(self):
        tests = ROOT / "android-port/Tests/ImmersiveBars"
        for p in ("ImmersiveBars.csproj", "UnityManagedCompile.csproj", "Program.cs"):
            self.assertTrue((tests / p).exists(), p)
        compile_project = (tests / "UnityManagedCompile.csproj").read_text()
        self.assertIn('DefineConstants>UNITY_ANDROID;', compile_project)
        self.assertIn('UnityEngine.CoreModule.dll', compile_project)
        self.assertIn('UnityEngine.AndroidJNIModule.dll', compile_project)
        self.assertIn('AndroidImmersiveSystemBars.cs', compile_project)


if __name__ == "__main__":
    unittest.main()
