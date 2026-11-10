using System;
using System.IO;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;
using UnityEditor.Build.Reporting;
using RaftGraphicsLab;

namespace RaftGraphicsLabEditor
{
    /// <summary>
    /// Dedicated synthetic-only GFX-MULTI-041 Android app. The original
    /// Raft Shader48 is NEVER bundled, converted, or claimed to be recovered.
    /// Uses no ZIP2 assets; unique package avoids replacing earlier labs.
    /// </summary>
    public static class GfxAffineReferenceAndroidBuilder
    {
        private static Material DiagnosticMaterial(string mode)
        {
            string shaderName="Hidden/GfxLab/Interpolation"+mode;
            string path="Assets/GfxInterpolationGenerated/"+mode+".mat";
            var shader=Shader.Find(shaderName);
            if(shader==null)
                throw new InvalidOperationException(
                    "GFX041_DIAGNOSTIC_SHADER_NOT_IMPORTED_"+mode);
            var mat=AssetDatabase.LoadAssetAtPath<Material>(path);
            if(mat==null)
            {
                mat=new Material(shader);
                mat.name="SYNTHETIC_ONLY_GFX041_"+mode;
                AssetDatabase.CreateAsset(mat,path);
            }
            else
                mat.shader=shader;
            EditorUtility.SetDirty(mat);
            return mat;
        }

        public static void PrepareAffineScene()
        {
            Directory.CreateDirectory("Assets/GfxInterpolationGenerated");
            Directory.CreateDirectory("Assets/Scenes");
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            // Assets referenced by the saved scene force all 3 synthetic
            // shaders into the APK even if Unity Editor uses a non-GLES GPU.
            var materials=new Material[4];
            materials[0]=DiagnosticMaterial("Linear");
            materials[1]=DiagnosticMaterial("Flat");
            materials[2]=DiagnosticMaterial("NoPerspective");
            materials[3]=DiagnosticMaterial("AffineEmulated");

            var scene=EditorSceneManager.NewScene(
                NewSceneSetup.EmptyScene,NewSceneMode.Single);
            var root=new GameObject(
                "GFX041_SyntheticGPUOnly_NoRaftShader48");
            var camera=root.AddComponent<Camera>();
            camera.clearFlags=CameraClearFlags.SolidColor;
            camera.backgroundColor=new Color(.055f,.075f,.1f,1f);
            camera.orthographic=true;
            camera.orthographicSize=1f;
            camera.nearClipPlane=.1f;
            camera.farClipPlane=10f;
            root.tag="MainCamera";
            root.AddComponent<GfxSessionRecorder>();
            root.AddComponent<GfxAffineReferenceProbe>();

            // Material references guarantee that Shader.Find can locate
            // all three test shaders in the Android player build.
            var hold=new GameObject(
                "GFX041_DiagnosticShaders_KeepInBuild_NotRaft");
            for(int i=0;i<materials.Length;i++)
            {
                var child=new GameObject("Keep_"+materials[i].name);
                child.transform.SetParent(hold.transform,false);
                var filter=child.AddComponent<MeshFilter>();
                var renderer=child.AddComponent<MeshRenderer>();
                renderer.sharedMaterial=materials[i];
                renderer.enabled=false; // the probe draws the GPU triangle directly
                filter.sharedMesh=null;
            }
            if(!EditorSceneManager.SaveScene(scene,
                "Assets/Scenes/GfxAffineReferenceProbe.unity"))
                throw new InvalidOperationException(
                    "GFX041_SYNTHETIC_PROBE_SCENE_SAVE_FAILED");
            EditorSceneManager.MarkSceneDirty(scene);

        }

        public static void Build()
        {
            PrepareAffineScene();
            PlayerSettings.companyName="alwansan";
            PlayerSettings.productName="Raft GFX Affine Reference Diagnostic";
            PlayerSettings.bundleVersion="0.7.0";
            PlayerSettings.Android.bundleVersionCode=7;
            PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Android,
                "com.alwansan.raft.graphicslab.affinereference");
            PlayerSettings.defaultInterfaceOrientation=UIOrientation.LandscapeLeft;
            PlayerSettings.allowedAutorotateToLandscapeLeft=true;
            PlayerSettings.allowedAutorotateToLandscapeRight=false;
            PlayerSettings.colorSpace=ColorSpace.Linear;
            PlayerSettings.SetScriptingBackend(
                NamedBuildTarget.Android,ScriptingImplementation.IL2CPP);
            PlayerSettings.Android.targetArchitectures=AndroidArchitecture.ARM64;
            PlayerSettings.Android.minSdkVersion=AndroidSdkVersions.AndroidApiLevel26;
            PlayerSettings.Android.targetSdkVersion=AndroidSdkVersions.AndroidApiLevelAuto;
            PlayerSettings.SetGraphicsAPIs(
                BuildTarget.Android,new[]{GraphicsDeviceType.OpenGLES3});
            PlayerSettings.Android.useAPKExpansionFiles=false;
            EditorUserBuildSettings.buildAppBundle=false;
            QualitySettings.vSyncCount=0;
            AssetDatabase.SaveAssets();

            string apk="builds/Android/GfxLab-AffineReference-GPUProbe.apk";
            Directory.CreateDirectory(Path.GetDirectoryName(apk));
            var report=BuildPipeline.BuildPlayer(
                new[]{new EditorBuildSettingsScene(
                    "Assets/Scenes/GfxAffineReferenceProbe.unity",true)},
                apk,BuildTarget.Android,BuildOptions.None);
            if(report.summary.result!=BuildResult.Succeeded ||
               !File.Exists(apk) || new FileInfo(apk).Length<1024*1024)
                throw new InvalidOperationException(
                    "GFX041_SIGNED_ANDROID_APK_BUILD_FAILED");
            Debug.Log("GFX041_SIGNED_ANDROID_DIAGNOSTIC_BUILD_OK"+
                " original_shader_restored=false"+
                " synthetic_only=true GLES3=true"+
                " PC_GPU_PIXEL_PARITY=false");
        }
    }
}
