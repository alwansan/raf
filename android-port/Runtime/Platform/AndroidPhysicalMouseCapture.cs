#if UNITY_ANDROID && !UNITY_EDITOR
using System;
using System.Threading;
using UnityEngine;
using UnityEngine.InputSystem;

namespace RaftAndroid.Platform
{
    // Physical Android mouse only. Does not touch the original EventSystem,
    // synthetic LEFT-touch mouse, PlayerInput, buttons or wheel.
    // Android 8+ View pointer capture is requested on Android's UI thread,
    // only after original game code explicitly requests a locked cursor.
    public sealed class AndroidPhysicalMouseCapture : MonoBehaviour
    {
        private const string VirtualTouchMouse = "RaftAndroidTouchLeft";
        private static AndroidPhysicalMouseCapture instance;
        private static int originalLockIntent;

        private readonly PhysicalMouseDeltaAccumulator deltas = new PhysicalMouseDeltaAccumulator();
        private CapturedListener listener;
        private bool focused = true, paused, supported;
        private volatile bool nativeHasMotion, requested;
        private int epoch, lastLoggedCount;
        private float nextRequestTime;

        private sealed class CapturedListener : AndroidJavaProxy
        {
            private readonly AndroidPhysicalMouseCapture owner;
            public CapturedListener(AndroidPhysicalMouseCapture owner)
                : base("android.view.View$OnCapturedPointerListener")
            { this.owner = owner; }

            public bool onCapturedPointer(AndroidJavaObject view, AndroidJavaObject motionEvent)
            {
                // This callback executes on Android's event thread, never Unity Update.
                // Returning false for button/scroll permits View's normal handler.
                try
                {
                    if (!owner.requested || motionEvent.Call<int>("getActionMasked") != 2)
                        return false; // ACTION_MOVE only.
                    float dx = motionEvent.Call<float>("getX");
                    float dy = motionEvent.Call<float>("getY");
                    owner.deltas.Push(dx, dy);
                    owner.nativeHasMotion = true;
                    return true;
                }
                catch (AndroidJavaException)
                {
                    return false; // Fail open to Unity's original handling.
                }
            }
        }

        public static CursorLockMode ApplyCursorLock(CursorLockMode mode)
        {
            // Preserve the original authored cursor-lock assignment exactly.
            Cursor.lockState = mode;
            Interlocked.Exchange(ref originalLockIntent,
                mode == CursorLockMode.Locked ? 1 : 0);
            return mode;
        }

        public static float GetAxis(string axis) { return Axis(axis, false); }
        public static float GetAxisRaw(string axis) { return Axis(axis, true); }

        private static float Axis(string axis, bool raw)
        {
            var current = instance;
            if (current != null && current.nativeHasMotion && current.requested &&
                (axis == "Mouse X" || axis == "Mouse Y"))
                return current.deltas.Sample(Time.frameCount, axis == "Mouse X");
            // No capture => identical legacy Unity input for mouse/keyboard.
            return raw ? Input.GetAxisRaw(axis) : Input.GetAxis(axis);
        }

        private void OnEnable()
        {
            if (instance != null && instance != this) { enabled = false; return; }
            instance = this;
            try
            {
                using (var version = new AndroidJavaClass("android.os.Build$VERSION"))
                    supported = version.GetStatic<int>("SDK_INT") >= 26;
                if (supported) listener = new CapturedListener(this);
            }
            catch (AndroidJavaException)
            {
                supported = false;
            }
        }

        private static bool PhysicalMousePresent()
        {
            if (!Input.mousePresent) return false;
            foreach (var mouse in Mouse.all)
                if (mouse != null && mouse.added && mouse.name != VirtualTouchMouse)
                    return true;
            return false;
        }

        private void Update()
        {
            if (!supported) return;
            // Escape offers an immediate physical exit even if original pause
            // transition sets cursor state on a subsequent frame.
            if (Input.GetKeyDown(KeyCode.Escape))
                Interlocked.Exchange(ref originalLockIntent, 0);
            bool shouldCapture = !paused && focused &&
                Volatile.Read(ref originalLockIntent) == 1 && PhysicalMousePresent();
            if (!shouldCapture)
            {
                if (requested || nativeHasMotion) ReleaseCapture();
                return;
            }
            if (Time.unscaledTime >= nextRequestTime)
            {
                nextRequestTime = Time.unscaledTime + 1.5f;
                RequestCapture();
            }
            int received = deltas.ReceivedCount;
            if (received >= lastLoggedCount + 120)
            {
                lastLoggedCount = received;
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("input",
                    "physical_mouse_relative", "events=" + received +
                    "; legacyAxes=true; deviceDirectionVerified=false");
            }
        }

        private static void OnAndroidUi(Action work)
        {
            using (var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
            using (var activity = player.GetStatic<AndroidJavaObject>("currentActivity"))
                activity.Call("runOnUiThread", new AndroidJavaRunnable(work));
        }

        private void RequestCapture()
        {
            requested = true;
            int currentEpoch = Interlocked.Increment(ref epoch);
            try
            {
                OnAndroidUi(() =>
                {
                    if (currentEpoch != Volatile.Read(ref epoch) || !requested) return;
                    try
                    {
                        using (var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
                        using (var activity = player.GetStatic<AndroidJavaObject>("currentActivity"))
                        using (var view = activity.Call<AndroidJavaObject>("getCurrentFocus"))
                        {
                            // Do not steal focus from Unity, nor trap the user
                            // when activity/menu does not own a focused view.
                            if (view == null || !view.Call<bool>("hasWindowFocus") ||
                                !view.Call<bool>("isFocused")) return;
                            view.Call("setOnCapturedPointerListener", listener);
                            if (!view.Call<bool>("hasPointerCapture"))
                                view.Call("requestPointerCapture");
                        }
                    }
                    catch (AndroidJavaException) { /* fallback to legacy mouse */ }
                });
            }
            catch (AndroidJavaException)
            {
                requested = false;
                nativeHasMotion = false;
                deltas.Reset();
            }
        }

        private void ReleaseCapture()
        {
            Interlocked.Increment(ref epoch);
            requested = false;
            nativeHasMotion = false;
            deltas.Reset();
            lastLoggedCount = 0;
            try
            {
                OnAndroidUi(() =>
                {
                    try
                    {
                        using (var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
                        using (var activity = player.GetStatic<AndroidJavaObject>("currentActivity"))
                        using (var view = activity.Call<AndroidJavaObject>("getCurrentFocus"))
                            if (view != null && view.Call<bool>("hasPointerCapture"))
                                view.Call("releasePointerCapture");
                    }
                    catch (AndroidJavaException) { /* focus-loss releases it */ }
                });
            }
            catch (AndroidJavaException) { }
        }

        private void OnApplicationPause(bool value)
        {
            paused = value;
            if (value) ReleaseCapture();
        }

        private void OnApplicationFocus(bool value)
        {
            focused = value;
            if (!value) ReleaseCapture();
        }

        private void OnDisable()
        {
            ReleaseCapture();
            if (instance == this) instance = null;
        }
    }
}
#endif
