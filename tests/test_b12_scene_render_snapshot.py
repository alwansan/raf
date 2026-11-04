"""B12 source contract for bounded Android scene-render diagnosis, not device proof."""
import unittest
from pathlib import Path
S = (Path(__file__).resolve().parents[1] / "android-port/Runtime/Platform/AndroidTestDiagnostics.cs").read_text("utf-8")
PART = S.split("private System.Collections.IEnumerator ReportSceneShaderSnapshot(Scene scene)", 1)[1].split("private static void SceneUnloaded(Scene scene)", 1)[0]

class B12Probe(unittest.TestCase):
    def test_lifecycle_and_delay(self):
        for s in ("SceneManager.sceneLoaded += SceneLoaded;",
                  "SceneManager.sceneLoaded -= SceneLoaded;",
                  "StartCoroutine(ReportSceneShaderSnapshot(scene));"):
            self.assertIn(s,S)
        self.assertIn("yield return new WaitForSecondsRealtime(3f);",PART)
        self.assertIn("if (!scene.isLoaded) yield break;",PART)

    def test_bounded_and_active_only(self):
        for s in ("const int RendererLimit = 512;", "if (sampled >= RendererLimit)",
                  "scene.GetRootGameObjects()", "renderer.enabled",
                  "renderer.gameObject.activeInHierarchy", "truncated="):
            self.assertIn(s,PART)

    def test_no_material_clone_or_render_mutation(self):
        self.assertIn("renderer.sharedMaterials",PART)
        for s in ("renderer.material;", "new Material(", "SetPass(", "SetShader(",
                  "WorldHasBeenRecieved =", "SteamUserStats.StoreStats"):
            self.assertNotIn(s,PART)

    def test_differential_shader_error_categories(self):
        for s in ("null_materials=", "null_shaders=", "unsupported_shaders=",
                  "zero_pass_materials=", "internal_error_shaders=",
                  "!shader.isSupported", "material.passCount == 0",
                  'shader.name == "Hidden/InternalErrorShader"'):
            self.assertIn(s,PART)


    def test_shared_mesh_presence_without_geometry_readback(self):
        for term in ("renderer as MeshRenderer", "renderer as SkinnedMeshRenderer",
                     "GetComponent<MeshFilter>()", "filter.sharedMesh",
                     "skinnedRenderer.sharedMesh", "mesh_renderers=",
                     "missing_mesh_filters=", "missing_mesh_assets=",
                     "skinned_renderers=", "missing_skinned_meshes="):
            self.assertIn(term, PART)
        for term in ("mesh.triangles", "mesh.vertices", "new Mesh(",
                     ".mesh =", ".sharedMesh =", "GetMesh("):
            self.assertNotIn(term, PART)

    def test_ambient_and_error_reporting(self):
        for s in ("QualitySettings.activeColorSpace", "RenderSettings.ambientMode",
                  "RenderSettings.fog", "RenderSettings.skybox",
                  "scene_shader_snapshot.unavailable", "error_type=",
                  "original_shader_pixels_verified=false"):
            self.assertIn(s,PART)
