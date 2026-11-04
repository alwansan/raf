"""B12 bounded Unity Android scene diagnostics policy (synthetic source controls, not device proof)."""
import re
import unittest
from pathlib import Path

SOURCE = Path(__file__).resolve().parents[1] / "android-port/Runtime/Platform/AndroidTestDiagnostics.cs"
S = SOURCE.read_text("utf-8")
PART = S.split("private System.Collections.IEnumerator ReportSceneShaderSnapshot(Scene scene)", 1)[1].split("private static void SceneUnloaded(Scene scene)", 1)[0]


class B12Probe(unittest.TestCase):
    def test_lifecycle_and_delay(self):
        for item in ("SceneManager.sceneLoaded += SceneLoaded;",
                     "SceneManager.sceneLoaded -= SceneLoaded;",
                     "StartCoroutine(ReportSceneShaderSnapshot(scene));"):
            self.assertIn(item, S)
        self.assertIn("yield return new WaitForSecondsRealtime(3f);", PART)
        self.assertIn("if (!scene.isLoaded) yield break;", PART)

    def test_renderer_and_tree_work_bounded_before_collection(self):
        for item in ("const int RootLimit = 1024;", "const int TransformLimit = 4096;",
                     "const int PendingLimit = 1024;", "const int RendererLimit = 512;",
                     "const int MaterialLimit = 4096;",
                     "if (rootCount > RootLimit)", "if (visitedTransforms >= TransformLimit)",
                     "if (pendingCount >= PendingLimit)", "if (sampled >= RendererLimit)",
                     "if (slots >= MaterialLimit)", "truncated=", "limit_reason="):
            self.assertIn(item, PART)
        # The previous source cap was misleading: the whole root hierarchy
        # Renderer[] was allocated before the 512-renderer loop limit.
        # Scan executable source only: the source comment names the retired API.
        executable = re.sub(r"//[^\n]*|/\*[\s\S]*?\*/", "", PART)
        self.assertNotIn("GetComponentsInChildren<Renderer>", executable)
        self.assertNotIn("GetComponentsInChildren(", executable)
        self.assertNotIn("scene.GetRootGameObjects()", PART)
        self.assertIn("scene.GetRootGameObjects(roots);", PART)
        self.assertIn("current.GetComponents<Renderer>(renderers);", PART)

    def test_root_array_preflight_and_explicit_partial_result(self):
        self.assertLess(PART.index("if (rootCount > RootLimit)"),
                        PART.index("scene.GetRootGameObjects(roots);"))
        self.assertIn('limitReason = "root_limit";', PART)
        self.assertIn('limitReason = "transform_limit";', PART)
        self.assertIn('limitReason = "pending_limit";', PART)
        self.assertIn('limitReason = "renderer_limit";', PART)
        self.assertIn('limitReason = "material_limit";', PART)
        self.assertIn("root_count=", PART)
        self.assertIn("visited_transforms=", PART)

    def test_reusable_renderer_list_and_fixed_tree_stack(self):
        for item in ("var pending = new Transform[PendingLimit];",
                     "var renderers = new List<Renderer>(4);", "renderers.Clear();",
                     "pending[pendingCount++] = root.transform;",
                     "pending[pendingCount++] = current.GetChild(child);",
                     "pending[pendingCount] = null;", "current.childCount"):
            self.assertIn(item, PART)
        self.assertLess(PART.index("if (visitedTransforms >= TransformLimit)"),
                        PART.index("current.GetComponents<Renderer>(renderers);"))
        self.assertLess(PART.index("if (pendingCount >= PendingLimit)"),
                        PART.index("pending[pendingCount++] = current.GetChild(child);"))

    def test_only_active_enabled_renderers_sampled(self):
        for item in ("!root.activeInHierarchy", "!current.gameObject.activeInHierarchy",
                     "renderer.enabled", "renderer.gameObject.activeInHierarchy"):
            self.assertIn(item, PART)

    def test_no_material_clone_or_render_mutation(self):
        self.assertIn("renderer.sharedMaterials", PART)
        for forbidden in ("renderer.material;", "new Material(", "new Mesh(", "SetPass(",
                          "SetShader(", "WorldHasBeenRecieved =", "SteamUserStats.StoreStats",
                          "mesh.vertices", "mesh.triangles", ".sharedMesh ="):
            self.assertNotIn(forbidden, PART)

    def test_differential_shader_error_categories(self):
        for item in ("null_materials=", "null_shaders=", "unsupported_shaders=",
                     "zero_pass_materials=", "internal_error_shaders=",
                     "!shader.isSupported", "material.passCount == 0",
                     'shader.name == "Hidden/InternalErrorShader"'):
            self.assertIn(item, PART)

    def test_shared_mesh_presence_without_geometry_readback(self):
        for item in ("renderer as MeshRenderer", "renderer as SkinnedMeshRenderer",
                     "GetComponent<MeshFilter>()", "filter.sharedMesh",
                     "skinnedRenderer.sharedMesh", "mesh_renderers=",
                     "missing_mesh_filters=", "missing_mesh_assets=",
                     "skinned_renderers=", "missing_skinned_meshes="):
            self.assertIn(item, PART)

    def test_ambient_and_error_reporting(self):
        for item in ("QualitySettings.activeColorSpace", "RenderSettings.ambientMode",
                     "RenderSettings.fog", "RenderSettings.skybox",
                     "scene_shader_snapshot.unavailable", "error_type=",
                     "original_shader_pixels_verified=false"):
            self.assertIn(item, PART)

    def test_no_iterator_yield_inside_catch_guard(self):
        # C# iterators cannot yield in a try that has a catch. The single
        # startup yield and scene-unload exit are both before the guarded scan.
        self.assertEqual(len(re.findall(r"\byield\s+(?:return|break)\b", PART)), 2)
        self.assertLess(PART.index("if (!scene.isLoaded) yield break;"), PART.index("try"))

    def test_scene_lifecycle_preserved(self):
        for item in ("SceneManager.sceneLoaded += SceneLoaded;",
                     "SceneManager.sceneLoaded -= SceneLoaded;",
                     'AndroidRuntimeLog.Write("scene", "loaded"',
                     "private static void SceneUnloaded(Scene scene)",
                     "private static void ActiveSceneChanged(Scene before, Scene after)"):
            self.assertIn(item, S)


if __name__ == "__main__":
    unittest.main()
