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


        // Captured callback proof is intentionally separate from Unity input.
        var actions=new PhysicalMouseActionEvidence();
        Check(!actions.Record(11,4098,1,1,0,0),"Touchscreen is not a mouse click");
        Check(actions.Read().Count==0,"Rejected touchscreen left no evidence");
        Check(actions.Record(11,131076,1,1,0,0),"Mouse0 press callback");
        Check(actions.Record(12,131076,1,0,0,0),"Mouse0 release callback");
        Check(actions.Record(11,8194,2,2,0,0),"Mouse1 press callback");
        Check(actions.Record(12,8194,2,0,0,0),"Mouse1 release callback");
        Check(actions.Record(11,1048584,4,4,0,0),"Mouse2 press callback");
        var read=actions.Read();
        Check(read.PressMask==7 && read.ReleaseMask==3 &&
              read.Presses==3 && read.Releases==2,"Button masks from explicit edges only");
        Check(actions.Record(0,8194,1,1,0,0) && actions.Record(1,8194,1,0,0,0),
            "DOWN/UP are observed as ambiguous, not identified presses");
        read=actions.Read();
        Check(read.AmbiguousDownUp==2 && read.ReleaseMask==3,
            "Undefined DOWN/UP actionButton cannot invent named edges");
        Check(!actions.Record(2,131076,0,0,1,1),"Move axis values are not scroll");
        Check(!actions.Record(8,131076,0,0,0,0),"Zero scroll is not wheel evidence");
        Check(!actions.Record(8,131076,0,0,float.NaN,1),"NaN scroll rejected");
        Check(!actions.Record(8,131076,0,0,1001,1),"Huge scroll rejected");
        Check(actions.Record(8,131076,0,0,-1,0),"Vertical scroll callback");
        Check(actions.Record(8,131076,0,0,0,2),"Horizontal scroll callback");
        Check(actions.Record(8,8194,0,0,1,-1),"Dual-axis scroll callback");
        read=actions.Read();
        Check(read.Count==10 && read.Vertical==2 && read.Horizontal==2,
            "Count ten bounded actions, two of each scroll axis");
        Check(PhysicalMouseActionEvidence.VScroll==9 &&
              PhysicalMouseActionEvidence.HScroll==10 &&
              !PhysicalMouseActionEvidence.IsAction(2) &&
              PhysicalMouseActionEvidence.IsAction(8),"Android action/axis constants");
        actions.Reset();
        read=actions.Read();
        Check(read.Count==0 && read.PressMask==0 && read.Vertical==0,
            "Release resets captured action evidence");


        // Pointer capture fallback must not lose a click between Unity frames
        // or re-emit a down edge for each original script reading in one frame.
        var legacyMouse = new PhysicalMouseButtonWheelFrame();
        Check(!legacyMouse.Record(11,4098,1,1,0f,0f), "No touchscreen mouse injection");
        Check(!legacyMouse.Record(8,0,0,0,1f,0f), "Unknown-source wheel rejected");
        Check(legacyMouse.Record(11,131076,1,1,0f,0f), "Captured Mouse0 press");
        Check(legacyMouse.Record(12,131076,1,0,0f,0f), "Captured Mouse0 release");
        var frame1 = legacyMouse.Sample(100);
        Check(frame1.Down(0) && frame1.Up(0) && !frame1.Held(0),
            "Press+release between Unity frames must preserve both edges");
        Check(legacyMouse.Sample(100).Down(0) && legacyMouse.Sample(100).Up(0),
            "Multiple same-frame authored callers share latched buttons");
        Check(!legacyMouse.Sample(101).Down(0) && !legacyMouse.Sample(101).Up(0),
            "Edges consumed at next frame without repeating");
        Check(legacyMouse.Record(0,8194,0,1,0f,0f), "Physical primary DOWN");
        Check(legacyMouse.Record(11,8194,1,1,0f,0f), "Coincident explicit primary PRESS");
        Check(legacyMouse.Sample(102).Down(0) && legacyMouse.Sample(102).Held(0),
            "ACTION_DOWN and BUTTON_PRESS coalesce to one held primary edge");
        Check(!legacyMouse.Sample(102).Down(-1) && !legacyMouse.Sample(102).Held(3),
            "Invalid indices cannot read physical buttons");
        Check(legacyMouse.Record(1,8194,0,0,0f,0f), "Physical primary UP");
        Check(legacyMouse.Record(12,8194,1,0,0f,0f), "Coincident explicit primary RELEASE");
        Check(legacyMouse.Sample(103).Up(0) && !legacyMouse.Sample(103).Held(0),
            "ACTION_UP and BUTTON_RELEASE coalesce to one primary release edge");
        Check(legacyMouse.Record(11,131076,2,2,0f,0f), "Physical right PRESSED");
        Check(legacyMouse.Record(11,131076,4,6,0f,0f), "Physical middle PRESSED");
        var frame2 = legacyMouse.Sample(104);
        Check(frame2.Down(1) && frame2.Down(2) &&
              frame2.Held(1) && frame2.Held(2), "Right and middle independent");
        Check(legacyMouse.Record(12,131076,2,4,0f,0f) &&
              legacyMouse.Record(12,131076,4,0,0f,0f),
            "Independent right and middle release");
        Check(legacyMouse.Sample(105).Up(1) && legacyMouse.Sample(105).Up(2),
            "Both physical release edges visible in next frame");
        Check(!legacyMouse.Record(11,131076,3,3,0f,0f),
            "Unknown multi-button changed mask cannot invent two presses");
        Check(!legacyMouse.Record(8,131076,0,0,float.NaN,1f),
            "NaN captured VScroll rejected");
        Check(!legacyMouse.Record(8,131076,0,0,0f,0f),
            "Zero scroll rejected");
        Check(!legacyMouse.Record(2,131076,0,0,0.4f,0.1f),
            "MOVE axis values cannot masquerade as scroll");
        Check(legacyMouse.Record(8,131076,0,0,1f,-2f),
            "Physical vertical+horizontal wheel accepted");
        Check(legacyMouse.Record(8,1048584,0,0,-2f,3f),
            "Touchpad scroll accepted without touching camera");
        var wheelFrame = legacyMouse.Sample(106);
        Check(Math.Abs(wheelFrame.Vertical + 0.1f) < 1e-5f &&
              Math.Abs(wheelFrame.Horizontal - 0.1f) < 1e-5f,
            "Android ±wheel deltas scaled and accumulated per frame");
        Check(Math.Abs(legacyMouse.Sample(106).Vertical + 0.1f) < 1e-5f,
            "Repeated Mouse ScrollWheel readers cannot double consume deltas");
        Check(legacyMouse.Sample(107).Vertical == 0f &&
              legacyMouse.Sample(107).Horizontal == 0f,
            "No stale wheel event after frame boundary");
        Check(legacyMouse.Record(11,131076,1,1,0f,0f),
            "Pre-release accepted callback");
        Check(legacyMouse.Sample(108).Held(0), "Pre-release held state");
        legacyMouse.Reset();
        Check(!legacyMouse.Sample(108).Held(0) &&
              !legacyMouse.Sample(108).Down(0) &&
              !legacyMouse.Sample(109).Up(0),
            "Native capture release clears held and all same-frame stale edges");
        Check(legacyMouse.AcceptedCount == 0, "Reset clears diagnostic counter");
        Check(legacyMouse.Record(8,131076,0,0,999f,-999f),
            "Bounded wheel axis source accepts sub-1000 input");
        wheelFrame=legacyMouse.Sample(110);
        Check(Math.Abs(wheelFrame.Vertical-20f)<1e-5f &&
              Math.Abs(wheelFrame.Horizontal+20f)<1e-5f,
            "Per-frame wheel accumulation clamps excessive magnitude");
        Check(!legacyMouse.Record(8,131076,0,0,1001f,0f),
            "Outlier wheel cannot inject into legacy scroll");
        Check(legacyMouse.Record(11,131076,2,2,0f,0f),
            "Pending right press before thread batch");
        Check(legacyMouse.Sample(111).Down(1), "Right press survives concurrent frame gate");
        Check(legacyMouse.Sample(112).Held(1), "Held right persists until release");

        Console.WriteLine("T4_PHYSICAL_MOUSE_DELTA_CONTROLS passed=" + tests +
            " AndroidJavaBridgeCompiled=false DeviceVerified=false");
        return 0;
    }
}
