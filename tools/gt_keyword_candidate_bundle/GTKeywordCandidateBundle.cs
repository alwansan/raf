using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Rendering;
using UnityEngine;
using UnityEngine.Rendering;

namespace RaftGT {
    public sealed class GTKeywordCandidateCompilerObservation : IPreprocessShaders {
        public int callbackOrder { get { return Int32.MaxValue; } }
        public void OnProcessShader(Shader shader, ShaderSnippetData snippet, IList<ShaderCompilerData> data) {
            if (!GTKeywordCandidateBundle.Capturing || shader.name != GTKeywordCandidateBundle.Target) return;
            foreach (var d in data) {
                GTKeywordCandidateBundle.AddObservation(new GTKeywordCandidateBundle.Observation {
                    pass_name=snippet.passName, pass_type=snippet.passType.ToString(), stage=snippet.shaderType.ToString(),
                    platform=d.shaderCompilerPlatform.ToString(),
                    keywords=d.shaderKeywordSet.GetShaderKeywords().Select(k=>k.name).OrderBy(k=>k,StringComparer.Ordinal).ToArray()
                });
            }
        }
    }
    public static class GTKeywordCandidateBundle {
        public const string Target="GT/AuthoredKeywordCandidate";
        const string ShaderPath="Assets/GTKeywordCandidate.shader";
        const string BundleName="gt-keyword-candidate";
        public static bool Capturing;
        static readonly List<Observation> Observed=new List<Observation>();
        public static void AddObservation(Observation o) { lock(Observed) { Observed.Add(o); } }
        [Serializable] public sealed class Observation {public string pass_name,pass_type,stage,platform;public string[] keywords;}
        [Serializable] public sealed class Scope {public string name;public bool overridable;}
        [Serializable] public sealed class Variant {public string[] keywords;public string vs,fs;}
        [Serializable] public sealed class Pass {public int index;public string name,mode,passType;public Variant[] variants;}
        [Serializable] public sealed class ExpectedScope {public string name,scope;public int source_flag;}
        [Serializable] public sealed class Contract {public int schema;public string shader_name,candidate_sha256;public ExpectedScope[] scopes;public Pass[] passes;}
        [Serializable] public sealed class MaterialRoute {public string[] keywords;}
        [Serializable] public sealed class Result {
            public int schema=1,errors,pass_count;
            public string status="INCONCLUSIVE",run_id,unity_version,shader_name,candidate_sha256,contract_sha256,bundle_sha256,error="",checkpoint;
            public string editor_graphics_api,editor_graphics_device;
            public long bundle_bytes;
            public bool android_vulkan_only,original_assets_read,material_restored_empty;
            public Scope[] scopes;public Observation[] observations;public MaterialRoute[] material_routes;
        }
        static void Need(bool ok,string label){if(!ok)throw new InvalidOperationException(label);}
        static string Hash(byte[] b){using(var h=SHA256.Create())return String.Concat(h.ComputeHash(b).Select(x=>x.ToString("x2")));}
        static string Arg(string key){var a=Environment.GetCommandLineArgs();int i=Array.IndexOf(a,key);Need(i>=0&&i+1<a.Length,"run_id_missing");return a[i+1];}
        public static void Run(){
            var root=Directory.GetParent(Application.dataPath).FullName;
            var output=Path.Combine(root,"ProbeResults");
            Directory.CreateDirectory(output);
            var result=new Result{unity_version=Application.unityVersion,run_id=Arg("-gtCandidateRunId")};
            int exit=2;bool priorAsync=ShaderUtil.allowAsyncCompilation;
            try{
                result.checkpoint="input";
                ShaderUtil.allowAsyncCompilation=false;
                Need(result.unity_version=="2021.3.45f2","editor_version");
                result.editor_graphics_api=SystemInfo.graphicsDeviceType.ToString();
                result.editor_graphics_device=SystemInfo.graphicsDeviceName;
                // Commit the input even when the backend gate fails.
                byte[] candidate=File.ReadAllBytes(Path.Combine(root,ShaderPath));
                byte[] contract=File.ReadAllBytes(Path.Combine(root,"GTKeywordCandidateContract.json"));
                result.candidate_sha256=Hash(candidate);result.contract_sha256=Hash(contract);
                Need(SystemInfo.graphicsDeviceType==GraphicsDeviceType.Vulkan,"editor_Vulkan_required");
                var c=JsonUtility.FromJson<Contract>(System.Text.Encoding.UTF8.GetString(contract));
                Need(c.schema==1&&c.shader_name==Target&&c.candidate_sha256==result.candidate_sha256&&c.passes.Length==1&&c.scopes.Length==2,"authored_contract");
                PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android,false);
                PlayerSettings.SetGraphicsAPIs(BuildTarget.Android,new[]{GraphicsDeviceType.Vulkan});
                result.android_vulkan_only=PlayerSettings.GetGraphicsAPIs(BuildTarget.Android).SequenceEqual(new[]{GraphicsDeviceType.Vulkan});
                Need(result.android_vulkan_only,"Vulkan_target");
                result.checkpoint="import";
                AssetDatabase.ImportAsset(ShaderPath,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
                var shader=AssetDatabase.LoadAssetAtPath<Shader>(ShaderPath);
                Need(shader!=null&&shader.name==Target&&shader.passCount==c.passes.Length,"actual_shader_import");
                Need(shader.isSupported,"candidate_not_supported_by_editor_Vulkan");
                result.shader_name=shader.name;result.pass_count=shader.passCount;
                result.scopes=c.scopes.Select(e=>{
                    var k=shader.keywordSpace.keywords.Where(v=>v.name==e.name).ToArray();
                    Need(k.Length==1,"actual_keyword_scope_population");
                    return new Scope{name=e.name,overridable=k[0].isOverridable};
                }).ToArray();
                Need(result.scopes.All(s=>s.overridable==(c.scopes.Single(e=>e.name==s.name).scope=="global")),"actual_keyword_scope");
                result.checkpoint="register";
                var collection=new ShaderVariantCollection();
                foreach(var pass in c.passes){
                    PassType t;Need(Enum.TryParse(pass.passType,out t)&&t.ToString()==pass.passType,"pass_type");
                    foreach(var v in pass.variants)Need(collection.Add(new ShaderVariantCollection.ShaderVariant(shader,t,v.keywords)),"variant_registration");
                }
                Need(collection.variantCount==4,"variant_registration_count");
                const string variants="Assets/GTKeywordCandidate.shadervariants";
                AssetDatabase.CreateAsset(collection,variants);
                var material=new Material(shader);
                var observed=new List<MaterialRoute>();
                try{
                    foreach(var v in c.passes[0].variants){
                        foreach(var k in c.scopes)material.DisableKeyword(k.name);
                        foreach(var k in v.keywords)material.EnableKeyword(k);
                        var actual=material.shaderKeywords.OrderBy(k=>k,StringComparer.Ordinal).ToArray();
                        Need(actual.SequenceEqual(v.keywords.OrderBy(k=>k,StringComparer.Ordinal)),"material_keyword_API");
                        observed.Add(new MaterialRoute{keywords=actual});
                    }
                    foreach(var k in c.scopes)material.DisableKeyword(k.name);
                    result.material_restored_empty=material.shaderKeywords.Length==0;
                    Need(result.material_restored_empty,"material_keyword_restore");
                }finally{UnityEngine.Object.DestroyImmediate(material);}
                result.material_routes=observed.ToArray();
                AssetDatabase.SaveAssets();
                result.checkpoint="build";
                var directory=Path.Combine(output,"Private");Directory.CreateDirectory(directory);
                Capturing=true;lock(Observed){Observed.Clear();}
                AssetBundleManifest built;
                try{
                    built=BuildPipeline.BuildAssetBundles(directory,new[]{new AssetBundleBuild{
                        assetBundleName=BundleName,assetNames=new[]{ShaderPath,variants}
                    }},BuildAssetBundleOptions.StrictMode|BuildAssetBundleOptions.ForceRebuildAssetBundle,BuildTarget.Android);
                }finally{Capturing=false;}
                result.checkpoint="compiled";
                result.errors=ShaderUtil.GetShaderMessages(shader).Count(m=>m.severity.ToString()=="Error");
                var file=Path.Combine(directory,BundleName);
                Need(built!=null&&File.Exists(file)&&result.errors==0&&!ShaderUtil.ShaderHasError(shader),"Unity_bundle_or_compiler_error");
                byte[] bundle=File.ReadAllBytes(file);
                Need(bundle.Length>0&&bundle.Length<=8*1024*1024,"authored_bundle_size");
                result.bundle_bytes=bundle.Length;result.bundle_sha256=Hash(bundle);
                Need(Hash(File.ReadAllBytes(Path.Combine(root,ShaderPath)))==result.candidate_sha256&&Hash(File.ReadAllBytes(Path.Combine(root,"GTKeywordCandidateContract.json")))==result.contract_sha256,"Unity_input_drift");
                lock(Observed){result.observations=Observed.ToArray();}
                Need(result.observations.Length>0,"compiler_callbacks_missing");
                result.status="OBSERVED_CANDIDATE_ANDROID_VULKAN_BUNDLE";result.checkpoint="verified";exit=0;
            }catch(Exception e){result.error=e.GetType().Name+":"+e.Message;Debug.LogError("GT authored candidate "+result.error);}
            finally{
                Capturing=false;ShaderUtil.allowAsyncCompilation=priorAsync;
                lock(Observed){result.observations=Observed.ToArray();}
                File.WriteAllText(Path.Combine(output,"unity-raw.json"),JsonUtility.ToJson(result,true));
            }
            EditorApplication.Exit(exit);
        }
    }
}
