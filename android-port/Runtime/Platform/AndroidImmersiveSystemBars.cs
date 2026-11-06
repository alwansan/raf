#if UNITY_ANDROID && !UNITY_EDITOR
using System.Threading;
using UnityEngine;

namespace RaftAndroid.Platform
{
    // Independent Android-only fullscreen policy: does not alter Screen
    // resolution, touch, controller, Unity cursor, input or system gestures.
    public sealed class AndroidImmersiveSystemBars : MonoBehaviour
    {
        private static AndroidImmersiveSystemBars instance;
        private volatile bool active, focused = true, paused;
        private bool supported;
        private int sdk;
        private int hideGeneration;
        private float nextRefresh;

        [RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.BeforeSceneLoad)]
        private static void Install()
        {
            if (instance != null) return;
            var host = new GameObject("RaftAndroidImmersiveSystemBars");
            Object.DontDestroyOnLoad(host);
            host.AddComponent<AndroidImmersiveSystemBars>();
        }

        private void OnEnable()
        {
            if (instance != null && instance != this)
            {
                enabled = false;
                return;
            }
            instance = this;
            Interlocked.Increment(ref hideGeneration);
            active = true;
            try
            {
                using (var version = new AndroidJavaClass("android.os.Build$VERSION"))
                    sdk = version.GetStatic<int>("SDK_INT");
                supported = AndroidSystemBarPolicy.CanHide(sdk);
            }
            catch (AndroidJavaException) { supported = false; }
            ScheduleHide();
        }

        private void Update()
        {
            if (!supported || !AndroidSystemBarPolicy.ShouldApply(active, focused, paused))
                return;
            // Only recover if Unity/Android resets the requested window flags.
            // Deliberately sparse: never fight normal transient edge gestures.
            if (Time.unscaledTime >= nextRefresh)
                ScheduleHide();
        }

        private static int ActivityIdentity(AndroidJavaObject activity)
        {
            if (activity == null) return 0;
            using (var system = new AndroidJavaClass("java.lang.System"))
                return system.CallStatic<int>("identityHashCode", activity);
        }

        private void ScheduleHide()
        {
            if (!supported || !AndroidSystemBarPolicy.ShouldApply(active, focused, paused))
                return;
            nextRefresh = Time.unscaledTime + 15f;
            int queuedGeneration = Interlocked.Increment(ref hideGeneration);
            try
            {
                using (var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
                using (var activity = player.GetStatic<AndroidJavaObject>("currentActivity"))
                {
                    if (activity == null) return;
                    // Never retain a Java Activity object across a deferred UI
                    // runnable: carry only the nonzero identity and generation.
                    int queuedActivityIdentity = ActivityIdentity(activity);
                    if (queuedActivityIdentity == 0) return;
                    activity.Call("runOnUiThread", new AndroidJavaRunnable(() =>
                    {
                        if (!AndroidSystemBarPolicy.ShouldApply(active, focused, paused) ||
                            queuedGeneration != Volatile.Read(ref hideGeneration))
                            return;
                        try
                        {
                            using (var unityPlayer = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
                            using (var current = unityPlayer.GetStatic<AndroidJavaObject>("currentActivity"))
                            {
                                if (current == null ||
                                    !AndroidSystemBarPolicy.CanApplyQueuedHide(
                                        active, focused, paused, queuedGeneration,
                                        Volatile.Read(ref hideGeneration),
                                        queuedActivityIdentity, ActivityIdentity(current)))
                                    return;
                                using (var window = current.Call<AndroidJavaObject>("getWindow"))
                                {
                                    if (window == null) return;
                                    if (AndroidSystemBarPolicy.UseModernInsets(sdk))
                                    {
                                        // Android 11+ native API. OS gestures still reveal
                                        // transient overlays and preserve Back/Home access.
                                        using (var controller = window.Call<AndroidJavaObject>("getInsetsController"))
                                        using (var types = new AndroidJavaClass("android.view.WindowInsets$Type"))
                                        {
                                            if (controller == null) return;
                                            int bars = types.CallStatic<int>("systemBars");
                                            controller.Call("setSystemBarsBehavior",
                                                AndroidSystemBarPolicy.TransientBarsBySwipe);
                                            if (queuedGeneration != Volatile.Read(ref hideGeneration) ||
                                                !AndroidSystemBarPolicy.ShouldApply(active, focused, paused))
                                                return;
                                            controller.Call("hide", bars);
                                        }
                                    }
                                    else
                                    {
                                        using (var decor = window.Call<AndroidJavaObject>("getDecorView"))
                                        {
                                            if (decor == null) return;
                                            int previous = decor.Call<int>("getSystemUiVisibility");
                                            int merged = AndroidSystemBarPolicy.MergeLegacy(previous);
                                            if (merged != previous &&
                                                queuedGeneration == Volatile.Read(ref hideGeneration) &&
                                                AndroidSystemBarPolicy.ShouldApply(active, focused, paused))
                                                decor.Call("setSystemUiVisibility", merged);
                                        }
                                    }
                                }
                            }
                        }
                        catch (AndroidJavaException) { /* Unity retains its existing fullscreen state. */ }
                    }));
                }
            }
            catch (AndroidJavaException) { /* Platform integration is optional. */ }
        }

        private void OnApplicationFocus(bool value)
        {
            focused = value;
            Interlocked.Increment(ref hideGeneration);
            if (value) ScheduleHide();
        }

        private void OnApplicationPause(bool value)
        {
            paused = value;
            Interlocked.Increment(ref hideGeneration);
            if (!value) ScheduleHide();
        }

        private void OnDisable()
        {
            active = false;
            Interlocked.Increment(ref hideGeneration);
            if (instance == this) instance = null;
            // Android keeps its own system gesture exits; do not force-show
            // bars or change another Activity's window when leaving Raft.
        }
    }
}
#endif
