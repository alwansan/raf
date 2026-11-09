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
        private readonly PhysicalMouseActionEvidence actionEvidence = new PhysicalMouseActionEvidence();
        private readonly PhysicalMouseButtonWheelFrame buttonWheel = new PhysicalMouseButtonWheelFrame();
        private readonly PhysicalMouseLegacyReaderEvidence readerEvidence = new PhysicalMouseLegacyReaderEvidence();
        private long lastReaderLogCalls, lastReaderLogEdges, lastReaderLogScroll;
        private int lastActionReport;
        private CapturedListener listener;
        private bool focused = true, paused, supported;
        private volatile bool nativeHasMotion, requested, nativeCaptured;
        private readonly object captureGate = new object();
        private int epoch, lastMotionEpoch, lastLoggedCount, captureLossCount, loggedLossCount, captureRequestAttempts;
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
                            Volatile.Read(ref owner.epoch), owner.requested))
                        return false;
                    int action = motionEvent.Call<int>("getActionMasked");
                    if (action != PhysicalMouseMotionSource.ActionMove)
                    {
                        // Never consume button or scroll: the original View/Unity
                        // route remains the only input route. Record callback
                        // delivery, NOT successful input inside Raft.
                        if (PhysicalMouseActionEvidence.IsAction(action))
                        {
                            int eventSource = motionEvent.Call<int>("getSource");
                            // Android getActionButton is defined only for 11/12.
                            int changed = action == PhysicalMouseActionEvidence.Press ||
                                          action == PhysicalMouseActionEvidence.Release
                                ? motionEvent.Call<int>("getActionButton") : 0;
                            int held = motionEvent.Call<int>("getButtonState");
                            float v = action == PhysicalMouseActionEvidence.Scroll
                                ? motionEvent.Call<float>("getAxisValue", PhysicalMouseActionEvidence.VScroll) : 0f;
                            float h = action == PhysicalMouseActionEvidence.Scroll
                                ? motionEvent.Call<float>("getAxisValue", PhysicalMouseActionEvidence.HScroll) : 0f;
                            // Android eventTime is uptime milliseconds; deviceId
                            // prevents two physical mice from aliasing on same ms.
                            long eventTimeMs = motionEvent.Call<long>("getEventTime");
                            int deviceId = motionEvent.Call<int>("getDeviceId");
                            owner.RecordCapturedAction(listenerEpoch,action,eventSource,changed,held,v,h,eventTimeMs,deviceId);
                        }
                        return false;
                    }
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
                Volatile.Write(ref lastMotionEpoch, listenerEpoch);
                nativeCaptured = nativeHasMotion = true;
                return true;
            }
        }


        private void RecordCapturedAction(int listenerEpoch,int action,int source,
            int changedButton,int heldButton,float vertical,float horizontal,long eventTimeMs,int deviceId)
        {
            // Android UI event thread: no Unity APIs and no per-event logging.
            lock(captureGate)
            {
                if (PhysicalMouseMotionSource.AcceptEpoch(listenerEpoch,epoch,requested))
                {
                    actionEvidence.Record(action,source,changedButton,heldButton,vertical,horizontal);
                    // Stage only authentic captured mouse actions. The Unity
                    // main thread exposes one immutable per-frame snapshot;
                    // no InputSystem events or touch callbacks are injected.
                    // A generation-bound OnCapturedPointerListener callback
                    // itself is native capture evidence even without any MOVE.
                    // Do not require camera motion before a button-only click
                    // or wheel-only gesture may supplement missing Legacy Input.
                    if (buttonWheel.Record(action,source,changedButton,heldButton,vertical,horizontal,eventTimeMs,deviceId))
                        nativeCaptured = true;
                }
            }
        }

        private void LogCapturedActions(string operation,PhysicalMouseActionEvidence.Snapshot s)
        {
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("input",operation,
                "epoch="+Volatile.Read(ref epoch)+
                "; capturedCallbackEvents="+s.Count+
                "; pressCallbacks="+s.Presses+"; releaseCallbacks="+s.Releases+
                "; pressMask="+s.PressMask+"; releaseMask="+s.ReleaseMask+
                "; heldMask="+s.HeldMask+"; verticalScrollCallbacks="+s.Vertical+
                "; horizontalScrollCallbacks="+s.Horizontal+
                "; undefinedActionDownUp="+s.AmbiguousDownUp+
                "; legacyFrameInputBuffered="+buttonWheel.AcceptedCount+
                "; nonMoveConsumed=false; unityButtonsAndWheelVerified=false");
        }

        private void LogLegacyReaderEvidence(string operation,
            PhysicalMouseLegacyReaderEvidence.Snapshot counts)
        {
            // Purely observed Unity getter calls; no claim of in-game actions.
            RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("input", operation,
                "epoch=" + Volatile.Read(ref epoch) +
                "; captureRequested=" + requested + "; captureObserved=" + nativeCaptured +
                "; getterCalls=" + counts.Calls +
                "; positiveLegacy=" + counts.Legacy +
                "; positiveFallback=" + counts.Fallback +
                "; positiveEdges=" + counts.Edges +
                "; positiveScroll=" + counts.Scroll +
                "; " + readerEvidence.Report() +
                "; countersAreGetterCallsNotClicks=true; unityGameplayVerified=false");
        }

        public static CursorLockMode ApplyCursorLock(CursorLockMode mode)
        {
            // Preserve the original authored cursor-lock assignment exactly.
            Cursor.lockState = mode;
            int nextIntent = mode == CursorLockMode.Locked ? 1 : 0;
            int priorIntent = Interlocked.Exchange(ref originalLockIntent, nextIntent);
            if (priorIntent != nextIntent)
                LogLockIntent(nextIntent == 1 ? "authored_lock" : "authored_unlock");
            return mode;
        }

        private static void LogLockIntent(string transition)
        {
            // Only state transitions, never per-frame motion or keyboard text.
            // Logging must not change authored cursor/keyboard behavior.
            try
            {
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("input",
                    "physical_mouse_lock_intent", "transition=" + transition);
            }
            catch (Exception) { /* Diagnostics must remain nonblocking. */ }
        }

        public static float GetAxis(string axis) { return Axis(axis, false); }
        public static float GetAxisRaw(string axis) { return Axis(axis, true); }

        // Original Raft reads the Legacy Input mouse API directly. Preserve
        // it whenever the platform reports a value; only supplement a missing
        // value after the same current Android View has real pointer capture.
        // OR of boolean edge states cannot double-fire one Unity frame.
        private static bool TryCapturedFrame(out PhysicalMouseButtonWheelFrame.Snapshot result)
        {
            result = default(PhysicalMouseButtonWheelFrame.Snapshot);
            var current = instance;
            if (current == null) return false;
            lock (current.captureGate)
            {
                if (!current.requested || !current.nativeCaptured) return false;
                result = current.buttonWheel.Sample(Time.frameCount);
                return true;
            }
        }

        // Collect original patched Legacy Input reads only while capture
        // requested. Never write logs or call JNI in these hot-path readers.
        private static void RecordLegacyReader(int operation, int button,
            bool nativePositive, bool fallbackPositive)
        {
            var current = instance;
            if (current != null && current.requested)
                current.readerEvidence.Record(operation, button, nativePositive, fallbackPositive);
        }

        public static bool GetMouseButton(int index)
        {
            bool legacy = Input.GetMouseButton(index);
            if (legacy)
            {
                RecordLegacyReader(PhysicalMouseLegacyReaderEvidence.Held, index, true, false);
                return true;
            }
            PhysicalMouseButtonWheelFrame.Snapshot frame;
            bool fallback = TryCapturedFrame(out frame) && frame.Held(index);
            RecordLegacyReader(PhysicalMouseLegacyReaderEvidence.Held, index, false, fallback);
            return fallback;
        }

        public static bool GetMouseButtonDown(int index)
        {
            bool legacy = Input.GetMouseButtonDown(index);
            if (legacy)
            {
                RecordLegacyReader(PhysicalMouseLegacyReaderEvidence.Down, index, true, false);
                return true;
            }
            PhysicalMouseButtonWheelFrame.Snapshot frame;
            bool fallback = TryCapturedFrame(out frame) && frame.Down(index);
            RecordLegacyReader(PhysicalMouseLegacyReaderEvidence.Down, index, false, fallback);
            return fallback;
        }

        public static bool GetMouseButtonUp(int index)
        {
            bool legacy = Input.GetMouseButtonUp(index);
            if (legacy)
            {
                RecordLegacyReader(PhysicalMouseLegacyReaderEvidence.Up, index, true, false);
                return true;
            }
            PhysicalMouseButtonWheelFrame.Snapshot frame;
            bool fallback = TryCapturedFrame(out frame) && frame.Up(index);
            RecordLegacyReader(PhysicalMouseLegacyReaderEvidence.Up, index, false, fallback);
            return fallback;
        }

        public static Vector2 GetMouseScrollDelta()
        {
            Vector2 legacy = Input.mouseScrollDelta;
            if (legacy.x != 0f || legacy.y != 0f)
            {
                RecordLegacyReader(PhysicalMouseLegacyReaderEvidence.ScrollVector, -1, true, false);
                return legacy;
            }
            PhysicalMouseButtonWheelFrame.Snapshot frame;
            Vector2 value = TryCapturedFrame(out frame)
                ? new Vector2(frame.Horizontal, frame.Vertical) : legacy;
            RecordLegacyReader(PhysicalMouseLegacyReaderEvidence.ScrollVector, -1,
                false, value.x != 0f || value.y != 0f);
            return value;
        }

        private static float Axis(string axis, bool raw)
        {
            if (axis == "Mouse ScrollWheel")
            {
                float legacy = raw ? Input.GetAxisRaw(axis) : Input.GetAxis(axis);
                if (legacy != 0f)
                {
                    RecordLegacyReader(PhysicalMouseLegacyReaderEvidence.ScrollAxis, -1, true, false);
                    return legacy;
                }
                PhysicalMouseButtonWheelFrame.Snapshot capturedFrame;
                float value = TryCapturedFrame(out capturedFrame) ? capturedFrame.Vertical : legacy;
                RecordLegacyReader(PhysicalMouseLegacyReaderEvidence.ScrollAxis, -1, false, value != 0f);
                return value;
            }
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
            if (Input.GetKeyDown(KeyCode.Escape) &&
                Interlocked.Exchange(ref originalLockIntent, 0) != 0)
                LogLockIntent("escape_release");
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
            var readerCounts = readerEvidence.Read();
            // First reader, new positive edge/scroll, or once per 512 polls.
            // Held true across many frames cannot flood persistent logs.
            if (readerCounts.Calls > 0 &&
                (lastReaderLogCalls == 0 ||
                 readerCounts.Calls - lastReaderLogCalls >= 512 ||
                 readerCounts.Edges > lastReaderLogEdges ||
                 readerCounts.Scroll > lastReaderLogScroll))
            {
                lastReaderLogCalls = readerCounts.Calls;
                lastReaderLogEdges = readerCounts.Edges;
                lastReaderLogScroll = readerCounts.Scroll;
                LogLegacyReaderEvidence("physical_mouse_legacy_reader_evidence", readerCounts);
            }
            var actions=actionEvidence.Read();
            int last=Volatile.Read(ref lastActionReport);
            if(actions.Count>0 && (last==0 || actions.Count>=last+16))
            {
                Volatile.Write(ref lastActionReport,actions.Count);
                LogCapturedActions("physical_mouse_captured_action_callbacks",actions);
            }
            int received = deltas.ReceivedCount;
            // Emit one marker for a short real-mouse movement sequence; the
            // old 120-event-only gate hid all evidence in brief tests.
            // Thereafter retain the original 120-event logging interval.
            if (received > 0 && (lastLoggedCount == 0 || received >= lastLoggedCount + 120))
            {
                lastLoggedCount = received;
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("input",
                    "physical_mouse_relative", "events=" + received +
                    "; epoch=" + Volatile.Read(ref lastMotionEpoch) +
                    "; legacyAxes=true; deviceDirectionVerified=false");
            }
        }

        private static void OnAndroidUi(Action work)
        {
            using (var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
            using (var activity = player.GetStatic<AndroidJavaObject>("currentActivity"))
            {
                // During Android activity teardown there may be no UI thread
                // target. Fail softly via the existing request/probe/release
                // fallbacks instead of dereferencing a null JNI wrapper.
                if (activity == null)
                    throw new InvalidOperationException("Unity Activity unavailable");
                activity.Call("runOnUiThread", new AndroidJavaRunnable(() => work()));
            }
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
                    actionEvidence.Reset();
                    buttonWheel.Reset();
                    Volatile.Write(ref lastActionReport,0);
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
                        using (var view = activity == null ? null : activity.Call<AndroidJavaObject>("getCurrentFocus"))
                        {
                            int probedIdentity = ViewIdentity(view);
                            int requestedIdentity = Volatile.Read(ref captureViewIdentity);
                            if (requestedIdentity == 0 || probedIdentity != requestedIdentity)
                            {
                                // A different focused View cannot establish capture for
                                // the View that installed our generation-bound listener.
                                // Fail back to original Unity axes until reacquisition;
                                // do not report the other View's capture as our own.
                                Volatile.Write(ref mismatchedViewEpoch, token);
                                ObserveNativeCapture(token, false);
                                return;
                            }
                            bool active = view != null && view.Call<bool>("hasWindowFocus") &&
                                view.Call<bool>("isFocused") && view.Call<bool>("hasPointerCapture");
                            ObserveNativeCapture(token, active);
                        }
                    }
                    catch (AndroidJavaException) { ObserveNativeCapture(token, false); }
                });
            }
            catch (AndroidJavaException) { ObserveNativeCapture(token, false); }
            catch (InvalidOperationException) { ObserveNativeCapture(token, false); }
        }

        private void RequestCapture()
        {
            // Report first request as before. Retry telemetry is bounded to
            // powers of two so a device that never grants capture cannot flood logs.
            // Attempts count requests, not Android acceptance or mouse motion.
            int attempt = ++captureRequestAttempts;
            int currentEpoch;
            lock (captureGate)
            {
                requested = true;
                currentEpoch = ++epoch;
                // A new generation must not inherit the prior focused View.
                Volatile.Write(ref captureViewIdentity, 0);
            }
            // Correlate bounded request/retry events with the exact generation
            // used by the listener. These markers do not imply OS acceptance.
            if (attempt == 1)
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("input",
                    "physical_mouse_capture_requested",
                    "epoch=" + currentEpoch +
                    "; androidApi26=true; nativeAccepted=unknown; requiresDeviceConfirmation=true");
            else if ((attempt & (attempt - 1)) == 0)
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("input",
                    "physical_mouse_capture_retry",
                    "epoch=" + currentEpoch + "; attempt=" + attempt +
                    "; nativeAccepted=unknown; requiresDeviceConfirmation=true");
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
                        using (var view = activity == null ? null : activity.Call<AndroidJavaObject>("getCurrentFocus"))
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
            catch (InvalidOperationException) { ObserveNativeCapture(currentEpoch, false); }
        }

        private static void ReportReleaseOutcome(string result)
        {
            // UI-thread release is async: the original request marker is not
            // proof that a native View release method has actually returned.
            // Emit only fixed categories, no hashes, paths, event data or JNI.
            try
            {
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("input",
                    "physical_mouse_capture_release_outcome",
                    "result=" + result + "; native_release_confirmed=false");
            }
            catch (Exception) { /* Diagnostics must never alter pointer state. */ }
        }

        private void ReleaseCapture()
        {
            if (requested || nativeHasMotion)
                RaftAndroid.Diagnostics.AndroidRuntimeLog.Write("input",
                    "physical_mouse_capture_released",
                    "focus=" + focused + "; paused=" + paused +
                    "; requested=" + requested + "; relativeEvents=" + deltas.ReceivedCount);
            var finalActions=actionEvidence.Read();
            if(finalActions.Count>Volatile.Read(ref lastActionReport))
                LogCapturedActions("physical_mouse_captured_action_callbacks_final",finalActions);
            var finalReaderCounts = readerEvidence.Read();
            if (finalReaderCounts.Calls > lastReaderLogCalls)
                LogLegacyReaderEvidence("physical_mouse_legacy_reader_evidence_final", finalReaderCounts);
            int releaseViewIdentity;
            lock (captureGate)
            {
                // Capture the requested View identity before clearing it.
                // Never retain or invoke an AndroidJavaObject across threads.
                releaseViewIdentity = Volatile.Read(ref captureViewIdentity);
                epoch++;
                requested = nativeHasMotion = nativeCaptured = false;
                Volatile.Write(ref captureViewIdentity, 0);
                deltas.Reset();
                actionEvidence.Reset();
                buttonWheel.Reset();
                readerEvidence.Reset();
            }
            lastReaderLogCalls = lastReaderLogEdges = lastReaderLogScroll = 0;
            Volatile.Write(ref lastActionReport,0);
            lastLoggedCount = 0;
            captureRequestAttempts = 0;
            nextProbeTime = 0f;
            // Preserve the original release-epoch checkpoint and queued
            // callback guard. An unrelated View must still never be released.
            int releaseEpoch = Volatile.Read(ref epoch);
            // UI-thread dispatch is asynchronous: a new request may supersede
            // this release before it runs. Never revoke that newer capture.
            try
            {
                OnAndroidUi(() =>
                {
                    if (releaseEpoch != Volatile.Read(ref epoch) || requested)
                    {
                        ReportReleaseOutcome("superseded_generation");
                        return;
                    }
                    try
                    {
                        using (var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
                        using (var activity = player.GetStatic<AndroidJavaObject>("currentActivity"))
                        using (var view = activity == null ? null : activity.Call<AndroidJavaObject>("getCurrentFocus"))
                        {
                            // Same target rule as before. Distinguish skipped
                            // UI-thread calls from a successful *invocation*.
                            // OS capture state after this call is still unknown.
                            string result;
                            if (releaseViewIdentity == 0)
                                result = "unbound_request_view";
                            else if (view == null)
                                result = "focus_view_unavailable";
                            else if (ViewIdentity(view) != releaseViewIdentity)
                                result = "focused_view_changed";
                            else if (!view.Call<bool>("hasPointerCapture"))
                                result = "target_not_captured";
                            else
                            {
                                view.Call("releasePointerCapture");
                                result = "release_call_returned";
                            }
                            ReportReleaseOutcome(result);
                        }
                    }
                    catch (AndroidJavaException)
                    {
                        ReportReleaseOutcome("jni_exception");
                    }
                });
            }
            catch (AndroidJavaException)
            {
                ReportReleaseOutcome("ui_dispatch_exception");
            }
            catch (InvalidOperationException)
            {
                ReportReleaseOutcome("ui_dispatch_exception");
            }
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
#elif UNITY_5_3_OR_NEWER
using UnityEngine;

namespace RaftAndroid.Platform
{
    // Unity Editor compiles restored original gameplay scripts for Android
    // while UNITY_EDITOR is true. The real Android JNI/View bridge above must
    // not run there, but its static original-input call sites must resolve.
    // Other non-Android Unity players keep exact legacy input semantics.
    // Netstandard source-only builds without Unity symbols exclude both arms.
    public sealed class AndroidPhysicalMouseCapture : MonoBehaviour
    {
        public static CursorLockMode ApplyCursorLock(CursorLockMode mode)
        {
            Cursor.lockState = mode;
            return mode;
        }

        public static float GetAxis(string axis)
        {
            return Input.GetAxis(axis);
        }

        public static float GetAxisRaw(string axis)
        {
            return Input.GetAxisRaw(axis);
        }
        public static bool GetMouseButton(int button) { return Input.GetMouseButton(button); }
        public static bool GetMouseButtonDown(int button) { return Input.GetMouseButtonDown(button); }
        public static bool GetMouseButtonUp(int button) { return Input.GetMouseButtonUp(button); }
        public static Vector2 GetMouseScrollDelta() { return Input.mouseScrollDelta; }
    }
}
#endif
