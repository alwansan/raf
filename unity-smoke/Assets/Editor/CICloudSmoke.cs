using System;
using UnityEditor;
using UnityEngine;

public static class CICloudSmoke
{
    public static void Validate()
    {
        var expected = "2021.3.45f2";
        var actual = Application.unityVersion;
        Debug.Log("UNITY_EDITOR_CLOUD_SMOKE_STARTED " + actual);
        if (!string.Equals(actual, expected, StringComparison.Ordinal))
            throw new Exception("Unity version mismatch: expected " + expected + ", got " + actual);
        if (EditorUserBuildSettings.activeBuildTarget != BuildTarget.Android)
            throw new Exception("Expected Android target. Got: " + EditorUserBuildSettings.activeBuildTarget);
        Debug.Log("UNITY_EDITOR_CLOUD_SMOKE_OK (Editor licensed, scripts compiled, Android build target active)");
    }
}
