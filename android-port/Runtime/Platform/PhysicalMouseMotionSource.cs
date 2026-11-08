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
            if (source!=PhysicalMouseMotionSource.Mouse &&
                source!=PhysicalMouseMotionSource.MouseRelative &&
                source!=PhysicalMouseMotionSource.Touchpad) return false;
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
}
