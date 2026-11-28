using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Reflection;
using System.Security.Cryptography;
using System.Text;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

public static class GTFFTOriginalConstructor
{
    [Serializable] sealed class Case {
        public int resolution,seed,first,first_workgroup,second_workgroup;
        public bool third,fourth,two_channels,high_precision,shader_field_matched;
        public string format;
    }
    [Serializable] sealed class Expected {
        public string run_id,type_name,base_name,selector_hash,seed_hash,two_hash,high_hash,assembly_sha,compute_sha,meta_sha;
        public Case[] cases;
    }
    [Serializable] sealed class Receipt {
        public string status="INCONCLUSIVE",run_id="",failure_step="",exception_category="",inner_category="";
        public bool vulkan,original_assembly_loaded,constructor_il_nonempty,same_export_reference_resolved,assembly_name_collision;
        public int started_cases;
        public List<Case> cases=new List<Case>();
    }
    const BindingFlags Declared=BindingFlags.DeclaredOnly|BindingFlags.Instance|BindingFlags.Public|BindingFlags.NonPublic;
    static void Need(bool b){if(!b)throw new InvalidOperationException();}
    static string Hash(byte[] bytes){using(var h=SHA256.Create())return BitConverter.ToString(h.ComputeHash(bytes)).Replace("-","").ToLowerInvariant();}
    static string Sha(string s){return Hash(Encoding.UTF8.GetBytes(s));}
    static FieldInfo Field(Type t,string hash,Type kind) {
        var matches=new List<FieldInfo>();
        for(Type p=t;p!=null&&p!=typeof(object);p=p.BaseType)
            matches.AddRange(p.GetFields(Declared).Where(f=>f.FieldType==kind&&Sha(f.Name)==hash));
        Need(matches.Count==1);return matches[0];
    }
    static List<FieldInfo> ComputeFields(Type t){
        var fields=new List<FieldInfo>();
        for(Type p=t;p!=null&&p!=typeof(object);p=p.BaseType)
            fields.AddRange(p.GetFields(Declared).Where(f=>f.FieldType==typeof(ComputeShader)));
        return fields;
    }
    static string Category(Exception e) {
        if(e==null)return "";
        string n=e.GetType().Name;
        return new[]{"ArgumentException","TargetInvocationException","FileNotFoundException","FileLoadException","TypeLoadException","ReflectionTypeLoadException","MissingMethodException","MissingFieldException","InvalidOperationException","NullReferenceException","BadImageFormatException","NotSupportedException","UnityException","TargetException","TypeInitializationException"}.Contains(n)?n:"Other";
    }
    static string Arg(string name){var a=Environment.GetCommandLineArgs();int i=Array.IndexOf(a,name);Need(i>=0&&i+1<a.Length);return a[i+1];}
    static void Save(string root,Receipt r){File.WriteAllText(Path.Combine(root,"constructor-receipt.json"),JsonUtility.ToJson(r));}
    public static void Run(){
        string root=Directory.GetParent(Application.dataPath).FullName;
        var r=new Receipt();
        try {
            r.failure_step="expected";r.run_id=Arg("-gtFftRunId");
            var e=JsonUtility.FromJson<Expected>(File.ReadAllText(Path.Combine(root,"original-constructor-private.json")));
            Need(Application.isBatchMode&&Application.unityVersion=="2021.3.45f2"&&e.run_id==r.run_id&&e.cases.Length==20);
            r.failure_step="graphics";r.vulkan=SystemInfo.graphicsDeviceType==GraphicsDeviceType.Vulkan;
            Need(r.vulkan&&SystemInfo.supportsComputeShaders);
            r.failure_step="import";
            const string path="Assets/Original.compute";
            Need(Hash(File.ReadAllBytes(Path.Combine(root,path)))==e.compute_sha&&Hash(File.ReadAllBytes(Path.Combine(root,path+".meta")))==e.meta_sha);
            AssetDatabase.ImportAsset(path,ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
            AssetDatabase.ImportAsset("Assets/ReferenceWitness.asset",ImportAssetOptions.ForceSynchronousImport|ImportAssetOptions.ForceUpdate);
            var shader=AssetDatabase.LoadAssetAtPath<ComputeShader>(path);
            var witness=AssetDatabase.LoadAssetAtPath<GTFFTReferenceWitness>("Assets/ReferenceWitness.asset");
            r.same_export_reference_resolved=shader!=null&&witness!=null&&witness.selected!=null&&witness.selected.Length==1&&witness.selected[0]==shader&&witness.absent!=null&&witness.absent.Length==1&&witness.absent[0]==null;
            Need(r.same_export_reference_resolved);
            r.failure_step="original_assembly";
            var bytes=File.ReadAllBytes(Path.Combine(root,"original-managed-private.dll"));
            Need(Hash(bytes)==e.assembly_sha);
            r.assembly_name_collision=AppDomain.CurrentDomain.GetAssemblies().Any(a=>a.GetName().Name=="Assembly-CSharp");
            Need(!r.assembly_name_collision);
            Save(root,r);
            var asm=Assembly.Load(bytes);
            Need(asm.GetName().Name=="Assembly-CSharp");
            r.original_assembly_loaded=true;
            r.failure_step="original_type";
            var t=asm.GetType(e.type_name,true,false);
            Need(t.Assembly==asm&&t.BaseType!=null&&t.BaseType.Assembly==asm&&t.BaseType.FullName==e.base_name&&!typeof(UnityEngine.Object).IsAssignableFrom(t));
            r.failure_step="constructor_signature";
            var ctor=t.GetConstructor(Declared,null,new[]{typeof(ComputeShader),typeof(int),typeof(bool),typeof(bool)},null);
            Need(ctor!=null&&ctor.DeclaringType==t);
            var il=ctor.GetMethodBody();r.constructor_il_nonempty=il!=null&&il.GetILAsByteArray().Length>0;
            Need(r.constructor_il_nonempty);
            r.failure_step="field_identity";
            var first=Field(t,e.selector_hash,typeof(int));var seed=Field(t,e.seed_hash,typeof(int));
            var two=Field(t,e.two_hash,typeof(bool));var high=Field(t,e.high_hash,typeof(bool));
            var shaders=ComputeFields(t);Need(shaders.Count>0);
            foreach(var c in e.cases){
                r.failure_step="original_constructor";r.started_cases++;Save(root,r);
                // Only the exact original constructor, with bounded synthetic inputs.
                object o=ctor.Invoke(new object[]{shader,c.resolution,c.third,c.fourth});
                Need(o!=null&&o.GetType()==t);
                r.failure_step="original_fields";
                var v=new Case{resolution=c.resolution,third=c.third,fourth=c.fourth,
                    first=(int)first.GetValue(o),seed=(int)seed.GetValue(o),
                    two_channels=(bool)two.GetValue(o),high_precision=(bool)high.GetValue(o),
                    shader_field_matched=shaders.Count(f=>(ComputeShader)f.GetValue(o)==shader)==1};
                v.format=(v.two_channels?"ARGB":"RG")+(v.high_precision?"Float":"Half");
                Need(v.first==c.first&&v.seed==c.seed&&v.two_channels==c.two_channels&&v.high_precision==c.high_precision&&v.format==c.format&&v.shader_field_matched);
                r.failure_step="registered_original_index";
                Need(v.first>=0&&v.first+1<20);
                shader.GetKernelThreadGroupSizes(v.first,out uint x,out uint y,out uint z);
                Need(x==2u*(uint)v.resolution&&y==1&&z==1);v.first_workgroup=(int)x;
                shader.GetKernelThreadGroupSizes(v.first+1,out x,out y,out z);
                Need(x==2u*(uint)v.resolution&&y==1&&z==1);v.second_workgroup=(int)x;
                r.cases.Add(v);Save(root,r);
            }
            r.failure_step="";r.status="PASS";
        } catch(Exception ex){r.exception_category=Category(ex);r.inner_category=Category(ex.InnerException);}
        Save(root,r);EditorApplication.Exit(r.status=="PASS"?0:2);
    }
}
