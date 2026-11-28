// Authored guarded staging and separate world-space verification.
using System;
using System.Collections.Generic;
using System.IO;
using System.Security.Cryptography;
using UnityEditor;
using UnityEngine;
using UObject=UnityEngine.Object;

public static partial class GTPrivateLightImport {
    [Serializable] public class FreshCommit {public string run_id,scene,meta,expected,world,same_export,raw_stage;}
    [Serializable] public class WorldRow {public string id;public float[] matrix,position,direction;public bool active;}
    [Serializable] public class WorldManifest {public WorldRow[] rows;public string light_id,light_transform_id;}
    [Serializable] public class WorldReceipt {
        public string run_id,commitment_sha256,status="INCONCLUSIVE";
        public bool private_guard,light_owner_match,light_active_match;
        public int world_rows,world_checks,world_mismatches;
    }
    static string FreshPrivate="/github/workspace/gt-light-fresh-private";
    static FreshCommit FreshExpected;static string FreshDigest;
    static string FreshSha(string file){
        using(var hash=SHA256.Create())using(var stream=File.OpenRead(file))
            return BitConverter.ToString(hash.ComputeHash(stream)).Replace("-","").ToLowerInvariant();
    }
    static void FreshNeed(bool pass){if(!pass)throw new InvalidOperationException();}
    static string FreshArg(string name){
        var args=Environment.GetCommandLineArgs();int i=Array.IndexOf(args,name);
        FreshNeed(i>=0&&i+1<args.Length);return args[i+1];
    }
    static void FreshCopy(string name,string dest,string digest){
        string src=Path.Combine(FreshPrivate,name);
        FreshNeed(FreshSha(src)==digest&&!File.Exists(dest));
        File.Copy(src,dest,false);FreshNeed(FreshSha(dest)==digest);
    }
    static void PrepareFresh(string root){
        string id=FreshArg("-gtLightRunId");
        FreshNeed(Application.isBatchMode&&Application.unityVersion=="2021.3.45f2"&&
                  File.Exists(Path.Combine(FreshPrivate,"editor-output-private"))&&
                  File.ReadAllText(Path.Combine(FreshPrivate,"editor-output-private")).Trim()==id);
        string manifest=Path.Combine(FreshPrivate,"commitment.json");
        FreshDigest=FreshSha(manifest);FreshExpected=JsonUtility.FromJson<FreshCommit>(File.ReadAllText(manifest));
        FreshNeed(FreshExpected!=null&&FreshExpected.run_id==id&&
                  FreshSha(Path.Combine(FreshPrivate,"expected-world.json"))==FreshExpected.world);
        FreshCopy("expected-private.json",Path.Combine(root,"expected-private.json"),FreshExpected.expected);
        FreshCopy("PrivateScene.unity",Path.Combine(Application.dataPath,"PrivateScene.unity"),FreshExpected.scene);
        FreshCopy("PrivateScene.unity.meta",Path.Combine(Application.dataPath,"PrivateScene.unity.meta"),FreshExpected.meta);
        AssetDatabase.Refresh(ImportAssetOptions.ForceSynchronousImport);
    }
    static void WorldCheck(WorldReceipt r,bool pass){r.world_checks++;if(!pass)r.world_mismatches++;}
    static void ObserveWorld(string root,string guid,Dictionary<string,UObject> found){
        var r=new WorldReceipt{run_id=FreshExpected.run_id,commitment_sha256=FreshDigest,private_guard=true};
        try{
            string file=Path.Combine(FreshPrivate,"expected-world.json");FreshNeed(FreshSha(file)==FreshExpected.world);
            var expected=JsonUtility.FromJson<WorldManifest>(File.ReadAllText(file));
            FreshNeed(expected!=null&&expected.rows.Length==3);
            foreach(var n in expected.rows){
                FreshNeed(found.TryGetValue(n.id,out UObject obj)&&obj is Transform);
                var t=(Transform)obj;var matrix=t.localToWorldMatrix;var values=new float[16];
                for(int y=0;y<4;y++)for(int x=0;x<4;x++)values[y*4+x]=matrix[y,x];
                WorldCheck(r,Vec(n.matrix,values));
                var p=t.position;var d=t.forward;
                WorldCheck(r,Vec(n.position,p.x,p.y,p.z));
                WorldCheck(r,Vec(n.direction,d.x,d.y,d.z));
                WorldCheck(r,t.gameObject.activeInHierarchy==n.active);
                r.world_rows++;
            }
            FreshNeed(found.TryGetValue(expected.light_id,out UObject objLight)&&objLight is Light);
            var light=(Light)objLight;
            r.light_owner_match=Id(light.transform,guid)==expected.light_transform_id;
            r.light_active_match=light.isActiveAndEnabled&&light.gameObject.activeInHierarchy;
            r.status=r.world_rows==3&&r.world_checks==12&&r.world_mismatches==0&&r.light_owner_match&&r.light_active_match?"PASS":"FAIL";
        }finally{
            File.WriteAllText(Path.Combine(FreshPrivate,"world-safe.json"),JsonUtility.ToJson(r));
        }
    }
}
