using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using RaftGraphicsLab;

namespace RaftGraphicsLabEditor
{
    public static class GfxUnifiedAndroidBuilder098
    {
        public static void Build()
        {
            GfxOriginalStandardPcWitness098.Run();
            GfxMultiAndroidBuilder.PrepareModelScene();
            var viewer=UnityEngine.Object.FindObjectOfType<GfxMultiViewer>();
            if(viewer==null)throw new InvalidOperationException("GFX098_VIEWER_MISSING");
            GfxUnifiedSourceMaterials098.Apply(viewer);
            viewer.gameObject.AddComponent<GfxModelMatrixProbe098>();
            new GameObject("GFX098_LabNavigation").AddComponent<GfxUnifiedLabMenu098>();
            var scene=viewer.gameObject.scene;EditorSceneManager.MarkSceneDirty(scene);
            if(!EditorSceneManager.SaveScene(scene,"Assets/Scenes/GfxUnifiedModels098.unity"))throw new InvalidOperationException("GFX098_MODEL_SCENE_SAVE");
            GfxAffineReferenceAndroidBuilder.PrepareAffineScene();
            PlayerSettings.companyName="alwansan";PlayerSettings.productName="Raft Unified Model GPU Laboratory";
            PlayerSettings.bundleVersion="0.98.0";PlayerSettings.Android.bundleVersionCode=98;
            PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Android,"com.alwansan.raft.graphicslab.unified098");
            PlayerSettings.defaultInterfaceOrientation=UIOrientation.LandscapeLeft;
            PlayerSettings.allowedAutorotateToLandscapeLeft=true;PlayerSettings.allowedAutorotateToLandscapeRight=false;
            PlayerSettings.colorSpace=ColorSpace.Linear;
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Android,ScriptingImplementation.IL2CPP);
            PlayerSettings.Android.targetArchitectures=AndroidArchitecture.ARM64;
            PlayerSettings.Android.minSdkVersion=AndroidSdkVersions.AndroidApiLevel29;
            PlayerSettings.Android.targetSdkVersion=AndroidSdkVersions.AndroidApiLevelAuto;
            PlayerSettings.SetGraphicsAPIs(BuildTarget.Android,new[]{GraphicsDeviceType.OpenGLES3});
            PlayerSettings.Android.useAPKExpansionFiles=false;EditorUserBuildSettings.buildAppBundle=false;
            QualitySettings.shadowDistance=20;AssetDatabase.SaveAssets();AssetDatabase.Refresh();
            string apk="builds/Android/GFX098-Unified-Models-GPU-Lab.apk";Directory.CreateDirectory(Path.GetDirectoryName(apk));
            var report=BuildPipeline.BuildPlayer(new[]{
                new EditorBuildSettingsScene("Assets/Scenes/GfxUnifiedModels098.unity",true),
                new EditorBuildSettingsScene("Assets/Scenes/GfxAffineReferenceProbe.unity",true)},apk,BuildTarget.Android,BuildOptions.None);
            if(report.summary.result!=BuildResult.Succeeded||!File.Exists(apk))throw new InvalidOperationException("GFX098_ANDROID_BUILD_FAILED");
            Debug.Log("GFX098_UNIFIED_ANDROID_BUILD_PASS scenes=2 models=6 material_slots=7 material_aliases=6 texture_aliases=18 originalShaderRestored=false phase_closed=false");
        }
    }
}
