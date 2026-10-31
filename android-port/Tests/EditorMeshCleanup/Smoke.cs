// Deliberately tiny Unity API doubles: lifecycle policy tests, not Unity evidence.
using System;
using System.Reflection;
using MeshCombineStudio;
namespace UnityEngine
{
    public class Object
    {
        public static int Deferred, Immediate;
        public static void Destroy(Object value) { Deferred++; }
        public static void DestroyImmediate(Object value) { Immediate++; }
    }
    public class Mesh : Object { public bool Persistent; }
    public class MonoBehaviour : Object { }
    public class ExecuteInEditMode : Attribute { }
    public static class Application { public static bool isPlaying; }
}
#if UNITY_EDITOR
namespace UnityEditor
{
    public static class EditorUtility
    {
        public static bool IsPersistent(UnityEngine.Object value)
        { return ((UnityEngine.Mesh)value).Persistent; }
    }
}
#endif
class Smoke
{
    static int checks;
    static void Check(bool playing, bool persistent, bool skip, bool empty,
                      int deferred, int immediate)
    {
        UnityEngine.Application.isPlaying = playing;
        UnityEngine.Object.Deferred = UnityEngine.Object.Immediate = 0;
        GarbageCollectMesh.SkipGC = skip;
        var collector = new GarbageCollectMesh();
        collector.mesh = empty ? null : new UnityEngine.Mesh { Persistent = persistent };
        typeof(GarbageCollectMesh).GetMethod("OnDestroy", BindingFlags.NonPublic | BindingFlags.Instance)
            .Invoke(collector, null);
        if (UnityEngine.Object.Deferred != deferred || UnityEngine.Object.Immediate != immediate)
            throw new Exception("Unexpected lifecycle policy at case " + checks);
        if (!empty && collector.mesh.Persistent != persistent)
            throw new Exception("Original persistent flag changed");
        checks++;
    }
    static void Main()
    {
#if UNITY_EDITOR
        Check(false, true, false, false, 0, 0); // Never destroy persistent assets.
        Check(false, false, false, false, 0, 1); // Edit-mode transient cleanup.
        Check(false, false, true, false, 0, 0); // Original SkipGC contract.
        Check(false, false, false, true, 0, 0);
#else
        Check(false, true, false, false, 1, 0); // Conditional guard absent.
        Check(false, false, false, false, 1, 0);
        Check(false, false, true, false, 0, 0);
        Check(false, false, false, true, 0, 0);
#endif
        Check(true, true, false, false, 1, 0);
        Check(true, false, false, false, 1, 0);
        Check(true, false, true, false, 0, 0);
        Check(true, false, false, true, 0, 0);
        Console.WriteLine("RAFT_EDITOR_MESH_POLICY checks=" + checks + " passed=true");
    }
}
