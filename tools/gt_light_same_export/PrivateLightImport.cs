// Editor-only observer of the exact private exported scene. No save, play or player build.
using System;
using System.Collections.Generic;
using System.Globalization;
using System.IO;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UObject = UnityEngine.Object;

public static class GTPrivateLightImport
{
    [Serializable] public class Node {
        public string id, owner, parent;
        public int cid, lightType;
        public bool hasOwner, hasParent, hasChildren, hasActive, hasTRS, hasLight, active, enabled;
        public string[] children, components;
        public float[] position, rotation, scale, color;
        public float intensity, range;
    }
    [Serializable] public class Manifest { public string guid; public Node[] nodes; }
    [Serializable] public class Report {
        public string status="INCONCLUSIVE";
        public bool sceneOpened, sceneGuidMatched;
        public int matchedObjects, checks, mismatches;
        public List<string> mismatchCategories=new List<string>();
    }
    static void Check(Report r,string category,bool pass) {
        r.checks++;
        if (!pass) {
            r.mismatches++;
            if (!r.mismatchCategories.Contains(category)) r.mismatchCategories.Add(category);
        }
    }
    static bool Close(float a,float b) {
        return !float.IsNaN(a) && !float.IsInfinity(a) && !float.IsNaN(b) && !float.IsInfinity(b)
            && Mathf.Abs(a-b)<=Mathf.Max(0.00002f,0.000002f*Mathf.Max(Mathf.Abs(a),Mathf.Abs(b)));
    }
    static bool Vec(float[] expected,params float[] actual) {
        if(expected==null || expected.Length!=actual.Length)return false;
        for(int i=0;i<actual.Length;i++)if(!Close(expected[i],actual[i]))return false;
        return true;
    }
    static int Class(UObject o) {
        if(o is GameObject)return 1;
        if(o is RectTransform)return 224;
        if(o is Transform)return 4;
        if(o is Light)return 108;
        return 0;
    }
    static string Id(UObject o,string guid) {
        if(o==null)return "0";
        var x=GlobalObjectId.GetGlobalObjectIdSlow(o);
        if(x.assetGUID.ToString()!=guid || x.targetObjectId==0 || x.targetPrefabId!=0)return null;
        return unchecked((long)x.targetObjectId).ToString(CultureInfo.InvariantCulture);
    }
    static void Add(UObject o,string guid,Dictionary<string,UObject> found) {
        string id=Id(o,guid);
        if(id==null || id=="0")return;
        if(found.ContainsKey(id))throw new InvalidOperationException();
        found.Add(id,o);
    }
    static void Visit(Transform t,string guid,Dictionary<string,UObject> found) {
        Add(t.gameObject,guid,found);
        Add(t,guid,found);
        foreach(Light l in t.gameObject.GetComponents<Light>())if(l!=null)Add(l,guid,found);
        for(int i=0;i<t.childCount;i++)Visit(t.GetChild(i),guid,found);
    }
    public static void Run() {
        var r=new Report();
        string root=Path.GetFullPath(Path.Combine(Application.dataPath,".."));
        try {
            Manifest m=JsonUtility.FromJson<Manifest>(File.ReadAllText(Path.Combine(root,"expected-private.json")));
            const string assetPath="Assets/PrivateScene.unity";
            r.sceneGuidMatched=AssetDatabase.AssetPathToGUID(assetPath)==m.guid;
            if(!r.sceneGuidMatched)throw new InvalidOperationException();
            Scene s=EditorSceneManager.OpenScene(assetPath,OpenSceneMode.Single);
            r.sceneOpened=s.IsValid()&&s.isLoaded;
            if(!r.sceneOpened)throw new InvalidOperationException();
            var found=new Dictionary<string,UObject>();
            foreach(GameObject go in s.GetRootGameObjects())Visit(go.transform,m.guid,found);
            foreach(Node n in m.nodes) {
                UObject o;
                bool present=found.TryGetValue(n.id,out o);
                Check(r,"identity",present);
                if(!present)continue;
                r.matchedObjects++;
                bool typed=Class(o)==n.cid;
                Check(r,"native_class",typed);
                if(!typed)continue;
                if(n.hasOwner)Check(r,"component_owner",Id(((Component)o).gameObject,m.guid)==n.owner);
                if(n.hasActive) {
                    var go=(GameObject)o;
                    Check(r,"activeSelf",go.activeSelf==n.active);
                    Check(r,"activeInHierarchy",go.activeInHierarchy==n.active);
                    var ids=new HashSet<string>();
                    foreach(Component c in go.GetComponents<Component>())if(c!=null&&Class(c)!=0)ids.Add(Id(c,m.guid));
                    foreach(string id in n.components)Check(r,"component_membership",ids.Contains(id));
                }
                if(n.hasParent)Check(r,"parent",Id(((Transform)o).parent,m.guid)==n.parent);
                if(n.hasChildren) {
                    var t=(Transform)o;
                    bool good=t.childCount==n.children.Length;
                    if(good)for(int i=0;i<t.childCount;i++)if(Id(t.GetChild(i),m.guid)!=n.children[i])good=false;
                    Check(r,"ordered_children",good);
                }
                if(n.hasTRS) {
                    var t=(Transform)o;var p=t.localPosition;var q=t.localRotation;var z=t.localScale;
                    Check(r,"local_position",Vec(n.position,p.x,p.y,p.z));
                    Check(r,"local_rotation",Vec(n.rotation,q.x,q.y,q.z,q.w));
                    Check(r,"local_scale",Vec(n.scale,z.x,z.y,z.z));
                }
                if(n.hasLight) {
                    var l=(Light)o;var c=l.color;
                    Check(r,"enabled",l.enabled==n.enabled);
                    Check(r,"isActiveAndEnabled",l.isActiveAndEnabled==n.enabled);
                    Check(r,"light_type",(int)l.type==n.lightType);
                    Check(r,"light_color",Vec(n.color,c.r,c.g,c.b,c.a));
                    Check(r,"light_intensity",Close(n.intensity,l.intensity));
                    Check(r,"light_range",Close(n.range,l.range));
                }
            }
            r.status=r.mismatches==0&&r.matchedObjects==m.nodes.Length?"PASS":"FAIL";
        } catch(Exception) {
            r.status="INCONCLUSIVE";
            r.mismatchCategories.Add("editor_exception");
        }
        File.WriteAllText(Path.Combine(root,"import-safe.json"),JsonUtility.ToJson(r,true));
        Debug.Log("GT_LIGHT_PRIVATE_IMPORT_STATUS="+r.status+" matched="+r.matchedObjects+" checks="+r.checks+" mismatches="+r.mismatches);
        EditorApplication.Exit(r.status=="PASS"?0:2);
    }
}
