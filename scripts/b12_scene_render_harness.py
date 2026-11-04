"""Run the exact B12 Android snapshot coroutine in an asset-free managed Unity API stub.

This is an executable synthetic bounds test, not Unity Editor/player/GPU/device proof.
No proprietary Raft data are read, copied or printed.
"""
from __future__ import annotations
import argparse
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "android-port/Runtime/Platform/AndroidTestDiagnostics.cs"
START = "        private System.Collections.IEnumerator ReportSceneShaderSnapshot(Scene scene)"
END = "        private static void SceneUnloaded(Scene scene)"
QUALITY_START = "        private static string OriginalQualityStateSnapshot()"

CSPROJ = """<Project Sdk="Microsoft.NET.Sdk"><PropertyGroup>
<OutputType>Exe</OutputType><TargetFramework>net10.0</TargetFramework>
<LangVersion>9.0</LangVersion><EnableDefaultCompileItems>false</EnableDefaultCompileItems>
<ImplicitUsings>disable</ImplicitUsings><Nullable>disable</Nullable>
</PropertyGroup><ItemGroup><Compile Include="Harness.cs"/></ItemGroup></Project>
"""

STUBS = r"""
using System;
using System.Collections;
using System.Collections.Generic;
using System.Globalization;
using System.Text;
using UnityEngine;
using UnityEngine.SceneManagement;

namespace UnityEngine {
    public class Object {
        public static bool operator !(Object obj) => ReferenceEquals(obj, null);
        public static bool operator true(Object obj) => !ReferenceEquals(obj, null);
        public static bool operator false(Object obj) => ReferenceEquals(obj, null);
    }
    public class Component : Object {
        public GameObject gameObject;
        public T GetComponent<T>() where T : Component {
            foreach (Component component in gameObject.components)
                if (component is T found) return found;
            return null;
        }
    }
    public class GameObject : Object {
        public readonly List<Component> components = new List<Component>();
        public readonly Transform transform;
        public bool activeInHierarchy = true;
        public GameObject() {
            transform = new Transform { gameObject = this };
            components.Add(transform);
        }
    }
    public class Transform : Component {
        public readonly List<Transform> children = new List<Transform>();
        public int childCount => children.Count;
        public Transform GetChild(int index) => children[index];
        public void GetComponents<T>(List<T> output) where T : Component {
            output.Clear();
            foreach (Component component in gameObject.components)
                if (component is T found) output.Add(found);
        }
    }
    public class Mesh : Object {}
    public class MeshFilter : Component { public Mesh sharedMesh; }
    public class Renderer : Component {
        public bool enabled = true;
        public readonly List<Material> originalMaterials = new List<Material>();
        public void GetSharedMaterials(List<Material> output) {
            output.Clear();
            output.AddRange(originalMaterials);
        }
    }
    public class MeshRenderer : Renderer {}
    public class SkinnedMeshRenderer : Renderer { public Mesh sharedMesh; }
    public class Shader : Object { public bool isSupported = true; public string name = "Synthetic"; }
    // Production B18 snapshot is included with the scene coroutine. These
    // stubs contain only synthetic loaded objects, never a real FFT program.
    public class ComputeShader : Object { public string name = "SyntheticCompute"; }
    public static class Resources {
        public static int FindCalls;
        public static ComputeShader[] LoadedComputeShaders = Array.Empty<ComputeShader>();
        public static T[] FindObjectsOfTypeAll<T>() where T : Object {
            FindCalls++;
            if (typeof(T) == typeof(ComputeShader))
                return (T[])(object)LoadedComputeShaders;
            return Array.Empty<T>();
        }
    }
    public class Material : Object { public Shader shader; public int passCount = 1; }
    public class WaitForSecondsRealtime {
        public WaitForSecondsRealtime(float seconds) {}
    }
    public static class QualitySettings {
        public static string activeColorSpace = "Linear";
        public static string[] names = new[] { "SyntheticQuality" };
        public static int GetQualityLevel() => 0;
        public static int pixelLightCount = 4;
        public static int masterTextureLimit = 0;
        public static int antiAliasing = 4;
        public static string shadows = "All";
        public static float shadowDistance = 50f;
    }
    public static class RenderSettings {
        public static string ambientMode = "Skybox";
        public static bool fog = false;
        public static Material skybox = null;
    }
}
namespace UnityEngine.SceneManagement {
    public sealed class Scene {
        public bool isLoaded = true;
        public string name = "SyntheticScene";
        public readonly List<GameObject> roots = new List<GameObject>();
        public int rootCount => roots.Count;
        public int rootFetchCalls = 0;
        public void GetRootGameObjects(List<GameObject> output) {
            rootFetchCalls++;
            if (roots.Count > 1024) throw new Exception("Root array was materialized over budget");
            output.Clear();
            output.AddRange(roots);
        }
    }
}
namespace RaftAndroid.Diagnostics {
    public static class AndroidRuntimeLog {
        public static string Last;
        public static string LastWater;
        public static int WaterCalls;
        public static void Write(string area, string operation, string details, bool critical) {
            if (area == "render") { Last = operation + "|" + details; return; }
            if (area == "water" && operation == "loaded_compute_shader_snapshot") {
                WaterCalls++;
                LastWater = operation + "|" + details;
                return;
            }
            throw new Exception("Unexpected diagnostic area/operation");
        }
    }
}
public sealed class B12UnderTest {
    public string Probe(Scene scene) {
        RaftAndroid.Diagnostics.AndroidRuntimeLog.Last = null;
        RaftAndroid.Diagnostics.AndroidRuntimeLog.LastWater = null;
        RaftAndroid.Diagnostics.AndroidRuntimeLog.WaterCalls = 0;
        UnityEngine.Resources.FindCalls = 0;
        IEnumerator routine = ReportSceneShaderSnapshot(scene);
        int steps = 0;
        while (routine.MoveNext()) {
            if (++steps > 2) throw new Exception("Unexpected repeated frame work");
        }
        return RaftAndroid.Diagnostics.AndroidRuntimeLog.Last ?? "";
    }
"""

