#if UNITY_EDITOR
using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Experimental.Rendering;
using UnityEngine.Rendering;

public static class SyntheticResourcePixelValidation
{
    const int W = 4, H = 4;
    const string ShaderPath = "Assets/SyntheticResourcePixels.shader";
    const string ProbePath = "Assets/Editor/SyntheticResourcePixelValidation.cs";
    static readonly Color Background = new Color(.125f,.25f,.5f,1);
    [Serializable] sealed class Pixel { public float[] rgba; }
    [Serializable] sealed class Row {
        public string name, texture, filter, wrap;
        public bool main_property_verified, decoy_property_verified;
        public Pixel[] samples;
    }
    [Serializable] sealed class Receipt {
        public int schema_version=1;
        public string run_id,status="FAIL",reason="not_started",Unity_version,backend,active_color_space,graphics_device_name,shader_sha256,probe_sha256;
        public bool synthetic_only=true,Unity_render_executed,Android_device,production_pixels,XAPK;
        public List<Row> cases=new List<Row>();
    }
    public static void Run() {
        var result=new Receipt {run_id=Option("-gtResourceRunId"),Unity_version=Application.unityVersion,
            backend=SystemInfo.graphicsDeviceType.ToString(),active_color_space=QualitySettings.activeColorSpace.ToString(),
            graphics_device_name=SystemInfo.graphicsDeviceName};
        var owned=new List<UnityEngine.Object>();
        var previous=RenderTexture.active;
        bool srgb=GL.sRGBWrite, async=ShaderUtil.allowAsyncCompilation;
        RenderTexture target=null; string output=Option("-gtResourceReport"); int exit=2;
        try {
            if(String.IsNullOrWhiteSpace(result.run_id)||String.IsNullOrWhiteSpace(output)||!Path.IsPathRooted(output)||File.Exists(output))
                throw new InvalidOperationException("fresh_absolute_report_and_run_id_required");
            string root=Directory.GetParent(Application.dataPath).FullName;
            if(Path.GetFullPath(output).StartsWith(Path.GetFullPath(root)+Path.DirectorySeparatorChar,StringComparison.Ordinal))
                throw new InvalidOperationException("report_must_be_outside_project");
            result.shader_sha256=Hash(Path.Combine(root,ShaderPath)); result.probe_sha256=Hash(Path.Combine(root,ProbePath));
            if(!Application.isBatchMode||Application.unityVersion!="2021.3.45f2"||SystemInfo.graphicsDeviceType!=GraphicsDeviceType.Vulkan||
                QualitySettings.activeColorSpace!=ColorSpace.Linear||GraphicsSettings.currentRenderPipeline!=null||
                !SystemInfo.SupportsTextureFormat(TextureFormat.RGBAFloat)||!SystemInfo.SupportsRenderTextureFormat(RenderTextureFormat.ARGBFloat))
                throw new InvalidOperationException("required_linear_vulkan_environment_missing");
            ShaderUtil.allowAsyncCompilation=false;
            AssetDatabase.ImportAsset(ShaderPath,ImportAssetOptions.ForceSynchronousImport);
            var shader=AssetDatabase.LoadAssetAtPath<Shader>(ShaderPath);
            if(shader==null||!shader.isSupported||ShaderUtil.ShaderHasError(shader)) throw new InvalidOperationException("shader_import_failed");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            target=Own(new RenderTexture(W,H,0,RenderTextureFormat.ARGBFloat,RenderTextureReadWrite.Linear),owned);
            target.antiAliasing=1;target.useMipMap=false;target.autoGenerateMips=false;target.filterMode=FilterMode.Point;
            if(!target.Create()||target.sRGB||target.graphicsFormat!=GraphicsFormat.R32G32B32A32_SFloat)
                throw new InvalidOperationException("exact_float_target_missing");
            var readback=Own(new Texture2D(W,H,TextureFormat.RGBAFloat,false,true),owned);
            var camera=Own(new GameObject("Authored camera"),owned).AddComponent<Camera>();
            camera.enabled=false;camera.transform.position=new Vector3(0,0,-2);camera.orthographic=true;
            camera.orthographicSize=1;camera.aspect=1;camera.nearClipPlane=.1f;camera.farClipPlane=10;
            camera.clearFlags=CameraClearFlags.Nothing;camera.renderingPath=RenderingPath.Forward;
            camera.allowMSAA=false;camera.allowHDR=true;camera.allowDynamicResolution=false;
            camera.useOcclusionCulling=false;camera.targetTexture=target;
            var quad=Own(new GameObject("Authored clip-space quad"),owned);var mesh=Own(new Mesh(),owned);
            mesh.vertices=new[]{new Vector3(-1,-1,0),new Vector3(1,-1,0),new Vector3(1,1,0),new Vector3(-1,1,0)};
            mesh.uv=new[]{new Vector2(0,0),new Vector2(1,0),new Vector2(1,1),new Vector2(0,1)};
            mesh.triangles=new[]{0,1,2,0,2,3};mesh.RecalculateBounds();
            quad.AddComponent<MeshFilter>().sharedMesh=mesh;var renderer=quad.AddComponent<MeshRenderer>();
            renderer.shadowCastingMode=ShadowCastingMode.Off;renderer.receiveShadows=false;
            var mat=Own(new Material(shader),owned);renderer.sharedMaterial=mat;
            if(!mat.HasProperty("_MainTex")||!mat.HasProperty("_OldTex")) throw new InvalidOperationException("material_property_missing");
            var a=new[]{new Color(.125f,.75f,.25f,0),new Color(.875f,.25f,.75f,1)};
            var b=new[]{new Color(.5f,.125f,1,.5f),new Color(.25f,.875f,.125f,1)};
            var decoy=Make(new[]{new Color(.75f,0,1,1),new Color(0,1,0,1)},FilterMode.Point,TextureWrapMode.Clamp,owned);
            var ap=Make(a,FilterMode.Point,TextureWrapMode.Clamp,owned);
            var al=Make(a,FilterMode.Bilinear,TextureWrapMode.Clamp,owned);
            var ar=Make(a,FilterMode.Bilinear,TextureWrapMode.Repeat,owned);
            var bp=Make(b,FilterMode.Point,TextureWrapMode.Clamp,owned);
            var bl=Make(b,FilterMode.Bilinear,TextureWrapMode.Clamp,owned);
            var white=Make(new[]{Color.white,Color.white},FilterMode.Point,TextureWrapMode.Clamp,owned);
            mat.SetTexture("_OldTex",decoy);
            string[] names={"A_point","A_linear","A_repeat","B_point","B_linear","A_point_after_B","white_substitute","decoy_as_main"};
            string[] labels={"A","A","A","B","B","A","white","decoy"};
            Texture2D[] textures={ap,al,ar,bp,bl,ap,white,decoy};
            for(int i=0;i<names.Length;i++) {
                var tex=textures[i];mat.SetTexture("_MainTex",tex);
                var row=new Row{name=names[i],texture=labels[i],filter=tex.filterMode.ToString(),wrap=tex.wrapMode.ToString(),
                    main_property_verified=mat.GetTexture("_MainTex")==tex,decoy_property_verified=mat.GetTexture("_OldTex")==decoy};
                if(!row.main_property_verified||!row.decoy_property_verified) throw new InvalidOperationException("material_api_binding_mismatch");
                RenderTexture.active=target;GL.sRGBWrite=false;GL.Clear(false,true,Background);camera.Render();
                RenderTexture.active=target;readback.ReadPixels(new Rect(0,0,W,H),0,0,false);
                var colors=readback.GetPixels();if(colors.Length!=W*H)throw new InvalidOperationException("readback_population");
                result.Unity_render_executed=true;row.samples=new Pixel[colors.Length];
                for(int k=0;k<colors.Length;k++) {
                    Color c=colors[k];row.samples[k]=new Pixel{rgba=new[]{c.r,c.g,c.b,c.a}};
                    foreach(float value in row.samples[k].rgba)if(Single.IsNaN(value)||Single.IsInfinity(value))throw new InvalidOperationException("nonfinite_pixel");
                }
                result.cases.Add(row);
            }
            if(ShaderUtil.ShaderHasError(shader))throw new InvalidOperationException("shader_error_after_render");
            result.status="READBACK_COMPLETE";result.reason="independent_numeric_gate_required";exit=0;
        } catch(Exception e){result.reason=e.GetType().Name+": "+e.Message;}
        finally {
            RenderTexture.active=previous;GL.sRGBWrite=srgb;ShaderUtil.allowAsyncCompilation=async;
            if(target!=null)target.Release();for(int i=owned.Count-1;i>=0;i--)if(owned[i]!=null)UnityEngine.Object.DestroyImmediate(owned[i]);
        }
        try {
            if(output==null||File.Exists(output))throw new IOException("fresh_report_required");
            File.WriteAllText(output,JsonUtility.ToJson(result,true)+"\n");
            Debug.Log("GT_RESOURCE_PIXEL_STATUS "+result.status+" cases="+result.cases.Count+" reason="+result.reason);
        } catch(Exception e){Debug.LogError(e.Message);exit=2;}
        EditorApplication.Exit(exit);
    }
    static Texture2D Make(Color[] colors,FilterMode filter,TextureWrapMode wrap,List<UnityEngine.Object> owned) {
        var tex=Own(new Texture2D(2,1,TextureFormat.RGBAFloat,false,true),owned);
        tex.filterMode=filter;tex.wrapMode=wrap;tex.anisoLevel=0;tex.SetPixels(colors);tex.Apply(false,false);return tex;
    }
    static T Own<T>(T value,List<UnityEngine.Object> owned) where T:UnityEngine.Object {owned.Add(value);return value;}
    static string Hash(string path){using(var h=SHA256.Create())using(var s=File.OpenRead(path))return BitConverter.ToString(h.ComputeHash(s)).Replace("-","").ToLowerInvariant();}
    static string Option(string arg){var a=Environment.GetCommandLineArgs();for(int i=0;i+1<a.Length;i++)if(a[i]==arg)return a[i+1];return null;}
}
#endif
