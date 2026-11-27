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

public static class SyntheticKeywordPixelValidation
{
    const string G = "GT_A2_GLOBAL", L = "GT_A2_LOCAL";
    const int W = 6, H = 4;
    const string ShaderPath = "Assets/SyntheticKeywordPixels.shader";
    const string ProbePath = "Assets/Editor/SyntheticKeywordPixelValidation.cs";
    [Serializable] sealed class Pixel { public float[] rgba; }
    [Serializable] sealed class Row {
        public string name;
        public int material, route;
        public bool global_enabled, local_A, local_B, global_local_impostor, material_global_A;
        public Pixel[] samples;
    }
    [Serializable] sealed class Receipt {
        public int schema_version = 1;
        public string run_id, status="FAIL", reason="not_started", Unity_version, backend, active_color_space,
            graphics_device_name, shader_sha256, probe_sha256;
        public bool synthetic_only=true, Unity_render_executed, Android_device, production_pixels, XAPK,
            global_overridable, local_overridable;
        public List<Row> cases = new List<Row>();
    }
    sealed class Step {
        public string name; public int mat, route;
        public bool g,a,b,i,mg;
        public Step(string name,int mat,bool g,bool a,bool b,bool i,bool mg,int route) {
            this.name=name; this.mat=mat; this.g=g; this.a=a; this.b=b; this.i=i; this.mg=mg; this.route=route;
        }
    }
    static readonly Step[] Steps = {
        new Step("empty_A",0,false,false,false,false,false,3),
        new Step("global_on_A",0,true,false,false,false,false,1),
        new Step("global_off_A",0,false,false,false,false,false,3),
        new Step("local_on_A",0,false,true,false,false,false,2),
        new Step("isolated_B",1,false,true,false,false,false,3),
        new Step("both_A",0,true,true,false,false,false,0),
        new Step("global_B",1,true,true,false,false,false,1),
        new Step("global_off_local_A",0,false,true,false,false,false,2),
        new Step("global_impostor_B",1,false,true,false,true,false,3),
        new Step("local_off_A",0,false,false,false,true,false,3),
        new Step("material_global_A",0,false,false,false,false,true,1),
        new Step("material_global_isolation_B",1,false,false,false,false,true,3),
        new Step("material_global_off_A",0,false,false,false,false,false,3),
        new Step("local_on_B",1,false,false,true,false,false,2),
        new Step("isolated_A",0,false,false,true,false,false,3)
    };
    public static void Run() {
        var result=new Receipt { run_id=Option("-gtKeywordRunId"),Unity_version=Application.unityVersion,
            backend=SystemInfo.graphicsDeviceType.ToString(),active_color_space=QualitySettings.activeColorSpace.ToString(),
            graphics_device_name=SystemInfo.graphicsDeviceName };
        var owned=new List<UnityEngine.Object>();
        var previous=RenderTexture.active;
        bool srgb=GL.sRGBWrite, async=ShaderUtil.allowAsyncCompilation;
        bool oldG=Shader.IsKeywordEnabled(G),oldL=Shader.IsKeywordEnabled(L);
        RenderTexture target=null;
        string output=Option("-gtKeywordReport"); int exit=2;
        try {
            if (String.IsNullOrWhiteSpace(result.run_id)||String.IsNullOrWhiteSpace(output)||!Path.IsPathRooted(output)||File.Exists(output))
                throw new InvalidOperationException("fresh_absolute_report_and_run_id_required");
            string root=Directory.GetParent(Application.dataPath).FullName;
            if (Path.GetFullPath(output).StartsWith(Path.GetFullPath(root)+Path.DirectorySeparatorChar,StringComparison.Ordinal))
                throw new InvalidOperationException("report_must_be_outside_project");
            result.shader_sha256=Hash(Path.Combine(root,ShaderPath)); result.probe_sha256=Hash(Path.Combine(root,ProbePath));
            if (!Application.isBatchMode||Application.unityVersion!="2021.3.45f2"||SystemInfo.graphicsDeviceType!=GraphicsDeviceType.Vulkan||
                QualitySettings.activeColorSpace!=ColorSpace.Linear||GraphicsSettings.currentRenderPipeline!=null||
                !SystemInfo.SupportsTextureFormat(TextureFormat.RGBAFloat)||!SystemInfo.SupportsRenderTextureFormat(RenderTextureFormat.ARGBFloat))
                throw new InvalidOperationException("required_batchmode_linear_Vulkan_environment_missing");
            ShaderUtil.allowAsyncCompilation=false;
            AssetDatabase.ImportAsset(ShaderPath,ImportAssetOptions.ForceSynchronousImport);
            var shader=AssetDatabase.LoadAssetAtPath<Shader>(ShaderPath);
            if(shader==null||!shader.isSupported||ShaderUtil.ShaderHasError(shader)) throw new InvalidOperationException("shader_import_failed");
            var gkw=shader.keywordSpace.FindKeyword(G); var lkw=shader.keywordSpace.FindKeyword(L);
            if(!gkw.isValid||!lkw.isValid) throw new InvalidOperationException("keyword_declaration_missing");
            result.global_overridable=gkw.isOverridable; result.local_overridable=lkw.isOverridable;
            if(!result.global_overridable||result.local_overridable) throw new InvalidOperationException("keyword_scope_wrong");
            EditorSceneManager.NewScene(NewSceneSetup.EmptyScene,NewSceneMode.Single);
            target=Own(new RenderTexture(W,H,0,RenderTextureFormat.ARGBFloat,RenderTextureReadWrite.Linear),owned);
            target.antiAliasing=1; target.useMipMap=false; target.autoGenerateMips=false; target.filterMode=FilterMode.Point;
            if(!target.Create()||target.sRGB||target.graphicsFormat!=GraphicsFormat.R32G32B32A32_SFloat)
                throw new InvalidOperationException("exact_float_target_missing");
            var readback=Own(new Texture2D(W,H,TextureFormat.RGBAFloat,false,true),owned);
            var camera=Own(new GameObject("Authored camera"),owned).AddComponent<Camera>();
            camera.enabled=false; camera.transform.position=new Vector3(0,0,-2); camera.orthographic=true;
            camera.orthographicSize=1; camera.aspect=(float)W/H; camera.nearClipPlane=.1f; camera.farClipPlane=10;
            camera.clearFlags=CameraClearFlags.Nothing; camera.renderingPath=RenderingPath.Forward;
            camera.allowMSAA=false; camera.allowHDR=true; camera.allowDynamicResolution=false;
            camera.useOcclusionCulling=false; camera.targetTexture=target;
            var quad=Own(new GameObject("Authored quad"),owned); var mesh=Own(new Mesh(),owned);
            mesh.vertices=new[]{new Vector3(-1.5f,-1,0),new Vector3(1.5f,-1,0),new Vector3(1.5f,1,0),new Vector3(-1.5f,1,0)};
            mesh.triangles=new[]{0,1,2,0,2,3}; mesh.RecalculateBounds();
            quad.AddComponent<MeshFilter>().sharedMesh=mesh; var renderer=quad.AddComponent<MeshRenderer>();
            renderer.shadowCastingMode=ShadowCastingMode.Off; renderer.receiveShadows=false;
            var mats=new[]{Own(new Material(shader),owned),Own(new Material(shader),owned)};
            mats[0].SetFloat("_ProbeMaterialMarker",.25f); mats[1].SetFloat("_ProbeMaterialMarker",.75f);
            foreach(var step in Steps) {
                SetGlobal(G,step.g); SetGlobal(L,step.i);
                SetMaterial(mats[0],L,step.a); SetMaterial(mats[1],L,step.b);
                SetMaterial(mats[0],G,step.mg); SetMaterial(mats[1],G,false);
                if(Shader.IsKeywordEnabled(G)!=step.g||Shader.IsKeywordEnabled(L)!=step.i||
                   mats[0].IsKeywordEnabled(L)!=step.a||mats[1].IsKeywordEnabled(L)!=step.b)
                    throw new InvalidOperationException("keyword_state_not_applied:"+step.name);
                renderer.sharedMaterial=mats[step.mat]; RenderTexture.active=target; GL.sRGBWrite=false;
                GL.Clear(false,true,new Color(.875f,.875f,.875f,0f)); camera.Render();
                RenderTexture.active=target; readback.ReadPixels(new Rect(0,0,W,H),0,0,false);
                var pixels=readback.GetPixels(); if(pixels.Length!=W*H) throw new InvalidOperationException("readback_population");
                result.Unity_render_executed=true;
                var row=new Row {name=step.name,material=step.mat,route=step.route,global_enabled=step.g,local_A=step.a,
                    local_B=step.b,global_local_impostor=step.i,material_global_A=step.mg,samples=new Pixel[pixels.Length]};
                bool pass=true; var expected=new Color((step.route+1)/8f,(step.route+1)/16f,step.mat==0?.25f:.75f,1);
                for(int j=0;j<pixels.Length;j++) {
                    var color=pixels[j]; row.samples[j]=new Pixel{rgba=new[]{color.r,color.g,color.b,color.a}};
                    for(int k=0;k<4;k++) if(Single.IsNaN(color[k])||Single.IsInfinity(color[k])||Mathf.Abs(color[k]-expected[k])>.002f) pass=false;
                }
                result.cases.Add(row);
                if(!pass) throw new InvalidOperationException("wrong_observed_route:"+step.name);
            }
            if(ShaderUtil.ShaderHasError(shader)) throw new InvalidOperationException("shader_error_after_render");
            result.status="PASS"; result.reason="all_authored_keyword_readbacks_matched"; exit=0;
        } catch(Exception e) {result.reason=e.GetType().Name+": "+e.Message;}
        finally {
            SetGlobal(G,oldG); SetGlobal(L,oldL); RenderTexture.active=previous; GL.sRGBWrite=srgb;
            ShaderUtil.allowAsyncCompilation=async; if(target!=null) target.Release();
            for(int i=owned.Count-1;i>=0;i--) if(owned[i]!=null) UnityEngine.Object.DestroyImmediate(owned[i]);
        }
        try { if(output==null||File.Exists(output)) throw new IOException("fresh_report_required");
            File.WriteAllText(output,JsonUtility.ToJson(result,true)+"\n");
            Debug.Log("GT_KEYWORD_PIXEL_STATUS "+result.status+" cases="+result.cases.Count+" reason="+result.reason);
        } catch(Exception e) {Debug.LogError(e.Message); exit=2;}
        EditorApplication.Exit(exit);
    }
    static void SetGlobal(string name,bool on) {if(on) Shader.EnableKeyword(name); else Shader.DisableKeyword(name);}
    static void SetMaterial(Material m,string name,bool on) {if(on) m.EnableKeyword(name); else m.DisableKeyword(name);}
    static T Own<T>(T value,List<UnityEngine.Object> owned) where T:UnityEngine.Object {owned.Add(value);return value;}
    static string Hash(string path) {using(var h=SHA256.Create()) using(var s=File.OpenRead(path)) return BitConverter.ToString(h.ComputeHash(s)).Replace("-","").ToLowerInvariant();}
    static string Option(string arg) {var a=Environment.GetCommandLineArgs();for(int i=0;i+1<a.Length;i++)if(a[i]==arg)return a[i+1];return null;}
}
#endif
