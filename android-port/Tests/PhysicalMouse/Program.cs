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

        Console.WriteLine("T4_PHYSICAL_MOUSE_DELTA_CONTROLS passed=" + tests +
            " AndroidJavaBridgeCompiled=false DeviceVerified=false");
        return 0;
    }
}
