using System;

namespace RaftAndroid.Platform
{
    // Captured mouse and touchpad events have different coordinate contracts.
    // Android API26+ SOURCE_MOUSE_RELATIVE getX/Y are relative, whereas a
    // captured SOURCE_TOUCHPAD has absolute getX/Y and relative AXIS 27/28.
    public static class PhysicalMouseMotionSource
    {
        public const int Mouse = 8194; // InputDevice.SOURCE_MOUSE (event from touchpad too)
        public const int MouseRelative = 131076; // InputDevice.SOURCE_MOUSE_RELATIVE
        public const int Touchpad = 1048584; // InputDevice.SOURCE_TOUCHPAD
        public const int AxisRelativeX = 27; // MotionEvent.AXIS_RELATIVE_X
        public const int AxisRelativeY = 28; // MotionEvent.AXIS_RELATIVE_Y
        public const int ActionMove = 2;
        public const int MaxHistorySamples = 64;

        public enum Kind { Ignore, Mouse, Touchpad }

        public static Kind Classify(int source)
        {
            if (source < 0) return Kind.Ignore;
            if ((source & MouseRelative) == MouseRelative) return Kind.Mouse;
            if ((source & Touchpad) == Touchpad) return Kind.Touchpad;
            return Kind.Ignore;
        }

        // Android documents that a touchpad normally sends MotionEvent
        // SOURCE_MOUSE, while InputDevice.getSources() advertises both mouse
        // and touchpad. Event source alone cannot identify a touchpad.
        // This fallback is only for an actual SOURCE_MOUSE event with an
        // attached device advertising SOURCE_TOUCHPAD. Other event classes
        // (including a touchscreen from the same composite device) fail open.
        public static Kind Classify(int eventSource, int deviceSources)
        {
            Kind direct = Classify(eventSource);
            if (direct != Kind.Ignore) return direct;
            if (eventSource == Mouse && deviceSources >= 0 &&
                (deviceSources & Touchpad) == Touchpad)
                return Kind.Touchpad;
            return Kind.Ignore;
        }

        // AndroidJavaProxy callbacks may complete after the Unity thread
        // releases capture and begins another native capture request.
        // A previous listener cannot transfer movement to a newer camera frame.
        public static bool AcceptEpoch(int listenerEpoch, int activeEpoch, bool requested)
        {
            return requested && listenerEpoch == activeEpoch;
        }

        public static bool ValidHistory(int size)
        {
            return size >= 0 && size <= MaxHistorySamples;
        }

        // Fail open for invalid or zero movement instead of overriding Unity's
        // original Mouse X/Y with an unusable relative delta.
        public static bool ValidDelta(float x, float y)
        {
            return !float.IsNaN(x) && !float.IsNaN(y) &&
                   !float.IsInfinity(x) && !float.IsInfinity(y) &&
                   Math.Abs(x) <= 10000f && Math.Abs(y) <= 10000f &&
                   (x != 0f || y != 0f);
        }
    }

    // Captured physical mouse callback observations only: never synthesize a
    // legacy Unity Input result or claim that a game button was delivered.
    public sealed class PhysicalMouseActionEvidence
    {
        public const int Down=0, Up=1, Scroll=8, Press=11, Release=12;
        public const int VScroll=9, HScroll=10;
        private readonly object gate = new object();
        private int count, presses, releases, pressMask, releaseMask, heldMask;
        private int vertical, horizontal, ambiguousDownUp;
        public struct Snapshot
        {
            public readonly int Count, Presses, Releases, PressMask, ReleaseMask;
            public readonly int HeldMask, Vertical, Horizontal, AmbiguousDownUp;
            public Snapshot(int count,int presses,int releases,int pressMask,int releaseMask,
                int heldMask,int vertical,int horizontal,int ambiguousDownUp)
            {
                Count=count;Presses=presses;Releases=releases;PressMask=pressMask;
                ReleaseMask=releaseMask;HeldMask=heldMask;Vertical=vertical;
                Horizontal=horizontal;AmbiguousDownUp=ambiguousDownUp;
            }
        }
        public static bool IsAction(int a)
        {
            return a==Down || a==Up || a==Scroll || a==Press || a==Release;
        }
        public bool Record(int action,int source,int actionButton,int buttonState,float v,float h)
        {
            if (!PhysicalMouseButtonWheelFrame.SourceIsPhysical(source)) return false;
            if (!IsAction(action)) return false;
            if (action==Scroll && (float.IsNaN(v)||float.IsNaN(h)||
                float.IsInfinity(v)||float.IsInfinity(h)||
                Math.Abs(v)>1000f||Math.Abs(h)>1000f||(v==0f&&h==0f))) return false;
            lock(gate)
            {
                if (count==int.MaxValue) return false;
                count++;
                heldMask=buttonState&7;
                if (action==Press) { presses++; pressMask|=actionButton&7; }
                else if (action==Release) { releases++; releaseMask|=actionButton&7; }
                else if (action==Scroll)
                {
                    if (v!=0f) vertical++;
                    if (h!=0f) horizontal++;
                }
                else ambiguousDownUp++; // getActionButton is UNDEFINED on DOWN/UP.
                return true;
            }
        }
        public Snapshot Read()
        {
            lock(gate) return new Snapshot(count,presses,releases,pressMask,releaseMask,
                heldMask,vertical,horizontal,ambiguousDownUp);
        }
        public void Reset()
        {
            lock(gate)
            {
                count=presses=releases=pressMask=releaseMask=heldMask=0;
                vertical=horizontal=ambiguousDownUp=0;
            }
        }
    }

