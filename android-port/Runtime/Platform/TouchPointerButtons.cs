using System;

namespace RaftAndroid.Platform
{
    // A tap remains pressed for one input update. Rapid taps are separated by
    // a released update so neither UI polling nor legacy callers lose clicks.
    public sealed class TouchPointerButtons
    {
        private readonly Action<bool> emit;
        private bool held, pulse;
        private int pending;
        public bool Pressed { get; private set; }
        public TouchPointerButtons(Action<bool> emit) { this.emit = emit ?? throw new ArgumentNullException(nameof(emit)); }
        private void Set(bool value) { if (Pressed == value) return; Pressed = value; emit(value); }
        public void Hold(bool value) { held = value; Set(held || pulse); }
        public void Tap()
        {
            if (!Pressed && !pulse && pending == 0) { pulse = true; Set(true); }
            else pending++;
        }
        public void BeginUpdate()
        {
            if (pulse) { pulse = false; Set(held); return; }
            if (!held && pending > 0) { pending--; pulse = true; Set(true); }
        }
        public void Cancel() { pending = 0; held = pulse = false; Set(false); }
    }
}