TESTS = r"""
    private static Material Mat(bool supported=true, int passes=1, string name="Synthetic") =>
        new Material { shader = new Shader { isSupported = supported, name = name }, passCount = passes };
    private static GameObject Node() => new GameObject();
    private static GameObject Child(GameObject parent) {
        GameObject child = Node();
        parent.transform.children.Add(child.transform);
        return child;
    }
    private static void RendererOn(GameObject go, Renderer renderer, Material mat) {
        renderer.gameObject = go;
        renderer.originalMaterials.Add(mat);
        go.components.Add(renderer);
    }
    private static void Require(bool ok, string message) {
        if (!ok) throw new Exception("B12 synthetic contract: " + message);
    }
    private static void Has(string report, string field) => Require(report.Contains(field), field);
    public static void Main() {
        B12UnderTest probe = new B12UnderTest();
        // A synthetic source object verifies that the production B18 helper
        // executes, not merely compiles; it does not test kernels or GPU pixels.
        Resources.LoadedComputeShaders = new[] { new ComputeShader { name = "SyntheticFFT" } };

        Scene shallow = new Scene();
        GameObject root = Node();
        shallow.roots.Add(root);
        RendererOn(root, new MeshRenderer(), Mat());
        GameObject skinned = Child(root);
        RendererOn(skinned, new SkinnedMeshRenderer { sharedMesh = new Mesh() }, Mat());
        GameObject bad = Child(root);
        RendererOn(bad, new Renderer(), Mat(false, 0, "Hidden/InternalErrorShader"));
        string report = probe.Probe(shallow);
        Has(report, "visible_renderers_sampled=3; truncated=False");
        Has(report, "limit_reason=none");
        Has(report, "missing_mesh_filters=1");
        Has(report, "missing_skinned_meshes=0");
        Has(report, "unsupported_shaders=1");
        Has(report, "zero_pass_materials=1");
        Has(report, "internal_error_shaders=1");
        Require(shallow.rootFetchCalls == 1, "normal root fetch count");
        Require(Resources.FindCalls == 1, "exactly one loaded compute resource query");
        Require(RaftAndroid.Diagnostics.AndroidRuntimeLog.WaterCalls == 1,
            "exactly one read-only water snapshot");
        Has(RaftAndroid.Diagnostics.AndroidRuntimeLog.LastWater, "loaded_total=1");
        Has(RaftAndroid.Diagnostics.AndroidRuntimeLog.LastWater, "runtime_kernel_count_verified=false");

        Scene tooManyRoots = new Scene();
        for (int i = 0; i < 1025; i++) tooManyRoots.roots.Add(Node());
        report = probe.Probe(tooManyRoots);
        Has(report, "truncated=True; limit_reason=root_limit");
        Require(tooManyRoots.rootFetchCalls == 0, "root fetch under cap");

        Scene wide = new Scene();
        root = Node();
        wide.roots.Add(root);
        for (int i = 0; i < 1025; i++) Child(root);
        report = probe.Probe(wide);
        Has(report, "truncated=True; limit_reason=pending_limit");
        Has(report, "visited_transforms=1");

        Scene deep = new Scene();
        root = Node();
        deep.roots.Add(root);
        for (int i = 0; i < 5000; i++) root = Child(root);
        report = probe.Probe(deep);
        Has(report, "visited_transforms=4096");
        Has(report, "truncated=True; limit_reason=transform_limit");

        Scene renderers = new Scene();
        root = Node();
        renderers.roots.Add(root);
        for (int i = 0; i < 515; i++) {
            RendererOn(root, new Renderer(), Mat());
            root = Child(root);
        }
        report = probe.Probe(renderers);
        Has(report, "visible_renderers_sampled=512; truncated=True");
        Has(report, "limit_reason=renderer_limit");

        Scene manyMaterials = new Scene();
        root = Node();
        manyMaterials.roots.Add(root);
        Renderer renderer = new Renderer { gameObject = root };
        for (int i = 0; i < 4100; i++) renderer.originalMaterials.Add(Mat());
        root.components.Add(renderer);
        report = probe.Probe(manyMaterials);
        Has(report, "material_slots=4096");
        Has(report, "truncated=True; limit_reason=material_limit");

        Scene inactive = new Scene();
        root = Node();
        root.activeInHierarchy = false;
        inactive.roots.Add(root);
        RendererOn(root, new Renderer(), Mat());
        report = probe.Probe(inactive);
        Has(report, "visible_renderers_sampled=0; truncated=False");

        Scene unloaded = new Scene { isLoaded = false };
        unloaded.roots.Add(Node());
        report = probe.Probe(unloaded);
        Require(report == "", "unloaded scene must not log snapshot");
        Require(unloaded.rootFetchCalls == 0, "unloaded scene roots not enumerated");
        Require(Resources.FindCalls == 0, "unloaded scene must not query compute objects");
        Require(RaftAndroid.Diagnostics.AndroidRuntimeLog.WaterCalls == 0,
            "unloaded scene must not emit the water snapshot");

        Console.WriteLine("B12_SCENE_BOUNDS_MANAGED cases=8 exactProductionMethod=true originalGameAssets=false unity=false device=false");
    }
}
"""

