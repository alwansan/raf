// Exact original skybox material/shader import and Android Vulkan-only asset bundle.
// Editor-only; never BuildPlayer, never save or open the original scene.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using System.Security.Cryptography;
using System.Linq;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEditor;
using UObject = UnityEngine.Object;

public static class GTPrivateSkyboxImport {
    [Serializable] public class ColorSlot { public string name; public string[] bits; }
    [Serializable] public class FloatSlot { public string name,bits; }
    [Serializable] public class Expected {
        public string shaderGuid,shaderFileId,materialGuid,materialFileId,shaderName,candidateSha256;
        public ColorSlot[] colors; public FloatSlot[] floats;
    }
    [Serializable] public class Receipt {
        public string status="INCONCLUSIVE",version="unknown",errorCategory="none",candidateSha256="";
        public bool shaderIdentity,materialIdentity,materialShaderReference,shaderNameExact,
                    androidVulkanOnly,bundleBuilt,playerBuilt;
        public int sourcePropertyCount,colorSlots,colorMatches,floatSlots,floatMatches,intSlots,texEnvSlots,
                   passCount,shaderErrorsBefore,shaderErrorsAfter,privateBundleBytes;
    }
    static string Digest(string p) {
        using(var h=SHA256.Create()) return BitConverter.ToString(h.ComputeHash(File.ReadAllBytes(p))).Replace("-","").ToLowerInvariant();
    }
    static string Bits(float f) {
        return BitConverter.ToUInt32(BitConverter.GetBytes(f),0).ToString("x8",CultureInfo.InvariantCulture);
    }
    static bool Identity(UObject o,string guid,string id) {
        string actualGuid; long actualId;
        return o!=null && AssetDatabase.TryGetGUIDAndLocalFileIdentifier(o,out actualGuid,out actualId)
            && actualGuid==guid && actualId.ToString(CultureInfo.InvariantCulture)==id;
    }
    static SerializedProperty Array(SerializedObject s,string name) {
        var p=s.FindProperty("m_SavedProperties."+name);
        if(p==null || !p.isArray)throw new InvalidOperationException();
        return p;
    }
    static Dictionary<string,SerializedProperty> Slots(SerializedProperty p) {
        var result=new Dictionary<string,SerializedProperty>();
        for(int i=0;i<p.arraySize;i++) {
            var item=p.GetArrayElementAtIndex(i);
            var key=item.FindPropertyRelative("first");
            var value=item.FindPropertyRelative("second");
            if(key==null || value==null || string.IsNullOrEmpty(key.stringValue) ||
               result.ContainsKey(key.stringValue))throw new InvalidOperationException();
            result.Add(key.stringValue,value.Copy());
        }
        return result;
    }
    static int Errors(Shader shader) {
        return ShaderUtil.GetShaderMessages(shader).Count(m=>m.severity.ToString()=="Error");
    }
    public static void Run() {
        var r=new Receipt();
        string root=Path.GetFullPath(Path.Combine(Application.dataPath,".."));
        string shaderPath="Assets/Original.shader", materialPath="Assets/Original.mat";
        try {
            r.version=Application.unityVersion;
            var e=JsonUtility.FromJson<Expected>(File.ReadAllText(Path.Combine(root,"expected-private.json")));
            r.candidateSha256=Digest(Path.Combine(root,shaderPath));
            var shader=AssetDatabase.LoadAssetAtPath<Shader>(shaderPath);
            var material=AssetDatabase.LoadAssetAtPath<Material>(materialPath);
            r.shaderIdentity=Identity(shader,e.shaderGuid,e.shaderFileId);
            r.materialIdentity=Identity(material,e.materialGuid,e.materialFileId);
            r.materialShaderReference=material!=null && shader!=null && material.shader==shader;
            r.shaderNameExact=shader!=null && shader.name==e.shaderName;
            if(!r.shaderIdentity || !r.materialIdentity || !r.materialShaderReference || !r.shaderNameExact ||
               r.candidateSha256!=e.candidateSha256) {
                r.errorCategory="identity_or_saved_property_drift";
                r.status="FAIL";
            } else {
                r.sourcePropertyCount=ShaderUtil.GetPropertyCount(shader);
                r.passCount=material.passCount;
                var so=new SerializedObject(material); so.Update();
                var colors=Slots(Array(so,"m_Colors")); var floats=Slots(Array(so,"m_Floats"));
                r.colorSlots=colors.Count; r.floatSlots=floats.Count;
                r.intSlots=Array(so,"m_Ints").arraySize;
                r.texEnvSlots=Array(so,"m_TexEnvs").arraySize;
                foreach(var slot in e.colors) {
                    SerializedProperty p;
                    if(!colors.TryGetValue(slot.name,out p))continue;
                    Color c=p.colorValue;
                    if(new[]{Bits(c.r),Bits(c.g),Bits(c.b),Bits(c.a)}.SequenceEqual(slot.bits))r.colorMatches++;
                }
                foreach(var slot in e.floats) {
                    SerializedProperty p;
                    if(floats.TryGetValue(slot.name,out p) && Bits(p.floatValue)==slot.bits)r.floatMatches++;
                }
                r.shaderErrorsBefore=Errors(shader);
                if(r.sourcePropertyCount!=0 || r.passCount!=1 || r.colorSlots!=6 || r.colorMatches!=6 ||
                   r.floatSlots!=20 || r.floatMatches!=20 || r.intSlots!=0 || r.texEnvSlots!=0) {
                    r.errorCategory="identity_or_saved_property_drift"; r.status="FAIL";
                } else {
                    PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android,false);
                    PlayerSettings.SetGraphicsAPIs(BuildTarget.Android,new[]{GraphicsDeviceType.Vulkan});
                    r.androidVulkanOnly=EditorUserBuildSettings.activeBuildTarget==BuildTarget.Android &&
                        !PlayerSettings.GetUseDefaultGraphicsAPIs(BuildTarget.Android) &&
                        PlayerSettings.GetGraphicsAPIs(BuildTarget.Android).SequenceEqual(new[]{GraphicsDeviceType.Vulkan});
                    if(r.androidVulkanOnly && r.shaderErrorsBefore==0) {
                        string dir=Path.Combine(root,"private-bundle");
                        Directory.CreateDirectory(dir);
                        var map=new[]{new AssetBundleBuild{assetBundleName="skybox-private",
                                      assetNames=new[]{shaderPath,materialPath}}};
                        var manifest=BuildPipeline.BuildAssetBundles(dir,map,
                            BuildAssetBundleOptions.ForceRebuildAssetBundle|BuildAssetBundleOptions.StrictMode,
                            BuildTarget.Android);
                        string output=Path.Combine(dir,"skybox-private");
                        r.bundleBuilt=manifest!=null && File.Exists(output) &&
                           manifest.GetAllAssetBundles().SequenceEqual(new[]{"skybox-private"});
                        if(r.bundleBuilt)r.privateBundleBytes=checked((int)new FileInfo(output).Length);
                    }
                    r.shaderErrorsAfter=Errors(shader);
                    r.status=r.androidVulkanOnly && r.bundleBuilt && r.privateBundleBytes>0 &&
                        r.shaderErrorsBefore==0 && r.shaderErrorsAfter==0?"PASS":"FAIL";
                    if(r.status!="PASS")r.errorCategory="compiler_or_bundle_failed";
                }
            }
        } catch(Exception) { r.status="INCONCLUSIVE"; r.errorCategory="editor_exception"; }
        File.WriteAllText(Path.Combine(root,"editor-safe.json"),JsonUtility.ToJson(r,true));
        Debug.Log("GT_SKYBOX_EDITOR_STATUS="+r.status+" colorMatches="+r.colorMatches+" floatMatches="+r.floatMatches+
                  " compilerErrors="+r.shaderErrorsAfter+" bundleBuilt="+r.bundleBuilt);
        EditorApplication.Exit(r.status=="PASS"?0:2);
    }
}
