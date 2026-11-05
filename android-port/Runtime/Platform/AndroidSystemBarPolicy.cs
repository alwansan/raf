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

        public static int MergeLegacy(int existing)
        {
            return existing | LegacyFullscreen | LegacyHideNavigation |
                   LegacyImmersiveSticky | LegacyLayoutStable |
                   LegacyLayoutHideNavigation | LegacyLayoutFullscreen;
        }
    }
}
