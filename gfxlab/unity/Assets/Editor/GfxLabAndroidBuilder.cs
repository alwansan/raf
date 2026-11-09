using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;
using RaftGraphicsLab;

namespace RaftGraphicsLabEditor
{
    /// <summary>Fails closed unless an authenticated original source OBJ has been staged.</summary>
    public static class GfxLabAndroidBuilder
    {
        [Serializable] private sealed class Evidence
        {
            public bool source_pinned;
            public bool original_geometry_exported;
            public int part_count;
            public int vertices;
            public int faces;
            public string model_category;
        }

        private static Material StoreMaterial(string file, Shader shader, Color color)
        {
            if (shader == null || !shader.isSupported)
                throw new InvalidOperationException("Required Unity built-in shader unavailable: " + file);
            string full = "Assets/GfxLabGenerated/" + file;
            var material = AssetDatabase.LoadAssetAtPath<Material>(full);
            if (material == null)
            {
                material = new Material(shader);
                material.name = Path.GetFileNameWithoutExtension(file);
                AssetDatabase.CreateAsset(material, full);
            }
            material.shader = shader;
            material.color = color;
            EditorUtility.SetDirty(material);
            return material;
        }

        public static void Build()
        {
            string root = Directory.GetCurrentDirectory();
            string modelDir = "Assets/OriginalModel";
            string evidenceFile = Path.Combine(modelDir, "evidence.json");
            if (!File.Exists(evidenceFile))
                throw new InvalidOperationException("GFXLAB_STOP: source-authentic evidence.json absent");
            var evidence = JsonUtility.FromJson<Evidence>(File.ReadAllText(evidenceFile));
            if (evidence == null || !evidence.source_pinned || !evidence.original_geometry_exported
                || evidence.part_count < 1 || evidence.vertices < 16 || evidence.faces < 1)
                throw new InvalidOperationException("GFXLAB_STOP: no authenticated original geometry");
            string[] paths = Directory.GetFiles(modelDir, "Part*.obj")
                .OrderBy(x => x, StringComparer.Ordinal).Select(x => x.Replace('\\','/')).ToArray();
            if (paths.Length != evidence.part_count || paths.Length > 8)
                throw new InvalidOperationException("GFXLAB_STOP: original Mesh part count drift");

            Directory.CreateDirectory("Assets/GfxLabGenerated");
            Directory.CreateDirectory("Assets/Scenes");
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var rootGo = new GameObject("OriginalMeshFromAuthenticatedZip2");
            var renderers = new System.Collections.Generic.List<Renderer>();
            int selectedMeshes = 0;
            int actualVertices = 0;
            int actualTriangles = 0;

            foreach (string path in paths)
            {
                GameObject prefab = AssetDatabase.LoadAssetAtPath<GameObject>(path);
                if (prefab == null)
                    throw new InvalidOperationException("GFXLAB_STOP: OBJ failed actual Unity importer");
                GameObject instance = UnityEngine.Object.Instantiate(prefab);
                instance.name = "OriginalMeshPart" + selectedMeshes.ToString("00");
                instance.transform.SetParent(rootGo.transform, true);
                foreach (var filter in instance.GetComponentsInChildren<MeshFilter>(true))
                {
                    Mesh mesh = filter.sharedMesh;
                    if (mesh == null || mesh.vertexCount == 0) continue;
                    selectedMeshes++;
                    actualVertices += mesh.vertexCount;
                    foreach (int[] tri in Enumerable.Range(0,mesh.subMeshCount)
                        .Select(i => mesh.GetTriangles(i)))
                        actualTriangles += tri.Length / 3;
                }
                renderers.AddRange(instance.GetComponentsInChildren<Renderer>(true));
            }
            if (selectedMeshes < 1 || renderers.Count == 0)
                throw new InvalidOperationException("GFXLAB_STOP: actual Unity imported Mesh/Renderer count is zero");

            var whiteLit = StoreMaterial("WhiteLit.mat", Shader.Find("Standard"), Color.white);
            var whiteUnlit = StoreMaterial("WhiteUnlit.mat", Shader.Find("Unlit/Color"), Color.white);
            var groundMat = StoreMaterial("Ground.mat", Shader.Find("Standard"), new Color(.22f,.24f,.27f,1));
            foreach (Renderer renderer in renderers)
            {
                var mat = renderer.sharedMaterials;
                if (mat.Length==0) mat = new [] { whiteLit };
                for (int i=0; i<mat.Length; i++) mat[i]=whiteLit;
                renderer.sharedMaterials=mat;
            }

            Bounds bounds = renderers[0].bounds;
            for (int i=1;i<renderers.Count;i++) bounds.Encapsulate(renderers[i].bounds);
            if (bounds.size.y < .00001f || (float.IsNaN(bounds.size.y) || float.IsInfinity(bounds.size.y)))
                throw new InvalidOperationException("GFXLAB_STOP: model bounds not valid");
            float scale = Mathf.Clamp(1.8f / bounds.size.y, .0001f, 1000f);
            rootGo.transform.localScale=Vector3.one*scale;
            rootGo.transform.position= new Vector3(-bounds.center.x*scale,
                -bounds.min.y*scale + .08f, -bounds.center.z*scale);
            if ((float.IsNaN(rootGo.transform.position.x) || float.IsInfinity(rootGo.transform.position.x)) ||
                (float.IsNaN(rootGo.transform.position.y) || float.IsInfinity(rootGo.transform.position.y)) ||
                (float.IsNaN(rootGo.transform.position.z) || float.IsInfinity(rootGo.transform.position.z)))
                throw new InvalidOperationException("GFXLAB_STOP: nonfinite model transform");

            var floor=GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            floor.name="StudioFloor";
            floor.transform.position=new Vector3(0,-.06f,0);
            floor.transform.localScale=new Vector3(1.35f,.04f,1.35f);
            floor.GetComponent<Renderer>().sharedMaterial=groundMat;
            var lightGo=new GameObject("DirectionalStudioLight");
            var light=lightGo.AddComponent<Light>();
            light.type=LightType.Directional;light.intensity=1.5f;
            lightGo.transform.rotation=Quaternion.Euler(46,-35,0);
            RenderSettings.ambientLight=new Color(.55f,.57f,.60f,1);
            RenderSettings.ambientMode=AmbientMode.Flat;
            var cameraGo=new GameObject("OrbitCamera");
            var camera=cameraGo.AddComponent<Camera>();
            camera.backgroundColor=new Color(.10f,.15f,.22f,1);
            camera.clearFlags=CameraClearFlags.SolidColor;
            camera.fieldOfView=45f;
            camera.nearClipPlane=.05f;
            camera.farClipPlane=150f;
            cameraGo.tag="MainCamera";
            var controller=cameraGo.AddComponent<GfxLabViewer>();
            controller.modelRoot=rootGo.transform;
            controller.sceneCamera=camera;
            controller.modelRenderers=renderers.ToArray();
            controller.whiteLit=whiteLit;
            controller.whiteUnlit=whiteUnlit;
            controller.meshCount=selectedMeshes;
            controller.vertexCount=actualVertices;
            controller.triangleCount=actualTriangles;
            controller.sourceCategory=evidence.model_category;

            var marker=GameObject.CreatePrimitive(PrimitiveType.Cube);
            marker.name="DimensionMarker_10cm";
            marker.transform.localScale=Vector3.one*.1f;
            marker.transform.position=new Vector3(-1.1f,.05f,-.5f);
            marker.GetComponent<Renderer>().sharedMaterial=groundMat;

            EditorSceneManager.MarkSceneDirty(scene);
            if (!EditorSceneManager.SaveScene(scene,"Assets/Scenes/GfxLab.unity"))
                throw new InvalidOperationException("GFXLAB_STOP: scene not saved");

            PlayerSettings.companyName="alwansan";
            PlayerSettings.productName="Raft Graphics Geometry Lab";
            PlayerSettings.bundleVersion="0.1.0";
            PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Android,
                "com.alwansan.raft.graphicslab");
            PlayerSettings.defaultInterfaceOrientation=UIOrientation.LandscapeLeft;
            PlayerSettings.colorSpace=ColorSpace.Linear;
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Android, ScriptingImplementation.IL2CPP);
            PlayerSettings.Android.targetArchitectures=AndroidArchitecture.ARM64;
            PlayerSettings.Android.minSdkVersion=AndroidSdkVersions.AndroidApiLevel26;
            PlayerSettings.Android.targetSdkVersion=AndroidSdkVersions.AndroidApiLevelAuto;
            PlayerSettings.SetGraphicsAPIs(BuildTarget.Android,
                new [] { GraphicsDeviceType.OpenGLES3 });
            EditorUserBuildSettings.buildAppBundle=false;
            PlayerSettings.Android.useAPKExpansionFiles=false;
            QualitySettings.shadowDistance=20f;
            AssetDatabase.SaveAssets();

            string target="builds/Android/GfxLab-Original-White.apk";
            Directory.CreateDirectory(Path.GetDirectoryName(target));
            var report=BuildPipeline.BuildPlayer(new[]
               {new EditorBuildSettingsScene("Assets/Scenes/GfxLab.unity",true)},
               target,BuildTarget.Android,BuildOptions.None);
            if (report.summary.result!=UnityEditor.Build.Reporting.BuildResult.Succeeded)
                throw new InvalidOperationException("GFXLAB_UNITY_BUILD_FAILED status="+report.summary.result);
            if (!File.Exists(target) || new FileInfo(target).Length<1024*1024)
                throw new InvalidOperationException("GFXLAB_STOP: APK missing or implausibly small");
            Debug.Log("GFXLAB_UNITY_BUILD_PASS geometry_verified=true unity_import=true"
                +" source_category="+evidence.model_category
                +" imported_meshes="+selectedMeshes+" imported_vertices="+actualVertices
                +" triangles="+actualTriangles
                +" output_bytes="+new FileInfo(target).Length
                +" device_pixels_verified=false");
        }
    }
}
