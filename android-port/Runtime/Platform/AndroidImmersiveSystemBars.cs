#if UNITY_ANDROID && !UNITY_EDITOR
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

        private void ScheduleHide()
        {
            if (!supported || !AndroidSystemBarPolicy.ShouldApply(active, focused, paused))
                return;
            nextRefresh = Time.unscaledTime + 15f;
            try
            {
                using (var player = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
                using (var activity = player.GetStatic<AndroidJavaObject>("currentActivity"))
                {
                    if (activity == null) return;
                    activity.Call("runOnUiThread", new AndroidJavaRunnable(() =>
                    {
                        if (!AndroidSystemBarPolicy.ShouldApply(active, focused, paused))
                            return;
                        try
                        {
                            using (var unityPlayer = new AndroidJavaClass("com.unity3d.player.UnityPlayer"))
                            using (var current = unityPlayer.GetStatic<AndroidJavaObject>("currentActivity"))
                            {
                                if (current == null) return;
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
                                            if (merged != previous)
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
            if (value) ScheduleHide();
        }

        private void OnApplicationPause(bool value)
        {
            paused = value;
            if (!value) ScheduleHide();
        }

        private void OnDisable()
        {
            active = false;
            if (instance == this) instance = null;
            // Android keeps its own system gesture exits; do not force-show
            // bars or change another Activity's window when leaving Raft.
        }
    }
}
#endif
