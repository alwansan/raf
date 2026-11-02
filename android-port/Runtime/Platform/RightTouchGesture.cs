using System;

namespace RaftAndroid.Platform
{
    public enum RightTouchCommand { Move, Tap, Down, Up }

    // Engine-independent ownership/timing policy. The adapter must deliver Tap
    // as a one-update right-button pulse; this policy never emits a left button.
    public sealed class RightTouchGesture
    {
        public const double HoldSeconds = 0.5;
        private int owner;
        private bool active, held;
        private double began, lastTime;
        private float x, y;
        private readonly Action<RightTouchCommand, float, float> emit;

        public RightTouchGesture(Action<RightTouchCommand, float, float> emit)
        { this.emit = emit ?? throw new ArgumentNullException(nameof(emit)); }

        public bool Active { get { return active; } }
        public bool Held { get { return held; } }

        public void Begin(int id, float px, float py, double time)
        {
            if (active || !Valid(px, py, time)) return;
            owner = id; active = true; held = false;
            began = lastTime = time; x = px; y = py;
            emit(RightTouchCommand.Move, x, y);
        }

        public void Move(int id, float px, float py, double time)
        {
            if (!active || owner != id || !Valid(px, py, time) || time < lastTime) return;
            x = px; y = py; lastTime = time;
            Tick(time);
            emit(RightTouchCommand.Move, x, y);
        }

        public void Tick(double time)
        {
            if (!active || held || double.IsNaN(time) || double.IsInfinity(time) || time < lastTime) return;
            if (time - began >= HoldSeconds)
            {
                held = true;
                emit(RightTouchCommand.Down, x, y);
            }
        }

        public void End(int id, float px, float py, double time, bool cancelled)
        {
            if (!active || owner != id) return;
            if (!Valid(px, py, time) || time < lastTime) { Cancel(); return; }
            x = px; y = py;
            if (!cancelled) Tick(time);
            bool wasHeld = held;
            active = held = false;
            if (wasHeld) emit(RightTouchCommand.Up, x, y);
            else if (!cancelled) emit(RightTouchCommand.Tap, x, y);
        }

        public void Cancel()
        {
            bool release = held;
            active = held = false;
            if (release) emit(RightTouchCommand.Up, x, y);
        }

        private static bool Valid(float x, float y, double time)
        {
            return !float.IsNaN(x) && !float.IsInfinity(x) &&
                !float.IsNaN(y) && !float.IsInfinity(y) &&
                !double.IsNaN(time) && !double.IsInfinity(time);
        }
    }
}
