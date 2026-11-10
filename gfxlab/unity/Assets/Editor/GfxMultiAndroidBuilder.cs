using System;
using System.IO;
using System.Linq;
using System.Collections.Generic;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.SceneManagement;
using RaftGraphicsLab;

namespace RaftGraphicsLabEditor
{
    public static class GfxMultiAndroidBuilder
    {
        [Serializable] private sealed class TextureRole
        {
            public string role;
            public string file;
            public float[] scale;
            public float[] offset;
        }
        [Serializable] private sealed class Surface
        {
            public float[] tint;
            public bool original_shader_restored;
            public TextureRole[] textures;
        }
        [Serializable] private sealed class Config
        {
            public string id;
            public string category;
            public string geometry_type;
            public int source_bones;
            public int vertex_count;
            public int face_count;
            public bool original_shader_equivalence;
            public bool skin_animation_restored;
            public Surface[] materials;
        }

        private static Material NewMaterial(string name, Shader shader, Color color)
        {
            if(shader == null || !shader.isSupported)
                throw new InvalidOperationException("GFX_MULTI_UNSUPPORTED_SHADER");
            string assetPath="Assets/GfxMultiGenerated/"+name+".mat";
            Material material=AssetDatabase.LoadAssetAtPath<Material>(assetPath);
            if(material==null)
            {
                material=new Material(shader);
                material.name=name;
                AssetDatabase.CreateAsset(material,assetPath);
            }
            material.shader=shader;
            material.color=color;
            EditorUtility.SetDirty(material);
            return material;
        }
        private static Texture2D ImportOriginalTexture(string path,string role)
        {
            if(!File.Exists(path))throw new InvalidOperationException("GFX_MULTI_TEXTURE_MISSING");
            var imp=AssetImporter.GetAtPath(path) as TextureImporter;
            if(imp==null)throw new InvalidOperationException("GFX_MULTI_TEXTURE_IMPORTER_MISSING");
            imp.textureType=role=="normal" ? TextureImporterType.NormalMap : TextureImporterType.Default;
            imp.sRGBTexture=role=="basecolor";
            imp.mipmapEnabled=true;
            imp.maxTextureSize=4096;
            imp.SaveAndReimport();
            var t=AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if(t==null||t.width<1||t.height<1)
                throw new InvalidOperationException("GFX_MULTI_TEXTURE_DID_NOT_IMPORT");
            return t;
        }
        private static Texture2D ImportDiagnosticSourceChannel(string originalPath,string role,bool forceLinear)
        {
            // A separate copy retains the PNG RGBA decoder channels for GPU
            // inspection; the Standard PBR normal import is a distinct asset.
            // This source belongs only to the ephemeral Unity runner output.
            string suffix=forceLinear?"_channel_linear.png":"_channel_source.png";
            string path=Path.ChangeExtension(originalPath,null)+suffix;
            if(!File.Exists(originalPath))
                throw new InvalidOperationException("GFX_MULTI_CHANNEL_SOURCE_MISSING");
            if(!File.Exists(path))File.Copy(originalPath,path);
            AssetDatabase.ImportAsset(path,ImportAssetOptions.ForceSynchronousImport);
            var importer=AssetImporter.GetAtPath(path) as TextureImporter;
            if(importer==null)
                throw new InvalidOperationException("GFX_MULTI_CHANNEL_IMPORTER_MISSING");
            importer.textureType=TextureImporterType.Default;
            // Source serialized TextureColorSpace proven GFX024:
            // BaseColor=sRGB, Metallic=sRGB, Normal=Linear.
            // FORCE_LINEAR is a control, NOT an inferred fix to original Raft.
            importer.sRGBTexture=!forceLinear && role!="normal";
            importer.mipmapEnabled=true;
            importer.filterMode=FilterMode.Bilinear;
            importer.wrapMode=TextureWrapMode.Repeat;
            importer.anisoLevel=1;
            importer.maxTextureSize=4096;
            importer.SaveAndReimport();
            var t=AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if(t==null||t.width<1||t.height<1)
                throw new InvalidOperationException("GFX_MULTI_CHANNEL_TEXTURE_IMPORT_FAILED");
            return t;
        }
        private static void AssignDiagnosticRole(
            GfxMultiViewer.DiagnosticSlot slot,string role,
            Texture2D source,Texture2D linear)
        {
            if(slot==null||source==null||linear==null)
                throw new InvalidOperationException("GFX_MULTI_CHANNEL_SOURCE_INVALID");
            if(role=="basecolor"){slot.basecolorSource=source;slot.basecolorLinear=linear;}
            else if(role=="normal"){slot.normalSource=source;slot.normalLinear=linear;}
            else if(role=="metallic"){slot.metallicSource=source;slot.metallicLinear=linear;}
            else throw new InvalidOperationException("GFX_MULTI_CHANNEL_ROLE_INVALID");
        }
        private static void SetRole(Material material, string role, Texture2D t, TextureRole reference)
        {
            string property=role=="basecolor" ? "_MainTex" : role=="normal" ? "_BumpMap" :
                role=="metallic" ? "_MetallicGlossMap" : null;
            if(property==null)throw new InvalidOperationException("GFX_MULTI_INVALID_TEXTURE_ROLE");
            material.SetTexture(property,t);
            if(reference.scale!=null && reference.offset!=null)
            {
                if(reference.scale.Length!=2||reference.offset.Length!=2)
                    throw new InvalidOperationException("GFX_MULTI_UV_TRANSFORM_MALFORMED");
                material.SetTextureScale(property,new Vector2(reference.scale[0],reference.scale[1]));
                material.SetTextureOffset(property,new Vector2(reference.offset[0],reference.offset[1]));
            }
            if(role=="normal")material.EnableKeyword("_NORMALMAP");
            if(role=="metallic")material.EnableKeyword("_METALLICGLOSSMAP");
        }
        private static Color SourceTint(Surface s)
        {
            if(s.tint==null)return Color.white; // no authoring tint, preserve source texture directly
            if(s.tint.Length!=4 || s.tint.Any(x=>float.IsNaN(x)||float.IsInfinity(x)))
                throw new InvalidOperationException("GFX_MULTI_INVALID_ORIGINAL_TINT");
            return new Color(s.tint[0],s.tint[1],s.tint[2],s.tint[3]);
        }
        private static GameObject OriginalInstance(string folder,string id)
        {
            string obj=folder+"/model.obj";
            var prefab=AssetDatabase.LoadAssetAtPath<GameObject>(obj);
            if(prefab==null)throw new InvalidOperationException("GFX_MULTI_OBJ_IMPORT_FAILED_"+id);
            GameObject instance=UnityEngine.Object.Instantiate(prefab);
            instance.name="SourceVerified_"+id;
            return instance;
        }
        private static int MeshVertexCount(GameObject root,out int faces)
        {
            int vertices=0;faces=0;
            foreach(var filter in root.GetComponentsInChildren<MeshFilter>(true))
            {
                var mesh=filter.sharedMesh;
                if(mesh==null)continue;
                vertices+=mesh.vertexCount;
                for(int i=0;i<mesh.subMeshCount;i++)
                    faces+=mesh.GetTriangles(i).Length/3;
            }
            return vertices;
        }
        // Use actual source mesh vertices: Renderer.bounds can be empty in
        // batchmode before a freshly constructed fallback MeshRenderer renders.
        // No geometry is substituted or invented. Only viewer transform changes.
        private static void NormalizePosition(GameObject root,Renderer[] renderers,string id)
        {
            if(renderers==null||renderers.Length==0)
                throw new InvalidOperationException("GFX_MULTI_RENDERER_EMPTY_"+id);
            double minX=double.PositiveInfinity,minY=double.PositiveInfinity,minZ=double.PositiveInfinity;
            double maxX=double.NegativeInfinity,maxY=double.NegativeInfinity,maxZ=double.NegativeInfinity;
            int n=0;
            foreach(var f in root.GetComponentsInChildren<MeshFilter>(true))
            {
                if(f.sharedMesh==null)continue;
                foreach(Vector3 v in f.sharedMesh.vertices)
                {
                    Vector3 p=f.transform.TransformPoint(v);
                    if(float.IsNaN(p.x)||float.IsNaN(p.y)||float.IsNaN(p.z)||
                       float.IsInfinity(p.x)||float.IsInfinity(p.y)||float.IsInfinity(p.z))
                        throw new InvalidOperationException("GFX_MULTI_NONFINITE_SOURCE_VERTEX_"+id);
                    minX=Math.Min(minX,p.x);maxX=Math.Max(maxX,p.x);
                    minY=Math.Min(minY,p.y);maxY=Math.Max(maxY,p.y);
                    minZ=Math.Min(minZ,p.z);maxZ=Math.Max(maxZ,p.z);
                    n++;
                }
            }
            if(n==0)throw new InvalidOperationException("GFX_MULTI_NO_SOURCE_VERTICES_"+id);
            double extent=Math.Max(maxX-minX,Math.Max(maxY-minY,maxZ-minZ));
            if(double.IsNaN(extent)||double.IsInfinity(extent)||extent<=1e-12)
                throw new InvalidOperationException("GFX_MULTI_DEGENERATE_SOURCE_VERTEX_BOUNDS_"+id);
            double scale=1.8d/extent;
            if(double.IsInfinity(scale)||double.IsNaN(scale)||scale<1e-10||scale>1e10)
                throw new InvalidOperationException("GFX_MULTI_UNREPRESENTABLE_VIEW_SCALE_"+id);
            double cx=minX+(maxX-minX)*0.5d,cy=minY+(maxY-minY)*0.5d,cz=minZ+(maxZ-minZ)*0.5d;
            double px=-cx*scale,py=1d-cy*scale,pz=-cz*scale;
            if(double.IsNaN(px)||double.IsNaN(py)||double.IsNaN(pz)||
               Math.Abs(px)>1e30||Math.Abs(py)>1e30||Math.Abs(pz)>1e30)
                throw new InvalidOperationException("GFX_MULTI_UNREPRESENTABLE_VIEW_CENTER_"+id);
            root.transform.localScale=Vector3.one*(float)scale;
            root.transform.position=new Vector3((float)px,(float)py,(float)pz);
            Debug.Log("GFX_MULTI_GEOMETRY_BOUNDS_FINITE model="+id+
                " vertices="+n+" source_geometry_preserved=true viewport_normalized=true");
        }
        private static GfxMultiViewer.Model BuildModel(int index)
        {
            string id="M"+index.ToString("00");
            string folder="Assets/MultiModels/"+id;
            string configPath=folder+"/config.json";
            if(!File.Exists(configPath))throw new InvalidOperationException("GFX_MULTI_CONFIG_MISSING_"+id);
            Config config=JsonUtility.FromJson<Config>(File.ReadAllText(configPath));
            if(config==null||config.id!=id||config.vertex_count<128||config.face_count<1
               ||config.materials==null||config.materials.Length<1||config.materials.Length>4
               ||config.original_shader_equivalence||config.skin_animation_restored)
                throw new InvalidOperationException("GFX_MULTI_INVALID_ORIGINAL_MANIFEST_"+id);
            var root=OriginalInstance(folder,id);
            int importedFaces=0;
            int importedVertices=MeshVertexCount(root,out importedFaces);
            int importedMaterialSlots=0;
            foreach(var flt in root.GetComponentsInChildren<MeshFilter>(true))
                if(flt.sharedMesh!=null)importedMaterialSlots+=Math.Max(1,flt.sharedMesh.subMeshCount);
            if(importedVertices<=0||importedFaces!=config.face_count ||
               importedMaterialSlots!=config.materials.Length)
            {
                // Unity 2021's OBJ ModelImporter emitted zero mesh for some original
                // static meshes (CI42712833407 M02). Use the same source v/vt/vn/f
                // to build an actual typed UnityEngine.Mesh without replacing art.
                Debug.LogWarning("GFX_MULTI_IMPORTER_FALLBACK model="+id+
                    " obj_imported_vertices="+importedVertices+
                    " obj_imported_submesh_slots="+importedMaterialSlots);
                UnityEngine.Object.DestroyImmediate(root);
                root=GfxOriginalObjImporter.Load(folder+"/model.obj",id);
                importedVertices=MeshVertexCount(root,out importedFaces);
                if(importedVertices<=0||importedFaces!=config.face_count)
                    throw new InvalidOperationException("GFX_MULTI_SOURCE_TRIANGLE_PARITY_FAIL_"+id);
            }
            Renderer[] renderers=root.GetComponentsInChildren<Renderer>(true);
            if(renderers.Length==0)
                throw new InvalidOperationException("GFX_MULTI_RENDERER_IMPORT_ZERO_"+id);
            var standard=Shader.Find("Standard");
            var unlit=Shader.Find("Unlit/Color");
            var originals=new Material[config.materials.Length];
            var pbr=new Material[config.materials.Length];
            var whiteLit=new Material[config.materials.Length];
            var whiteUnlit=new Material[config.materials.Length];
            var diagnostics=new GfxMultiViewer.DiagnosticSlot[config.materials.Length];
            int textures=0;
            for(int slot=0;slot<config.materials.Length;slot++)
            {
                Surface source=config.materials[slot];
                if(source==null||source.original_shader_restored||source.textures==null)
                    throw new InvalidOperationException("GFX_MULTI_FALSE_ORIGINAL_SHADER_CLAIM_"+id);
                whiteLit[slot]=NewMaterial(id+"_S"+slot+"_WhiteLit",standard,Color.white);
                whiteUnlit[slot]=NewMaterial(id+"_S"+slot+"_WhiteUnlit",unlit,Color.white);
                originals[slot]=NewMaterial(id+"_S"+slot+"_Albedo",standard,SourceTint(source));
                pbr[slot]=NewMaterial(id+"_S"+slot+"_PBRApprox",standard,SourceTint(source));
                bool baseColorPresent=false;
                diagnostics[slot]=new GfxMultiViewer.DiagnosticSlot();
                foreach(TextureRole r in source.textures)
                {
                    if(r==null||r.file==null||r.file.IndexOf("..",StringComparison.Ordinal)>=0
                       ||r.file.Contains("/")||r.file.Contains("\\"))
                        throw new InvalidOperationException("GFX_MULTI_SOURCE_TEXTURE_PATH_INVALID");
                    string texturePath=folder+"/"+r.file;
                    Texture2D tex=ImportOriginalTexture(texturePath,r.role);
                    Texture2D probeSource=ImportDiagnosticSourceChannel(texturePath,r.role,false);
                    Texture2D probeLinear=ImportDiagnosticSourceChannel(texturePath,r.role,true);
                    AssignDiagnosticRole(diagnostics[slot],r.role,probeSource,probeLinear);
                    textures++;
                    if(r.role=="basecolor")
                    {
                        SetRole(originals[slot],r.role,tex,r);
                        SetRole(pbr[slot],r.role,tex,r);
                        baseColorPresent=true;
                    }
                    else SetRole(pbr[slot],r.role,tex,r);
                }
                if(!baseColorPresent)throw new InvalidOperationException("GFX_MULTI_ORIGINAL_ALBEDO_ABSENT_"+id);
                pbr[slot].SetFloat("_Glossiness",.45f);
                EditorUtility.SetDirty(originals[slot]);
                EditorUtility.SetDirty(pbr[slot]);
            }
            // Preserve original Material slot topology; never silently paint a missing submesh.
            int totalUnitySlots=0;
            var rendererSlots=new List<GfxMultiViewer.MaterialSlot>();
            foreach(var renderer in renderers)
            {
                var filter=renderer.GetComponent<MeshFilter>();
                if(filter==null||filter.sharedMesh==null)
                    throw new InvalidOperationException("GFX_MULTI_ONLY_STATIC_OBJ_IMPORT_SUPPORTED_"+id);
                int count=Math.Max(1,filter.sharedMesh.subMeshCount);
                totalUnitySlots+=count;
                Material[] mode0=new Material[count];
                Material[] mode1=new Material[count];
                Material[] mode2=new Material[count];
                Material[] mode3=new Material[count];
                for(int i=0;i<count;i++)
                {
                    // For one renderer with N submeshes use N source materials. For
                    // separate renderers, enumerate submesh slots sequentially.
                    int slot=(totalUnitySlots-count)+i;
                    if(slot>=config.materials.Length)
                        throw new InvalidOperationException("GFX_MULTI_IMPORTED_EXTRA_SUBMESH_"+id);
                    mode0[i]=whiteLit[slot];mode1[i]=whiteUnlit[slot];
                    mode2[i]=originals[slot];mode3[i]=pbr[slot];
                }
                renderer.sharedMaterials=mode3;
                rendererSlots.Add(new GfxMultiViewer.MaterialSlot {
                    renderer=renderer,whiteLit=mode0,whiteUnlit=mode1,
                    sourceAlbedo=mode2,sourcePbr=mode3
                });
            }
            if(totalUnitySlots!=config.materials.Length)
                throw new InvalidOperationException("GFX_MULTI_SOURCE_MATERIAL_SUBMESH_MISMATCH_"+id+
                    "_source="+config.materials.Length+"_unity="+totalUnitySlots);
            NormalizePosition(root,renderers,id);
            root.SetActive(false);
            Debug.Log("GFX_MULTI_UNITY_ORIGINAL_MODEL_IMPORTED model="+id+
                " geometry_imported=true original_textures="+textures+
                " original_material_slots="+totalUnitySlots+" original_shader_exact=false");
            return new GfxMultiViewer.Model {
                id=id,category=config.category,geometryKind=config.geometry_type,
                sourceBones=config.source_bones,
                vertices=importedVertices,triangles=importedFaces,
                sourceMaterials=config.materials.Length,sourceTextures=textures,
                sourceVerified=true,exactShaderRestored=false,originalAnimationRestored=false,
                root=root,slots=rendererSlots.ToArray(),diagnosticSlots=diagnostics
            };
        }

