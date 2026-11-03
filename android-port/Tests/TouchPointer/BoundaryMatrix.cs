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

        // An earlier pending tap must not fire AFTER a later held touch releases.
        {
            var events = new List<bool>();
            var buttons = new TouchPointerButtons(events.Add);
            buttons.Tap(); buttons.Tap();
            buttons.BeginUpdate(); // first pulse releases, second remains queued
            buttons.Hold(true); buttons.BeginUpdate(); buttons.Hold(false);
            int endOfHold = events.Count;
            for (int i = 0; i < 5; i++) buttons.BeginUpdate();
            Require(!buttons.Pressed, "ghost-tap-not-pressed");
            Require(events.Count == endOfHold, "ghost-tap-after-hold-release");
        }

        // A tap request made while the left button is already held must not
        // become a click after its release; a genuinely new tap still works.
        {
            var events = new List<bool>();
            var buttons = new TouchPointerButtons(events.Add);
            buttons.Hold(true);
            buttons.Tap();
            buttons.BeginUpdate();
            buttons.Hold(false);
            int atRelease = events.Count;
            for (int i = 0; i < 4; i++) buttons.BeginUpdate();
            Require(!buttons.Pressed && events.Count == atRelease, "no-tap-replay-during-hold");
            buttons.Tap();
            Require(buttons.Pressed && events.Count == atRelease + 1, "new-tap-after-hold");
            buttons.BeginUpdate();
            Require(!buttons.Pressed && events.Count == atRelease + 2, "new-tap-release-after-hold");
        }

        // A pause/focus callback can synchronously cancel a touch while the
        // 500ms Down notification is being delivered. Neither completion path
        // may then emit a Tap or Move AFTER that cancellation/Up.
        {
            var events = new List<TouchPointerCommand>();
            TouchPointerGesture gesture = null;
            gesture = new TouchPointerGesture((cmd, x, y) =>
            {
                events.Add(cmd);
                if (cmd == TouchPointerCommand.Down) gesture.Cancel();
            });
            gesture.Begin(31, 1f, 2f, 10d);
            gesture.End(31, 8f, 9f, 10.5d, false);
            Require(events.Count == 3 &&
                events[0] == TouchPointerCommand.Move &&
                events[1] == TouchPointerCommand.Down &&
                events[2] == TouchPointerCommand.Up, "reentrant-cancel-end-no-ghost-tap");
            Require(!gesture.Active && !gesture.Held, "reentrant-cancel-end-clears-state");
        }

        {
            var events = new List<TouchPointerCommand>();
            TouchPointerGesture gesture = null;
            gesture = new TouchPointerGesture((cmd, x, y) =>
            {
                events.Add(cmd);
                if (cmd == TouchPointerCommand.Down) gesture.Cancel();
            });
            gesture.Begin(32, 1f, 2f, 20d);
            gesture.Move(32, 8f, 9f, 20.51d);
            Require(events.Count == 3 &&
                events[0] == TouchPointerCommand.Move &&
                events[1] == TouchPointerCommand.Down &&
                events[2] == TouchPointerCommand.Up, "reentrant-cancel-move-no-trailing-motion");
            Require(!gesture.Active && !gesture.Held, "reentrant-cancel-move-clears-state");
        }

        // Even when a new finger receives the SAME numeric touchId after a
        // synchronous focus reset, the old callback must never end the NEW
        // gesture. Ownership alone cannot distinguish these two lifetimes.
        {
            var events = new List<TouchPointerCommand>();
            TouchPointerGesture gesture = null;
            bool restarted = false;
            gesture = new TouchPointerGesture((cmd, x, y) =>
            {
                events.Add(cmd);
                if (cmd == TouchPointerCommand.Down && !restarted)
                {
                    restarted = true;
                    gesture.Cancel();
                    gesture.Begin(41, 90f, 91f, 30.5d);
                }
            });
            gesture.Begin(41, 1f, 2f, 30d);
            gesture.End(41, 3f, 4f, 30.5d, false);
            Require(gesture.Active && !gesture.Held, "same-touch-id-restart-survives-old-end");
            Require(events.Count == 4 &&
                events[0] == TouchPointerCommand.Move &&
                events[1] == TouchPointerCommand.Down &&
                events[2] == TouchPointerCommand.Up &&
                events[3] == TouchPointerCommand.Move, "same-touch-id-restart-no-old-tap");
            gesture.End(41, 92f, 93f, 30.6d, false);
            Require(events.Count == 5 &&
                events[4] == TouchPointerCommand.Tap &&
                !gesture.Active, "same-touch-id-restart-new-tap-valid");
        }

        {
            var events = new List<TouchPointerCommand>();
            TouchPointerGesture gesture = null;
            bool restarted = false;
            gesture = new TouchPointerGesture((cmd, x, y) =>
            {
                events.Add(cmd);
                if (cmd == TouchPointerCommand.Down && !restarted)
                {
                    restarted = true;
                    gesture.Cancel();
                    gesture.Begin(42, 90f, 91f, 40.51d);
                }
            });
            gesture.Begin(42, 1f, 2f, 40d);
            gesture.Move(42, 3f, 4f, 40.51d);
            Require(gesture.Active && !gesture.Held, "same-touch-id-restart-survives-old-move");
            Require(events.Count == 4 &&
                events[0] == TouchPointerCommand.Move &&
                events[1] == TouchPointerCommand.Down &&
                events[2] == TouchPointerCommand.Up &&
                events[3] == TouchPointerCommand.Move, "same-touch-id-restart-no-old-motion");
            gesture.End(42, 92f, 93f, 40.6d, false);
            Require(events.Count == 5 &&
                events[4] == TouchPointerCommand.Tap &&
                !gesture.Active, "same-touch-id-restart-move-new-tap-valid");
        }

        // Repeated Stationary touch packets must advance the gesture clock,
        // including the exact 500ms hold, without manufacturing 90 identical
        // synthetic mouse-position state events. Real position changes survive.
        {
            var events = new List<(TouchPointerCommand command, float x, float y)>();
            var gesture = new TouchPointerGesture((cmd, px, py) => events.Add((cmd, px, py)));
            gesture.Begin(71, 10f, 20f, 100d);
            for (int i = 1; i <= 90; i++)
                gesture.Move(71, 10f, 20f, 100d + i * 0.01d);
            Require(gesture.Held, "stationary-coalescing-preserves-500ms-hold");
            Require(events.Count == 2 &&
                events[0].command == TouchPointerCommand.Move &&
                events[1].command == TouchPointerCommand.Down,
                "stationary-coalescing-no-redundant-move");
            gesture.Move(71, 11f, 22f, 100.91d);
            Require(events.Count == 3 &&
                events[2].command == TouchPointerCommand.Move &&
                events[2].x == 11f && events[2].y == 22f,
                "stationary-coalescing-real-motion-preserved");
            gesture.End(71, 12f, 23f, 100.95d, false);
            Require(events.Count == 4 &&
                events[3].command == TouchPointerCommand.Up &&
                events[3].x == 12f && events[3].y == 23f &&
                !gesture.Active, "stationary-coalescing-release-preserved");

            // Even without moving the pointer, stale earlier timestamps
            // should still be rejected after stationary updates.
            gesture.Begin(72, 50f, 60f, 110d);
            gesture.Move(72, 50f, 60f, 110.25d);
            int beforeStale = events.Count;
            gesture.Move(72, 99f, 99f, 110.1d);
            Require(events.Count == beforeStale, "stationary-coalescing-clock-updated");
            gesture.Cancel();
            Require(!gesture.Active, "stationary-coalescing-cancel");
        }

        return checks;
    }
}
