using System;

namespace RaftAndroid.Audio
{
    // Platform-independent ordering gate; original FMOD managed providers remain intact.
    public sealed class FmodAndroidStartup
    {
        public const uint ExpectedVersion = 0x00020215;
        public bool Initialized { get; private set; }

        public void Initialize(Action loadOriginalLibraries, Action initializeJava, Func<uint> readNativeVersion)
        {
            if (Initialized) return;
            if (loadOriginalLibraries == null || initializeJava == null || readNativeVersion == null)
                throw new ArgumentNullException("FMOD startup operations are required");
            loadOriginalLibraries();
            initializeJava();
            uint actual = readNativeVersion();
            if (actual != ExpectedVersion)
                throw new InvalidOperationException("FMOD native version mismatch: " + actual.ToString("X8"));
            Initialized = true;
        }
    }
}