        public static void PrepareModelScene()
        {
            if(!Directory.Exists("Assets/MultiModels"))
                throw new InvalidOperationException("GFX_MULTI_MISSING_ALL_ORIGINAL_MODEL_DATA");
            Directory.CreateDirectory("Assets/GfxMultiGenerated");
            Directory.CreateDirectory("Assets/Scenes");
            AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
            var scene=EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            GfxMultiViewer.Model[] models=new GfxMultiViewer.Model[6];
            for(int i=0;i<6;i++)models[i]=BuildModel(i);
            models[0].root.SetActive(true);

            var lightGo=new GameObject("StudioDirectionalLight");
            var light=lightGo.AddComponent<Light>();
            light.type=LightType.Directional;
            light.intensity=1.5f;
            light.shadows=LightShadows.Soft;
            lightGo.transform.rotation=Quaternion.Euler(47f,-38f,0);
            RenderSettings.ambientMode=AmbientMode.Flat;
            RenderSettings.ambientLight=new Color(.56f,.58f,.61f,1f);
            var cameraGo=new GameObject("MultiModelOrbitCamera");
            Camera camera=cameraGo.AddComponent<Camera>();
            camera.backgroundColor=new Color(.09f,.15f,.23f,1);
            camera.clearFlags=CameraClearFlags.SolidColor;
            camera.fieldOfView=45f;
            camera.nearClipPlane=.03f;
            camera.farClipPlane=100f;
            cameraGo.tag="MainCamera";
            var automaticRecorder=cameraGo.AddComponent<GfxSessionRecorder>();
            var viewer=cameraGo.AddComponent<GfxMultiViewer>();
            viewer.sessionRecorder=automaticRecorder;
            viewer.viewingCamera=camera;
            viewer.models=models;
            viewer.defaultHideHelpers=true;
            // This shader only visualizes the source RGBA samples, and is never
            // the seven-pass original Shader48.
            Shader inspector=Shader.Find("Hidden/GfxLab/ChannelProbe");
            if(inspector==null||!inspector.isSupported)
                throw new InvalidOperationException("GFX_MULTI_CHANNEL_INSPECTOR_SHADER_UNAVAILABLE");
            var diagnosticMaterial=new Material(inspector);
            diagnosticMaterial.name="GfxLabChannelDiagnosticNotOriginalShader";
            AssetDatabase.CreateAsset(diagnosticMaterial,
                "Assets/GfxMultiGenerated/ChannelDiagnosticOnly.mat");
            viewer.diagnosticChannelMaterial=diagnosticMaterial;

            // Only for optional studio helpers; no synthetic helper is a source model.
            var floor=GameObject.CreatePrimitive(PrimitiveType.Cylinder);
            floor.name="OptionalStudioFloor_NotOriginalModel";
            floor.transform.position=new Vector3(0,-.055f,0);
            floor.transform.localScale=new Vector3(1.1f,.03f,1.1f);
            floor.GetComponent<Renderer>().sharedMaterial=
                NewMaterial("OptionalGround",Shader.Find("Standard"),new Color(.22f,.24f,.27f,1));
            floor.SetActive(false);
            viewer.studioFloor=floor;
            EditorSceneManager.MarkSceneDirty(scene);
            if(!EditorSceneManager.SaveScene(scene,"Assets/Scenes/GfxMulti.unity"))
                throw new InvalidOperationException("GFX_MULTI_SCENE_NOT_SAVED");

        }

