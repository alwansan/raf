using System;

namespace RaftAndroid.Editor
{
    // Shared by the real Unity import hook and executable non-Unity fixtures.
    internal static class AndroidColourTexturePolicy
    {
        internal static bool ShouldCompress(bool default2D, bool srgb, bool androidOverride,
                                            bool fontDependency, string extension, string androidFormat)
        {
            if (!default2D || !srgb || androidOverride || fontDependency) return false;
            extension = (extension ?? "").ToLowerInvariant();
            if (extension != ".png" && extension != ".jpg" && extension != ".jpeg" &&
                extension != ".tga" && extension != ".bmp") return false;
            return androidFormat == "RGB24" || androidFormat == "RGBA32" || androidFormat == "ARGB32";
        }
    }
}
