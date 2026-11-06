#if UNITY_EDITOR
using UnityEngine;

// Original authenticated mouse-axis/cursor assignments are rewritten into
// these three static calls. In the Unity Editor, including for an Android
// build target, they must remain compilable with non-capturing legacy input.
internal static class UnityEditorBridgeUsage
{
    internal static CursorLockMode Lock(CursorLockMode requested)
    {
        return RaftAndroid.Platform.AndroidPhysicalMouseCapture.ApplyCursorLock(requested);
    }

    internal static float ReadOriginalMouse()
    {
        return RaftAndroid.Platform.AndroidPhysicalMouseCapture.GetAxis("Mouse X")
            + RaftAndroid.Platform.AndroidPhysicalMouseCapture.GetAxisRaw("Mouse Y");
    }
}
#endif
