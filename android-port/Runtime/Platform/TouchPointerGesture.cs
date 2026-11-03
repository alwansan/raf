using System;

namespace RaftAndroid.Platform
{
    public enum TouchPointerCommand { Move, Tap, Down, Up }

    // Engine-independent ownership/timing policy. The adapter must deliver Tap
    // as a one-update left-button pulse; this policy never emits a right button.
    public sealed class TouchPointerGesture
    {
        public const double HoldSeconds = 0.5;
        private int owner;
        private bool active, held;
        private double began, lastTime;
        private float x, y;
        private readonly Action<TouchPointerCommand, float, float> emit;

        public TouchPointerGesture(Action<TouchPointerCommand, float, float> emit)
        { this.emit = emit ?? throw new ArgumentNullException(nameof(emit)); }

        public bool Active { get { return active; } }
        public bool Held { get { return held; } }

        public void Begin(int id, float px, float py, double time)
        {
            if (active || !Valid(px, py, time)) return;
            owner = id; active = true; held = false;
            began = lastTime = time; x = px; y = py;
            emit(TouchPointerCommand.Move, x, y);
        }

        public void Move(int id, float px, float py, double time)
        {
            if (!active || owner != id || !Valid(px, py, time) || time < lastTime) return;
            x = px; y = py; lastTime = time;
            Tick(time);
            // Down can synchronously trigger Cancel (pause/focus loss).
            // Never deliver motion for a gesture that was just released or
            // replaced by a different owner during that callback.
            if (!active || owner != id) return;
            emit(TouchPointerCommand.Move, x, y);
        }

        public void Tick(double time)
        {
            if (!active || held || double.IsNaN(time) || double.IsInfinity(time) || time < lastTime) return;
            if (time - began >= HoldSeconds)
            {
                held = true;
                emit(TouchPointerCommand.Down, x, y);
            }
        }

        public void End(int id, float px, float py, double time, bool cancelled)
        {
            if (!active || owner != id) return;
            if (!Valid(px, py, time) || time < lastTime) { Cancel(); return; }
            x = px; y = py;
            if (!cancelled) Tick(time);
            // Tick may deliver Down, whose listener can cancel/restart touch.
            // Otherwise End could synthesize a Tap after Cancel already sent Up.
            if (!active || owner != id) return;
            bool wasHeld = held;
            active = held = false;
            if (wasHeld) emit(TouchPointerCommand.Up, x, y);
            else if (!cancelled) emit(TouchPointerCommand.Tap, x, y);
        }

        public void Cancel()
        {
            bool release = held;
            active = held = false;
            if (release) emit(TouchPointerCommand.Up, x, y);
        }

        private static bool Valid(float x, float y, double time)
        {
            return !float.IsNaN(x) && !float.IsInfinity(x) &&
                !float.IsNaN(y) && !float.IsInfinity(y) &&
                !double.IsNaN(time) && !double.IsInfinity(time);
        }
    }
}
