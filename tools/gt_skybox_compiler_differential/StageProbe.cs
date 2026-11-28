// Authored compiler probe only. No game resource, Play, or BuildPlayer.
using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;
public static class GTStageProbe {
    [Serializable] public class Case {
        public string id, exceptionCategory="none";
        public bool imported,bundleBuilt,sourceCopyExact;
        public int errorsBefore=-1,errorsAfter=-1,stageSelectorMessages,bindingConflictMessages,negativeSentinelMessages;
        public string bundleSha256="";
    }
    [Serializable] public class Receipt {
        public string version;
        public bool androidVulkanOnly,playerBuilt;
        public List<Case> cases=new List<Case>();
    }
    static readonly string[] IDs={"common","guard_common","split_registers","guard_different_registers","guard_entries","guard_entries_offset","negative_error"};
    static int Errors(Shader s) { return s==null?-1:ShaderUtil.GetShaderMessages(s).Count(m=>m.severity.ToString()=="Error"); }
    static string Digest(string path) {
        using(var sha=SHA256.Create()) return BitConverter.ToString(sha.ComputeHash(File.ReadAllBytes(path))).Replace("-","").ToLowerInvariant();
    }
    static void CaptureMessages(Shader shader, Case c) {
        if(shader==null)return;
        var errors=ShaderUtil.GetShaderMessages(shader).Where(m=>m.severity.ToString()=="Error").ToArray();
        c.stageSelectorMessages=errors.Count(m=>m.message.Contains("GT_PROBE_STAGE_SELECTION"));
        c.bindingConflictMessages=errors.Count(m=>m.message.Contains("explicit bindings for uniform"));
        c.negativeSentinelMessages=errors.Count(m=>m.message.Contains("GT_PROBE_NEGATIVE_SENTINEL"));
    }
    public static void Run() {
        string root=Path.GetFullPath(Path.Combine(Application.dataPath,".."));
        var r=new Receipt{version=Application.unityVersion};int exit=2;
        try {
            PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android,false);
            PlayerSettings.SetGraphicsAPIs(BuildTarget.Android,new[]{GraphicsDeviceType.Vulkan});
            r.androidVulkanOnly=EditorUserBuildSettings.activeBuildTarget==BuildTarget.Android &&
                !PlayerSettings.GetUseDefaultGraphicsAPIs(BuildTarget.Android) &&
                PlayerSettings.GetGraphicsAPIs(BuildTarget.Android).SequenceEqual(new[]{GraphicsDeviceType.Vulkan});
            if(!r.androidVulkanOnly)throw new InvalidOperationException();
            foreach(var id in IDs) {
                var c=new Case{id=id};r.cases.Add(c);
                string path="Assets/Probe_"+id+".shader";Shader shader=null;
                Debug.Log("GT_STAGE_PROBE_BEGIN "+id);
                try {
                    File.Copy(Path.Combine(root,"cases",id+".shader"),Path.Combine(root,path),false);
                    c.sourceCopyExact=Digest(Path.Combine(root,"cases",id+".shader"))==Digest(Path.Combine(root,path));
                    AssetDatabase.ImportAsset(path,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
                    shader=AssetDatabase.LoadAssetAtPath<Shader>(path);
                    c.imported=shader!=null && shader.name=="Hidden/GTStageProbe/"+id;
                    c.errorsBefore=Errors(shader);
                    if(c.imported && c.sourceCopyExact && c.errorsBefore==0) {
                        string dir=Path.Combine(root,"private-bundles",id);Directory.CreateDirectory(dir);
                        var map=new[]{new AssetBundleBuild{assetBundleName="probe",assetNames=new[]{path}}};
                        var m=BuildPipeline.BuildAssetBundles(dir,map,BuildAssetBundleOptions.ForceRebuildAssetBundle|BuildAssetBundleOptions.StrictMode,BuildTarget.Android);
                        c.bundleBuilt=m!=null && File.Exists(Path.Combine(dir,"probe")) && new FileInfo(Path.Combine(dir,"probe")).Length>0 && m.GetAllAssetBundles().SequenceEqual(new[]{"probe"});
                        if(c.bundleBuilt)c.bundleSha256=Digest(Path.Combine(dir,"probe"));
                    }
                } catch(Exception e) { c.exceptionCategory=e.GetType().Name; }
                finally {
                    c.errorsAfter=Errors(shader);
                    CaptureMessages(shader,c);
                    Debug.Log("GT_STAGE_PROBE_CASE_RECEIPT "+JsonUtility.ToJson(c));
                    AssetDatabase.DeleteAsset(path);
                    Debug.Log("GT_STAGE_PROBE_END "+id);
                }
            }
            exit=0;
        } catch(Exception) { exit=2; }
        File.WriteAllText(Path.Combine(root,"editor-safe.json"),JsonUtility.ToJson(r,true));
        Debug.Log("GT_STAGE_PROBE_EDITOR_RECEIPT_WRITTEN="+File.Exists(Path.Combine(root,"editor-safe.json")));
        EditorApplication.Exit(exit);
    }
}
