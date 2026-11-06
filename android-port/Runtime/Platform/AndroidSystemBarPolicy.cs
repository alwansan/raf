namespace RaftAndroid.Platform
{
    // Only additive Android system-UI flags; never clear Unity-owned bits.
    // Android 11+ uses WindowInsetsController rather than this legacy mask.
    public static class AndroidSystemBarPolicy
    {
        public const int LegacyFullscreen = 0x00000004;
        public const int LegacyHideNavigation = 0x00000002;
        public const int LegacyImmersiveSticky = 0x00001000;
        public const int LegacyLayoutStable = 0x00000100;
        public const int LegacyLayoutHideNavigation = 0x00000200;
        public const int LegacyLayoutFullscreen = 0x00000400;
        public const int TransientBarsBySwipe = 2;

        public static bool UseModernInsets(int sdk) { return sdk >= 30; }
        public static bool CanHide(int sdk) { return sdk >= 26; }
        public static bool ShouldApply(bool active, bool focused, bool paused)
        {
            return active && focused && !paused;
        }

        // A queued runnable must not apply to a replacement Activity or
        // a stale focus/pause generation. A zero identity is unbound.
        public static bool CanApplyQueuedHide(bool active, bool focused, bool paused,
            int queuedGeneration, int currentGeneration,
            int queuedActivityIdentity, int currentActivityIdentity)
        {
            return ShouldApply(active, focused, paused) &&
                queuedGeneration != 0 && queuedGeneration == currentGeneration &&
                queuedActivityIdentity != 0 &&
                queuedActivityIdentity == currentActivityIdentity;
        }

        // Android window focus can diverge from Unity lifecycle focus.
        // Refuse a queued hide while a dialog or system overlay owns focus.
        public static bool CanApplyQueuedHide(bool active, bool focused, bool paused,
            int queuedGeneration, int currentGeneration,
            int queuedActivityIdentity, int currentActivityIdentity,
            bool androidWindowFocused)
        {
            return androidWindowFocused &&
                CanApplyQueuedHide(active, focused, paused, queuedGeneration,
                    currentGeneration, queuedActivityIdentity, currentActivityIdentity);
        }

        public static int MergeLegacy(int existing)
        {
            return existing | LegacyFullscreen | LegacyHideNavigation |
                   LegacyImmersiveSticky | LegacyLayoutStable |
                   LegacyLayoutHideNavigation | LegacyLayoutFullscreen;
        }
    }
}
