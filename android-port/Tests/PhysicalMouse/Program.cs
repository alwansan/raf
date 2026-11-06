using System;
using System.Threading.Tasks;
using RaftAndroid.Platform;

static class Program
{
    static int tests;

    static void Check(bool value, string name)
    {
        if (!value) throw new InvalidOperationException(name);
        tests++;
    }

    static int Main()
    {
        var motion = new PhysicalMouseDeltaAccumulator();
        motion.Push(10f, 5f);
        Check(Math.Abs(motion.Sample(10, true) - 1f) < 1e-6f, "X axis");
        Check(Math.Abs(motion.Sample(10, false) + 0.5f) < 1e-6f, "Y inverted");
        Check(Math.Abs(motion.Sample(10, true) - 1f) < 1e-6f, "Repeated same-frame reads");
        motion.Push(3f, -2f);
        Check(Math.Abs(motion.Sample(10, true) - 1f) < 1e-6f, "No late-event double-read");
        Check(Math.Abs(motion.Sample(11, true) - 0.3f) < 1e-6f, "Next-frame pending X");
        Check(Math.Abs(motion.Sample(11, false) - 0.2f) < 1e-6f, "Next-frame pending Y");
        motion.Push(float.NaN, 1);
        motion.Push(10001f, 1);
        motion.Push(float.PositiveInfinity, 1);
        Check(motion.ReceivedCount == 2, "Reject invalid or extreme events");
        motion.Reset();
        Check(motion.ReceivedCount == 0, "Reset event count on release");
        Check(motion.Sample(11, true) == 0f && motion.Sample(11, false) == 0f,
            "Reset discards stale motion even on same frame");
        motion.Push(9000f, 9000f);
        Check(motion.ReceivedCount == 1 && motion.Sample(12, true) == 409.6f,
            "Unexpected large but bounded device delta");
        motion.Reset();
        Parallel.For(0, 50, _ => motion.Push(1, 1));
        Check(motion.ReceivedCount == 50, "UI-thread concurrent event safety");
        Check(Math.Abs(motion.Sample(13, true) - 5f) < 1e-6f, "Concurrent sum X");
        Check(Math.Abs(motion.Sample(13, false) + 5f) < 1e-6f, "Concurrent sum Y");

        // Android API26 captured sources must not treat absolute touch
        // or an uncaptured SOURCE_MOUSE coordinate as a relative delta.
        Check(PhysicalMouseMotionSource.Classify(131076) ==
            PhysicalMouseMotionSource.Kind.Mouse, "SOURCE_MOUSE_RELATIVE");
        Check(PhysicalMouseMotionSource.Classify(1048584) ==
            PhysicalMouseMotionSource.Kind.Touchpad, "SOURCE_TOUCHPAD");
        Check(PhysicalMouseMotionSource.Classify(8194) ==
            PhysicalMouseMotionSource.Kind.Ignore, "Uncaptured SOURCE_MOUSE");
        Check(PhysicalMouseMotionSource.Classify(4098) ==
            PhysicalMouseMotionSource.Kind.Ignore, "SOURCE_TOUCHSCREEN");
        Check(PhysicalMouseMotionSource.Classify(0) ==
            PhysicalMouseMotionSource.Kind.Ignore, "Unknown source");
        Check(PhysicalMouseMotionSource.Classify(-1) ==
            PhysicalMouseMotionSource.Kind.Ignore, "Invalid source bits");
        Check(PhysicalMouseMotionSource.AxisRelativeX == 27 &&
              PhysicalMouseMotionSource.AxisRelativeY == 28, "Android relative axis IDs");
        Check(PhysicalMouseMotionSource.ValidHistory(0), "Unbatched MOVE");
        Check(PhysicalMouseMotionSource.ValidHistory(64), "Bounded historical samples");
        Check(!PhysicalMouseMotionSource.ValidHistory(65), "Reject oversized MOVE history");
        Check(!PhysicalMouseMotionSource.ValidHistory(-1), "Reject invalid history size");
        Check(PhysicalMouseMotionSource.ValidDelta(4f, 0f), "Horizontal-only movement");
        Check(PhysicalMouseMotionSource.ValidDelta(0f, -3f), "Vertical-only movement");
        Check(!PhysicalMouseMotionSource.ValidDelta(0f, 0f), "Ignore zero delta packets");
        Check(!PhysicalMouseMotionSource.ValidDelta(float.NaN, 1f), "Reject NaN delta");
        Check(!PhysicalMouseMotionSource.ValidDelta(float.NegativeInfinity, 1f),
            "Reject infinite delta");
        Check(!PhysicalMouseMotionSource.ValidDelta(10001f, 1f),
            "Reject out-of-range delta");


        // The native View listener itself is tied to a specific capture request.
        // A previous ACTION_MOVE may finish after release and a newer request:
        // even if requested becomes true again, the stale packet must fail.
        Check(PhysicalMouseMotionSource.AcceptEpoch(17, 17, true),
            "Current captured listener accepted");
        Check(!PhysicalMouseMotionSource.AcceptEpoch(17, 18, true),
            "Old captured listener cannot enter newer request");
        Check(!PhysicalMouseMotionSource.AcceptEpoch(18, 18, false),
            "Release rejects same-generation callback");
        Check(!PhysicalMouseMotionSource.AcceptEpoch(18, 19, false),
            "Release plus new epoch rejects callback");
        Check(PhysicalMouseMotionSource.AcceptEpoch(19, 19, true),
            "New listener restores current mouse movement");
        Check(!PhysicalMouseMotionSource.AcceptEpoch(-1, 19, true),
            "Invalid generation never accepted for current capture");


        // Android InputDevice docs: the touchpad's MotionEvent source usually
        // says SOURCE_MOUSE. Its InputDevice.getSources() advertises TOUCHPAD.
        // Never promote a regular mouse or touchscreen into touchpad deltas.
        const int mouseSource = PhysicalMouseMotionSource.Mouse;
        const int trackpadSources = mouseSource | PhysicalMouseMotionSource.Touchpad;
        Check(PhysicalMouseMotionSource.Classify(mouseSource, trackpadSources) ==
            PhysicalMouseMotionSource.Kind.Touchpad,
            "Documented touchpad event MOUSE with touchpad device capability");
        Check(PhysicalMouseMotionSource.Classify(mouseSource,
            PhysicalMouseMotionSource.Touchpad) == PhysicalMouseMotionSource.Kind.Touchpad,
            "Touchpad capability alone sufficient for MOUSE event");
        Check(PhysicalMouseMotionSource.Classify(mouseSource, mouseSource) ==
            PhysicalMouseMotionSource.Kind.Ignore, "Ordinary mouse remains unclassified");
        Check(PhysicalMouseMotionSource.Classify(mouseSource, 0) ==
            PhysicalMouseMotionSource.Kind.Ignore, "Missing physical device ignored");
        Check(PhysicalMouseMotionSource.Classify(mouseSource, -1) ==
            PhysicalMouseMotionSource.Kind.Ignore, "Invalid device sources ignored");
        Check(PhysicalMouseMotionSource.Classify(4098, trackpadSources) ==
            PhysicalMouseMotionSource.Kind.Ignore,
            "Touchscreen event ignored even on composite touchpad device");
        Check(PhysicalMouseMotionSource.Classify(65540, trackpadSources) ==
            PhysicalMouseMotionSource.Kind.Ignore, "Trackball event cannot spoof touchpad");
        Check(PhysicalMouseMotionSource.Classify(131076, 0) ==
            PhysicalMouseMotionSource.Kind.Mouse,
            "Actual relative mouse remains accepted without extra JNI lookup");
        Check(PhysicalMouseMotionSource.Classify(1048584, 0) ==
            PhysicalMouseMotionSource.Kind.Touchpad,
            "Explicit touchpad event remains accepted");
        Check(PhysicalMouseMotionSource.Classify(-1, trackpadSources) ==
            PhysicalMouseMotionSource.Kind.Ignore, "Negative event source rejected");
        Check(PhysicalMouseMotionSource.Classify(mouseSource, mouseSource | 16386) ==
            PhysicalMouseMotionSource.Kind.Ignore, "Stylus-capable mouse not a touchpad");
        Check(PhysicalMouseMotionSource.Classify(4098, trackpadSources | 4098) ==
            PhysicalMouseMotionSource.Kind.Ignore, "Composite touchscreen stays separate");

        Console.WriteLine("T4_PHYSICAL_MOUSE_DELTA_CONTROLS passed=" + tests +
            " AndroidJavaBridgeCompiled=false DeviceVerified=false");
        return 0;
    }
}
