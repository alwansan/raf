using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;

public static class BuildWater155
{
    public static void Build()
    {
        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        var camera = new GameObject("Camera").AddComponent<Camera>();
        camera.transform.position = new Vector3(6, 5, -7);
        camera.transform.LookAt(Vector3.zero);
        camera.backgroundColor = new Color(0.055f, 0.09f, 0.14f);
        camera.clearFlags = CameraClearFlags.SolidColor;

        var sun = new GameObject("Directional Light").AddComponent<Light>();
        sun.type = LightType.Directional;
        sun.intensity = 1.15f;
        sun.transform.rotation = Quaternion.Euler(50, -35, 0);
        RenderSettings.ambientLight = new Color(0.36f, 0.43f, 0.48f);

        var root = new GameObject("Water155");
        var probe = root.AddComponent<Water155>();
        probe.compute = AssetDatabase.LoadAssetAtPath<ComputeShader>("Assets/Water155.compute");
        var shader = Shader.Find("Standard");
        if (probe.compute == null || shader == null)
            throw new InvalidOperationException("GFX155 scene asset import failed");
        var material = new Material(shader) { color = new Color(0.03f, 0.43f, 0.58f) };
        material.SetFloat("_Glossiness", 0.64f);
        AssetDatabase.CreateAsset(material, "Assets/Water155.mat");
        probe.surface = root.AddComponent<MeshFilter>();
        root.AddComponent<MeshRenderer>().sharedMaterial = material;
        const string scenePath = "Assets/Water155.unity";
        if (!EditorSceneManager.SaveScene(scene, scenePath))
            throw new InvalidOperationException("GFX155 scene save failed");

        PlayerSettings.productName = "GFX155 Water Lab";
        PlayerSettings.SetApplicationIdentifier(BuildTargetGroup.Android, "com.alwansan.gfx155.water");
        PlayerSettings.bundleVersion = "1.0";
        PlayerSettings.Android.bundleVersionCode = 1;
        PlayerSettings.Android.minSdkVersion = AndroidSdkVersions.AndroidApiLevel29;
        PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
        PlayerSettings.Android.useCustomKeystore = false;
        PlayerSettings.defaultInterfaceOrientation = UIOrientation.LandscapeLeft;
        PlayerSettings.SetScriptingBackend(BuildTargetGroup.Android, ScriptingImplementation.IL2CPP);
        PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android, false);
        PlayerSettings.SetGraphicsAPIs(BuildTarget.Android, new[] { GraphicsDeviceType.Vulkan });
        EditorUserBuildSettings.buildAppBundle = false;

        const string output = "gfx155-output/GFX155-Water-Lab.apk";
        Directory.CreateDirectory(Path.GetDirectoryName(output));
        var report = BuildPipeline.BuildPlayer(new[] { scenePath }, output, BuildTarget.Android, BuildOptions.None);
        if (report.summary.result != BuildResult.Succeeded)
            throw new InvalidOperationException("GFX155 Android build " + report.summary.result);
    }
}
