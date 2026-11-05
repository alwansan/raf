using System;

namespace RaftAndroid.Platform
{
    // Captured mouse and touchpad events have different coordinate contracts.
    // Android API26+ SOURCE_MOUSE_RELATIVE getX/Y are relative, whereas a
    // captured SOURCE_TOUCHPAD has absolute getX/Y and relative AXIS 27/28.
    public static class PhysicalMouseMotionSource
    {
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
}