    // Fail-closed physical pointer-capture fallback for the original game's
    // Unity Legacy Input mouse button/wheel readers. This is frame-latched:
    // Android View callbacks run off Unity's main thread, and a quick click
    // may press+release entirely between two Unity frames. A single frame
    // exposes each observed edge at most once, regardless of how many original
    // scripts ask. Nothing is synthesized for touchscreen or unknown sources.
    public sealed class PhysicalMouseButtonWheelFrame
    {
        private readonly object gate = new object();
        private const float WheelScale = 0.1f; // one Android detent -> Unity scroll unit
        private const float MaxWheelFrame = 20f;
        private int pendingDown, pendingUp, held, frameDown, frameUp, frameHeld;
        private int frame = int.MinValue, totalAccepted;
        private float pendingV, pendingH, frameV, frameH;

        // Android can deliver DOWN + BUTTON_PRESS (or UP + BUTTON_RELEASE)
        // with one physical eventTime while Unity samples between callbacks.
        // A per-frame bit mask alone would replay a single click twice. Match
        // only an explicit/implicit primary edge from the exact same physical
        // device/source/time; missing IDs never suppress an event.
        private struct EdgeToken
        {
            public long EventTimeMs;
            public int Source, DeviceId;
            public bool Valid;
            public bool Matches(long timeMs, int source, int deviceId)
            {
                return Valid && timeMs > 0 && deviceId >= 0 &&
                       EventTimeMs == timeMs && Source == source && DeviceId == deviceId;
            }
            public static EdgeToken Make(long timeMs, int source, int deviceId)
            {
                return new EdgeToken { EventTimeMs = timeMs, Source = source,
                    DeviceId = deviceId, Valid = timeMs > 0 && deviceId >= 0 };
            }
        }
        private EdgeToken implicitDown, explicitDown, implicitUp, explicitUp;

        public struct Snapshot
        {
            public readonly int DownMask, UpMask, HeldMask;
            public readonly float Vertical, Horizontal;
            public Snapshot(int down, int up, int held, float v, float h)
            {
                DownMask = down; UpMask = up; HeldMask = held;
                Vertical = v; Horizontal = h;
            }
            public bool Down(int button) { return InMask(DownMask, button); }
            public bool Up(int button) { return InMask(UpMask, button); }
            public bool Held(int button) { return InMask(HeldMask, button); }
            private static bool InMask(int mask, int button)
            {
                return button >= 0 && button <= 2 && (mask & (1 << button)) != 0;
            }
        }

        public static bool SourceIsPhysical(int source)
        {
            if (source < 0) return false;
            return (source & PhysicalMouseMotionSource.MouseRelative)
                     == PhysicalMouseMotionSource.MouseRelative ||
                   (source & PhysicalMouseMotionSource.Touchpad)
                     == PhysicalMouseMotionSource.Touchpad ||
                   (source & PhysicalMouseMotionSource.Mouse)
                     == PhysicalMouseMotionSource.Mouse;
        }

        private static float Bounded(float n)
        {
            return n > MaxWheelFrame ? MaxWheelFrame :
                   n < -MaxWheelFrame ? -MaxWheelFrame : n;
        }

