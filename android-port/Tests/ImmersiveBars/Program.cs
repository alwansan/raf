using System;
using RaftAndroid.Platform;

static class Program
{
    static int count;
    static void Check(bool condition, string reason)
    {
        if (!condition) throw new InvalidOperationException(reason);
        count++;
    }

    static int Main()
    {
        Check(!AndroidSystemBarPolicy.CanHide(25), "Android 7 does not enter this bridge");
        Check(AndroidSystemBarPolicy.CanHide(26), "API26 legacy supported");
        Check(AndroidSystemBarPolicy.CanHide(29), "Android10 legacy supported");
        Check(AndroidSystemBarPolicy.CanHide(30), "API30 supported");
        Check(!AndroidSystemBarPolicy.UseModernInsets(29), "Android10 uses legacy flags");
        Check(AndroidSystemBarPolicy.UseModernInsets(30), "Android11 WindowInsetsController");
        Check(AndroidSystemBarPolicy.UseModernInsets(35), "Android15 WindowInsetsController");
        Check(AndroidSystemBarPolicy.TransientBarsBySwipe == 2,
            "Native transient system gestures remain enabled");
        const int mask = 0x1706;
        Check(AndroidSystemBarPolicy.MergeLegacy(0) == mask,
            "Legacy flags contain only expected fullscreen/immersive bits");
        Check(AndroidSystemBarPolicy.MergeLegacy(mask) == mask,
            "Legacy flags are idempotent");
        const int original = unchecked((int)0x80000008u);
        int merged = AndroidSystemBarPolicy.MergeLegacy(original);
        Check((merged & original) == original, "Existing Unity flags preserved");
        Check((merged & mask) == mask, "All six system-bar flags requested");
        Check(AndroidSystemBarPolicy.MergeLegacy(merged) == merged,
            "Reapplying legacy flags does not toggle state");
        Check(AndroidSystemBarPolicy.ShouldApply(true, true, false),
            "Active foreground game hides bars");
        Check(!AndroidSystemBarPolicy.ShouldApply(false, true, false),
            "Disabled component does not touch Activity");
        Check(!AndroidSystemBarPolicy.ShouldApply(true, false, false),
            "Focus loss leaves system UI alone");
        Check(!AndroidSystemBarPolicy.ShouldApply(true, true, true),
            "Pause leaves system UI alone");
        Check(!AndroidSystemBarPolicy.ShouldApply(false, false, true),
            "Stopped game leaves system UI alone");
        Check(AndroidSystemBarPolicy.CanApplyQueuedHide(true, true, false,
            3, 3, 120, 120), "Current owner and generation may hide");
        Check(!AndroidSystemBarPolicy.CanApplyQueuedHide(true, true, false,
            3, 4, 120, 120), "Stale generation must fail");
        Check(!AndroidSystemBarPolicy.CanApplyQueuedHide(true, true, false,
            4, 3, 120, 120), "Future generation must fail");
        Check(!AndroidSystemBarPolicy.CanApplyQueuedHide(true, true, false,
            0, 0, 120, 120), "Uninitialized generation must fail");
        Check(!AndroidSystemBarPolicy.CanApplyQueuedHide(true, true, false,
            3, 3, 120, 121), "Another Activity must fail");
        Check(!AndroidSystemBarPolicy.CanApplyQueuedHide(true, true, false,
            3, 3, 0, 120), "Unbound Activity must fail");
        Check(!AndroidSystemBarPolicy.CanApplyQueuedHide(true, true, false,
            3, 3, 120, 0), "Missing live Activity must fail");
        Check(!AndroidSystemBarPolicy.CanApplyQueuedHide(true, false, false,
            3, 3, 120, 120), "Background must fail");
        Check(!AndroidSystemBarPolicy.CanApplyQueuedHide(true, true, true,
            3, 3, 120, 120), "Pause must fail");
        Check(!AndroidSystemBarPolicy.CanApplyQueuedHide(false, true, false,
            3, 3, 120, 120), "Disabled state must fail");
        Check(AndroidSystemBarPolicy.CanApplyQueuedHide(true, true, false,
            3, 3, 120, 120, true), "Focused original Android window may hide");
        Check(!AndroidSystemBarPolicy.CanApplyQueuedHide(true, true, false,
            3, 3, 120, 120, false), "Native focus loss overrides stale Unity focus");
        Check(!AndroidSystemBarPolicy.CanApplyQueuedHide(true, true, false,
            3, 4, 120, 120, true), "Focused window cannot bypass stale generation");
        Check(!AndroidSystemBarPolicy.CanApplyQueuedHide(true, true, false,
            3, 3, 120, 121, true), "Focused other Activity cannot borrow owner");
        Check(!AndroidSystemBarPolicy.CanApplyQueuedHide(true, true, true,
            3, 3, 120, 120, true), "Focused window cannot bypass paused Unity");
        Console.WriteLine("T4_SYSTEM_BARS_POLICY_CSHARP passed=" + count +
            " authenticUnityABICompiledSeparately=true androidDeviceVerified=false");
        return 0;
    }
}
