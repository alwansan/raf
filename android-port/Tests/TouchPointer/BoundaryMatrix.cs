using System;
using System.Collections.Generic;
using RaftAndroid.Platform;

// Deterministic CPU-only contract matrix. Exercises the ACTUAL authored
// gesture/queue classes, not a reimplementation of their logic.
// Does not claim Unity InputSystem, UGUI or device-input validation.
internal static class BoundaryMatrix
{
    private static int checks;
    private static void Require(bool value, string caseName)
    {
        checks++;
        if (!value) throw new InvalidOperationException("Touch boundary matrix: " + caseName);
    }

    internal static int Run()
    {
        // Exact hold boundary and clock-offset invariance: 499ms is a
        // short tap, 500ms+ is Down then Up, with release position retained.
        foreach (double origin in new[] { 0d, 17d, 1000d, 1000000d })
        {
            foreach (double elapsed in new[] { 0.499d, 0.5d, 0.501d })
            {
                var events = new List<(TouchPointerCommand command, float x, float y)>();
                var gesture = new TouchPointerGesture((c, x, y) => events.Add((c, x, y)));
                gesture.Begin(17, 10f, 20f, origin);
                gesture.Tick(origin + elapsed);
                bool expectedHeld = elapsed >= 0.5d;
                Require(gesture.Held == expectedHeld, "threshold");
                gesture.End(17, 30f, 40f, origin + elapsed, false);
                Require(!gesture.Active && !gesture.Held, "released");
                Require(events.Count == (expectedHeld ? 3 : 2), "transition-count");
                Require(events[0].command == TouchPointerCommand.Move, "initial-move");
                Require(events[events.Count - 1].command == (expectedHeld ? TouchPointerCommand.Up : TouchPointerCommand.Tap),
                    "release-command");
                Require(events[events.Count - 1].x == 30f && events[events.Count - 1].y == 40f, "release-coordinates");
                if (expectedHeld)
                {
                    Require(events[1].command == TouchPointerCommand.Down, "single-left-down");
                    Require(events[1].x == 10f && events[1].y == 20f, "hold-start-coordinates");
                }
            }

            // Cancellation never creates a fresh tap, whether or not the
            // hold has crossed 500ms; an existing hold releases exactly once.
            foreach (double elapsed in new[] { 0.499d, 0.5d, 0.75d })
            {
                var events = new List<TouchPointerCommand>();
                var gesture = new TouchPointerGesture((command, x, y) => events.Add(command));
                gesture.Begin(17, 2f, 3f, origin);
                gesture.Tick(origin + elapsed);
                gesture.End(17, 4f, 5f, origin + elapsed, true);
                gesture.Cancel();
                Require(!gesture.Active && !gesture.Held, "cancel-clears-state");
                Require(!events.Contains(TouchPointerCommand.Tap), "cancel-never-taps");
                Require(events.Count == (elapsed >= 0.5d ? 3 : 1), "cancel-release-count");
                if (elapsed >= 0.5d)
                {
                    Require(events[1] == TouchPointerCommand.Down, "cancel-held-down");
                    Require(events[2] == TouchPointerCommand.Up, "cancel-held-up");
                }
            }
        }

        // A competing finger must not take the gameplay gesture, move
        // its cursor or release it. Subsequent cancel must still release.
        {
            var events = new List<(TouchPointerCommand command, float x, float y)>();
            var gesture = new TouchPointerGesture((c, x, y) => events.Add((c, x, y)));
            gesture.Begin(1, 12f, 13f, 50d);
            gesture.Tick(50.5d);
            int before = events.Count;
            gesture.Begin(2, 99f, 99f, 50.6d);
            gesture.Move(2, 99f, 99f, 50.7d);
            gesture.End(2, 99f, 99f, 50.8d, false);
            Require(gesture.Active && gesture.Held && events.Count == before, "no-second-finger-hijack");
            gesture.Cancel();
            Require(events.Count == before + 1 && events[events.Count - 1].command == TouchPointerCommand.Up,
                "cancel-after-secondary");
            Require(events[events.Count - 1].x == 12f && events[events.Count - 1].y == 13f,
                "cancel-keeps-owner-coordinates");
        }

        // Stress queued taps with deterministic bounded input. One update
        // of release must separate presses; cancel discards pending pulses.
        {
            const int taps = 128;
            var transitions = new List<bool>();
            var buttons = new TouchPointerButtons(transitions.Add);
            for (int i = 0; i < taps; i++) buttons.Tap();
            Require(buttons.Pressed, "first-queued-press");
            for (int i = 0; i < taps * 2 - 1; i++) buttons.BeginUpdate();
            Require(!buttons.Pressed && transitions.Count == taps * 2, "all-queued-taps-drained");
            for (int i = 0; i < transitions.Count; i++)
                Require(transitions[i] == (i % 2 == 0), "alternating-tap-release");
            buttons.Hold(true);
            for (int i = 0; i < 4; i++) buttons.BeginUpdate();
            Require(buttons.Pressed, "hold-survives-input-updates");
            buttons.Tap();
            buttons.Cancel();
            for (int i = 0; i < 4; i++) buttons.BeginUpdate();
            Require(!buttons.Pressed && transitions[transitions.Count - 1] == false, "cancel-clears-hold-and-queue");
        }

        return checks;
    }
}