        // actionButton is defined only for ACTION_BUTTON_PRESS/RELEASE. DOWN
        // has no valid actionButton but on Android mice does denote primary
        // button down when buttonState has BUTTON_PRIMARY. UP uses the prior
        // held primary state; no phantom release without observed press.
        // PRESS and DOWN for one gesture are coalesced by bitwise edge masks
        // and by Android eventTime + physical device across Unity frame edges.
        // Optional arguments keep older internal ABI callers source-compatible,
        // but no timestamp/device ID means no cross-frame deduplication.
        public bool Record(int action, int source, int actionButton,
            int buttonState, float vertical, float horizontal,
            long eventTimeMs = -1, int deviceId = -1)
        {
            if (!SourceIsPhysical(source)) return false;
            if (action != PhysicalMouseActionEvidence.Press &&
                action != PhysicalMouseActionEvidence.Release &&
                action != PhysicalMouseActionEvidence.Down &&
                action != PhysicalMouseActionEvidence.Up &&
                action != PhysicalMouseActionEvidence.Scroll) return false;
            if (action == PhysicalMouseActionEvidence.Scroll &&
                (float.IsNaN(vertical) || float.IsInfinity(vertical) ||
                 float.IsNaN(horizontal) || float.IsInfinity(horizontal) ||
                 Math.Abs(vertical) > 1000f || Math.Abs(horizontal) > 1000f ||
                 (vertical == 0f && horizontal == 0f))) return false;
            lock (gate)
            {
                int state = buttonState & 7;
                if (action == PhysicalMouseActionEvidence.Press)
                {
                    int changed = actionButton & 7;
                    if (changed != 1 && changed != 2 && changed != 4) return false;
                    if (changed != 1 || !implicitDown.Matches(eventTimeMs, source, deviceId))
                        pendingDown |= changed;
                    if (changed == 1)
                        explicitDown = EdgeToken.Make(eventTimeMs, source, deviceId);
                    held = state | changed;
                }
                else if (action == PhysicalMouseActionEvidence.Release)
                {
                    int changed = actionButton & 7;
                    if (changed != 1 && changed != 2 && changed != 4) return false;
                    // A release without an observed press is still an actual
                    // Android BUTTON_RELEASE callback, but not an invented DOWN.
                    if (changed != 1 || !implicitUp.Matches(eventTimeMs, source, deviceId))
                        pendingUp |= changed;
                    if (changed == 1)
                        explicitUp = EdgeToken.Make(eventTimeMs, source, deviceId);
                    held = state & ~changed;
                }
                else if (action == PhysicalMouseActionEvidence.Down)
                {
                    if ((state & 1) != 0)
                    {
                        if (!explicitDown.Matches(eventTimeMs, source, deviceId))
                            pendingDown |= 1;
                        implicitDown = EdgeToken.Make(eventTimeMs, source, deviceId);
                    }
                    held = state;
                }
                else if (action == PhysicalMouseActionEvidence.Up)
                {
                    if ((held & 1) != 0)
                    {
                        if (!explicitUp.Matches(eventTimeMs, source, deviceId))
                            pendingUp |= 1;
                        implicitUp = EdgeToken.Make(eventTimeMs, source, deviceId);
                    }
                    held = state;
                }
                else
                {
                    pendingV = Bounded(pendingV + vertical * WheelScale);
                    pendingH = Bounded(pendingH + horizontal * WheelScale);
                }
                if (totalAccepted != int.MaxValue) totalAccepted++;
                return true;
            }
        }

        public Snapshot Sample(int unityFrame)
        {
            lock (gate)
            {
                if (frame != unityFrame)
                {
                    frame = unityFrame;
                    frameDown = pendingDown;
                    frameUp = pendingUp;
                    frameHeld = held;
                    frameV = pendingV;
                    frameH = pendingH;
                    pendingDown = pendingUp = 0;
                    pendingV = pendingH = 0f;
                }
                return new Snapshot(frameDown, frameUp, frameHeld, frameV, frameH);
            }
        }

        public int AcceptedCount
        {
            get { lock (gate) return totalAccepted; }
        }

        public void Reset()
        {
            lock (gate)
            {
                pendingDown = pendingUp = held = frameDown = frameUp = frameHeld = 0;
                pendingV = pendingH = frameV = frameH = 0f;
                frame = int.MinValue;
                implicitDown = explicitDown = implicitUp = explicitUp = default(EdgeToken);
                totalAccepted = 0;
            }
        }
    }

}