        public static void Build()
        {
            PrepareModelScene();
            PlayerSettings.companyName="alwansan";
            PlayerSettings.productName="Raft GFX Multi Model Laboratory";
            PlayerSettings.bundleVersion="0.5.0";
            PlayerSettings.Android.bundleVersionCode=5;
            PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Android,
                "com.alwansan.raft.graphicslab.autologs");
            PlayerSettings.defaultInterfaceOrientation=UIOrientation.LandscapeLeft;
            PlayerSettings.colorSpace=ColorSpace.Linear;
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Android,ScriptingImplementation.IL2CPP);
            PlayerSettings.Android.targetArchitectures=AndroidArchitecture.ARM64;
            PlayerSettings.Android.minSdkVersion=AndroidSdkVersions.AndroidApiLevel26;
            PlayerSettings.Android.targetSdkVersion=AndroidSdkVersions.AndroidApiLevelAuto;
            PlayerSettings.SetGraphicsAPIs(BuildTarget.Android,new []{GraphicsDeviceType.OpenGLES3});
            PlayerSettings.Android.useAPKExpansionFiles=false;
            EditorUserBuildSettings.buildAppBundle=false;
            QualitySettings.shadowDistance=20f;
            AssetDatabase.SaveAssets();

            string apk="builds/Android/GfxLab-Multi-Six-AutoLogs.apk";
            Directory.CreateDirectory(Path.GetDirectoryName(apk));
            var report=BuildPipeline.BuildPlayer(
                new[]{new EditorBuildSettingsScene("Assets/Scenes/GfxMulti.unity",true)},
                apk,BuildTarget.Android,BuildOptions.None);
            if(report.summary.result!=UnityEditor.Build.Reporting.BuildResult.Succeeded ||
                !File.Exists(apk) || new FileInfo(apk).Length<1024*1024)
                throw new InvalidOperationException("GFX_MULTI_UNITY_ANDROID_BUILD_NOT_PROVEN");
            Debug.Log("GFX_MULTI_UNITY_REAL_BUILD_PASS models=6 channel_probe=true original_shader_exact=false"+
                " source_materials=7 original_animation=false owner_device_pixels=false");
        }
    }
}
