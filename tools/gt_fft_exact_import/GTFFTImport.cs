using System;
using System.IO;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

public static class GTFFTImport
{
    [Serializable] sealed class Expected {
        public string run_id,guid,wrong_guid,compute_sha,meta_sha,witness_sha;
        public long file_id;
    }
    [Serializable] sealed class Receipt {
        public string status="INCONCLUSIVE",run_id="",failure_step="";
        public bool vulkan,source_sha_matched,exact_guid_file_id,correct_reference_resolved,wrong_reference_null,wrong_guid_unresolved;
        public int kernel_registration_count,workgroup_count;
    }
    static void Need(bool b){if(!b)throw new InvalidOperationException();}
    static string Sha(string path){using(var h=SHA256.Create())using(var s=File.OpenRead(path))return BitConverter.ToString(h.ComputeHash(s)).Replace("-","").ToLowerInvariant();}
    static string Arg(string key){var a=Environment.GetCommandLineArgs();int i=Array.IndexOf(a,key);Need(i>=0&&i+1<a.Length);return a[i+1];}
    public static void Run(){
        string root=Directory.GetParent(Application.dataPath).FullName;
        var r=new Receipt();
        try{
            r.failure_step="expected";r.run_id=Arg("-gtFftRunId");
            var e=JsonUtility.FromJson<Expected>(File.ReadAllText(Path.Combine(root,"expected-private.json")));
            Need(Application.isBatchMode&&Application.unityVersion=="2021.3.45f2"&&e.run_id==r.run_id);
            r.failure_step="graphics";
            r.vulkan=SystemInfo.graphicsDeviceType==GraphicsDeviceType.Vulkan;Need(r.vulkan&&SystemInfo.supportsComputeShaders);
            r.failure_step="source";
            const string path="Assets/Original.compute";
            r.source_sha_matched=Sha(Path.Combine(root,path))==e.compute_sha;Need(r.source_sha_matched);
            AssetDatabase.ImportAsset(path,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
            AssetDatabase.ImportAsset("Assets/ReferenceWitness.asset",ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
            r.failure_step="identity";
            var shader=AssetDatabase.LoadAssetAtPath<ComputeShader>(path);
            Need(shader!=null);
            r.exact_guid_file_id=AssetDatabase.TryGetGUIDAndLocalFileIdentifier(shader,out string guid,out long id)&&guid==e.guid&&id==e.file_id&&AssetDatabase.GUIDToAssetPath(e.guid)==path;
            Need(r.exact_guid_file_id);
            r.failure_step="reference";
            var witness=AssetDatabase.LoadAssetAtPath<GTFFTReferenceWitness>("Assets/ReferenceWitness.asset");
            Need(witness!=null);
            r.correct_reference_resolved=witness.selected!=null&&witness.selected.Length==1&&witness.selected[0]==shader;
            r.wrong_reference_null=witness.absent!=null&&witness.absent.Length==1&&witness.absent[0]==null;
            r.wrong_guid_unresolved=String.IsNullOrEmpty(AssetDatabase.GUIDToAssetPath(e.wrong_guid));
            Need(r.correct_reference_resolved&&r.wrong_reference_null&&r.wrong_guid_unresolved);
            r.failure_step="registration";
            for(int i=0;i<20;i++){
                string n="RaftFftSlot"+i.ToString("00");
                Need(shader.HasKernel(n)&&shader.FindKernel(n)==i);r.kernel_registration_count++;
                shader.GetKernelThreadGroupSizes(i,out uint x,out uint y,out uint z);
                Need(x==(64u<<(i%10/2))&&y==1&&z==1);r.workgroup_count++;
            }
            r.failure_step="";r.status="PASS";
        }catch(Exception){ }
        File.WriteAllText(Path.Combine(root,"editor-receipt.json"),JsonUtility.ToJson(r));
        EditorApplication.Exit(r.status=="PASS"?0:2);
    }
}
