using System;

namespace RaftAndroid.Platform
{
    // Platform-independent buffer. The Android UI callback never calls Unity APIs.
    // Readers in multiple original camera scripts see the same per-frame sample.
    public sealed class PhysicalMouseDeltaAccumulator
    {
        private readonly object gate = new object();
        private float pendingX, pendingY, frameX, frameY;
        private int sampledFrame = -1;
        private int received;

        public int ReceivedCount
        {
            get { lock (gate) return received; }
        }

        public void Push(float x, float y)
        {
            if (float.IsNaN(x) || float.IsNaN(y) ||
                float.IsInfinity(x) || float.IsInfinity(y) ||
                Math.Abs(x) > 10000f || Math.Abs(y) > 10000f)
                return;
            lock (gate)
            {
                pendingX = Math.Max(-4096f, Math.Min(4096f, pendingX + x));
                pendingY = Math.Max(-4096f, Math.Min(4096f, pendingY + y));
                if (received < int.MaxValue) received++;
            }
        }

        // Android's captured getY moves downward; Unity's legacy Mouse Y is up.
        // The first-device tuning factor is deliberately bounded and constant;
        // no claim of exact PC sensitivity without a measured device trace.
        public float Sample(int frame, bool horizontal)
        {
            lock (gate)
            {
                if (sampledFrame != frame)
                {
                    frameX = pendingX;
                    frameY = pendingY;
                    pendingX = pendingY = 0;
                    sampledFrame = frame;
                }
                return (horizontal ? frameX : -frameY) * 0.1f;
            }
        }

        public void Reset()
        {
            lock (gate)
            {
                pendingX = pendingY = frameX = frameY = 0;
                sampledFrame = -1;
                received = 0;
            }
        }
    }
}
