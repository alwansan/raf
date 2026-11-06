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
        private volatile bool nativeHasMotion, requested, nativeCaptured;
        private readonly object captureGate = new object();
        private int epoch, lastLoggedCount, captureLossCount, loggedLossCount;
        private int captureViewIdentity, mismatchedViewEpoch, loggedMismatchedViewEpoch;
        private float nextRequestTime, nextProbeTime;

        private sealed class CapturedListener : AndroidJavaProxy
        {
            private readonly AndroidPhysicalMouseCapture owner;
            private readonly int listenerEpoch;
            public CapturedListener(AndroidPhysicalMouseCapture owner, int listenerEpoch)
                : base("android.view.View$OnCapturedPointerListener")
            {
                this.owner = owner;
                this.listenerEpoch = listenerEpoch;
            }

            public bool onCapturedPointer(AndroidJavaObject view, AndroidJavaObject motionEvent)
            {
                // This callback executes on Android's event thread, never Unity Update.
                // Returning false for button/scroll permits View's normal handler.
                try
                {
                    if (!PhysicalMouseMotionSource.AcceptEpoch(listenerEpoch,
                            Volatile.Read(ref owner.epoch), owner.requested) ||
                        motionEvent.Call<int>("getActionMasked") != 2)
                        return false; // ACTION_MOVE only and current generation.
                    int source = motionEvent.Call<int>("getSource");
                    int deviceSources = 0;
                    // Android touchpad MotionEvent.getSource() normally reports
                    // SOURCE_MOUSE, not SOURCE_TOUCHPAD. Only for this source,
                    // consult its real InputDevice capabilities; never treat
                    // a touchscreen position as a camera-relative movement.
                    if (source == PhysicalMouseMotionSource.Mouse)
                    {
                        using (var device = motionEvent.Call<AndroidJavaObject>("getDevice"))
                        {
                            if (device != null)
                                deviceSources = device.Call<int>("getSources");
                        }
                    }
                    var kind = PhysicalMouseMotionSource.Classify(source, deviceSources);
                    if (kind == PhysicalMouseMotionSource.Kind.Ignore)
                        return false; // Unknown mouse/touch remains Unity-owned.
                    int historyCount = motionEvent.Call<int>("getHistorySize");
                    if (!PhysicalMouseMotionSource.ValidHistory(historyCount))
                        return false; // Never block Android UI on unbounded batched packets.
                    float dx = 0f, dy = 0f;
                    // Android batches historical deltas; reading only the final
                    // sample loses actual physical movement under load.
                    for (int h = 0; h < historyCount; h++)
                    {
                        if (kind == PhysicalMouseMotionSource.Kind.Mouse)
                        {
                            dx += motionEvent.Call<float>("getHistoricalX", h);
                            dy += motionEvent.Call<float>("getHistoricalY", h);
                        }
                        else
                        {
                            dx += motionEvent.Call<float>("getHistoricalAxisValue",
                                PhysicalMouseMotionSource.AxisRelativeX, h);
                            dy += motionEvent.Call<float>("getHistoricalAxisValue",
                                PhysicalMouseMotionSource.AxisRelativeY, h);
                        }
                    }
                    if (kind == PhysicalMouseMotionSource.Kind.Mouse)
                    {
                        // SOURCE_MOUSE_RELATIVE: getX/Y are deltas, not screen pixels.
                        dx += motionEvent.Call<float>("getX");
                        dy += motionEvent.Call<float>("getY");
                    }
                    else
                    {
                        // SOURCE_TOUCHPAD: getX/Y are absolute positions; use
                        // relative axes instead to prevent huge camera jumps.
                        dx += motionEvent.Call<float>("getAxisValue",
                            PhysicalMouseMotionSource.AxisRelativeX);
                        dy += motionEvent.Call<float>("getAxisValue",
                            PhysicalMouseMotionSource.AxisRelativeY);
                    }
                    return owner.RecordCapturedMotion(listenerEpoch, dx, dy);
                }
                catch (AndroidJavaException)
                {
                    return false; // Fail open to Unity's original handling.
                }
                finally
                {
                    // AndroidJavaProxy creates JNI wrappers per callback. Avoid
                    // retaining references for every high-frequency mouse move.
                    if (motionEvent != null) motionEvent.Dispose();
                    if (view != null) view.Dispose();
                }
            }
        }

        private bool RecordCapturedMotion(int listenerEpoch, float dx, float dy)
        {
            lock (captureGate)
            {
                if (!PhysicalMouseMotionSource.AcceptEpoch(listenerEpoch, epoch, requested) ||
                    !PhysicalMouseMotionSource.ValidDelta(dx, dy))
                    return false;
                deltas.Push(dx, dy);
                nativeCaptured = nativeHasMotion = true;
                return true;
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
            if (current != null && (axis == "Mouse X" || axis == "Mouse Y"))
            {
                lock (current.captureGate)
                {
                    if (current.requested && current.nativeCaptured && current.nativeHasMotion)
                        return current.deltas.Sample(Time.frameCount, axis == "Mouse X");
                }
            }
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
                // Each pointer-capture request installs its own generation-bound
                // proxy. OnEnable has no capture request and no listener yet.
            }
            catch (AndroidJavaException)
            {
                supported = false;
            }
        }

        private static bool PhysicalMousePresent()
        {
            // The legacy Input.mousePresent flag is not authoritative for
            // Input System devices on Android. A real added Input System mouse
            // may exist even when legacy mousePresent reports false. Conversely,
            // the virtual LEFT-touch mouse must never trigger pointer capture.
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
            if (!nativeCaptured && Time.unscaledTime >= nextRequestTime)
            {
                nextRequestTime = Time.unscaledTime + 1.5f;
                RequestCapture();
            }
            if (requested && Time.unscaledTime >= nextProbeTime)
            {
                nextProbeTime = Time.unscaledTime + 0.15f;
                ProbeCapturedPointer();
            }
            int mismatch = Volatile.Read(ref mismatchedViewEpoch);
            if (mismatch != 0 && mismatch != loggedMismatchedViewEpoch)
            {
                loggedMismatchedViewEpoch = mismatch;
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("input",
                    "physical_mouse_capture_view_changed",
                    "epoch=" + mismatch + "; legacyFallbackMayApply=true");
            }
            int losses = Volatile.Read(ref captureLossCount);
            if (losses != loggedLossCount)
            {
                loggedLossCount = losses;
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("input",
                    "physical_mouse_capture_lost",
                    "lostTransitions=" + losses + "; legacyFallback=true");
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
                activity.Call("runOnUiThread", new AndroidJavaRunnable(() => work()));
        }

        // Android can revoke pointer capture without Unity focus callbacks.
        // Only an actual focused View.hasPointerCapture result may keep the
        // legacy mouse-axis override active. Old queued probes are ignored.
        private void ObserveNativeCapture(int token, bool captured)
        {
            lock (captureGate)
            {
                if (!requested || epoch != token) return;
                bool lost = nativeCaptured && !captured;
                nativeCaptured = captured;
                if (!captured)
                {
                    nativeHasMotion = false;
                    deltas.Reset();
                }
                if (lost) Interlocked.Increment(ref captureLossCount);
            }
        }

        private static int ViewIdentity(AndroidJavaObject view)
        {
            if (view == null) return 0;
            using (var system = new AndroidJavaClass("java.lang.System"))
                return system.CallStatic<int>("identityHashCode", view);
        }

        private void ProbeCapturedPointer()
        {
            int token = Volatile.Read(ref epoch);
            try
            {
                OnAndroidUi(() =>
                {
                    if (!requested || token != Volatile.Read(ref epoch)) return;
                    try
                    {
                        using (var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
                        using (var activity = player.GetStatic<AndroidJavaObject>("currentActivity"))
                        using (var view = activity.Call<AndroidJavaObject>("getCurrentFocus"))
                        {
                            int probedIdentity = ViewIdentity(view);
                            int requestedIdentity = Volatile.Read(ref captureViewIdentity);
                            if (requestedIdentity != 0 && probedIdentity != requestedIdentity)
                                Volatile.Write(ref mismatchedViewEpoch, token);
                            bool active = view != null && view.Call<bool>("hasWindowFocus") &&
                                view.Call<bool>("isFocused") && view.Call<bool>("hasPointerCapture");
                            ObserveNativeCapture(token, active);
                        }
                    }
                    catch (AndroidJavaException) { ObserveNativeCapture(token, false); }
                });
            }
            catch (AndroidJavaException) { ObserveNativeCapture(token, false); }
        }

        private void RequestCapture()
        {
            if (!requested)
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("input",
                    "physical_mouse_capture_requested",
                    "androidApi26=true; nativeAccepted=unknown; requiresDeviceConfirmation=true");
            int currentEpoch;
            lock (captureGate) { requested = true; currentEpoch = ++epoch; }
            // Do not reuse one listener across release/reacquire. Its token is
            // captured at install time, not read from a later active request.
            var requestListener = new CapturedListener(this, currentEpoch);
            listener = requestListener;
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
                                !view.Call<bool>("isFocused"))
                            {
                                ObserveNativeCapture(currentEpoch, false);
                                return;
                            }
                            Volatile.Write(ref captureViewIdentity, ViewIdentity(view));
                            view.Call("setOnCapturedPointerListener", requestListener);
                            if (view.Call<bool>("hasPointerCapture"))
                                ObserveNativeCapture(currentEpoch, true);
                            else
                                view.Call("requestPointerCapture");
                        }
                    }
                    catch (AndroidJavaException) { ObserveNativeCapture(currentEpoch, false); }
                });
            }
            catch (AndroidJavaException) { ObserveNativeCapture(currentEpoch, false); }
        }

        private void ReleaseCapture()
        {
            if (requested || nativeHasMotion)
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("input",
                    "physical_mouse_capture_released",
                    "focus=" + focused + "; paused=" + paused +
                    "; requested=" + requested + "; relativeEvents=" + deltas.ReceivedCount);
            lock (captureGate)
            {
                epoch++;
                requested = nativeHasMotion = nativeCaptured = false;
                deltas.Reset();
            }
            lastLoggedCount = 0;
            Volatile.Write(ref captureViewIdentity, 0);
            nextProbeTime = 0f;
            // UI-thread dispatch is asynchronous: a new request may supersede
            // this release before it runs. Never revoke that newer capture.
            int releaseEpoch = Volatile.Read(ref epoch);
            try
            {
                OnAndroidUi(() =>
                {
                    if (releaseEpoch != Volatile.Read(ref epoch) || requested) return;
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