def build(out: Path) -> Path:
    out = Path(out)
    if out.exists() or out.is_symlink():
        raise ValueError("B12 test output must be absent and non-symlinked")
    source = SOURCE.read_text(encoding="utf-8")
    if source.count(START) != 1 or source.count(END) != 1:
        raise ValueError("Unrecognized original B12 renderer diagnostic method")
    method = source[source.index(START):source.index(END)]
    quality = ""
    if "OriginalQualityStateSnapshot()" in method:
        if source.count(QUALITY_START) != 1:
            raise ValueError("Unknown same-source quality helper integration")
        quality = source[source.index(QUALITY_START):source.index(START)]
    if "LoadedComputeShaderSnapshot()" not in method:
        raise ValueError("Production B18 loaded-compute evidence was removed from scene snapshot")
    for required in ("const int RootLimit = 1024;", "const int TransformLimit = 4096;",
                     "const int PendingLimit = 1024;", "const int RendererLimit = 512;",
                     "const int MaterialLimit = 4096;", "renderer.GetSharedMaterials(materials);"):
        if required not in method:
            raise ValueError("B12 production method budget contract changed")
    out.mkdir(parents=True)
    (out / "B12Harness.csproj").write_text(CSPROJ, encoding="utf-8")
    (out / "Harness.cs").write_text(STUBS + quality + method + TESTS, encoding="utf-8")
    return out / "B12Harness.csproj"

if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--output", type=Path, required=True)
    args = ap.parse_args()
    project = build(args.output)
    print("B12_SCENE_BOUNDS_HARNESS sourceMethod=true output=" + project.name)
