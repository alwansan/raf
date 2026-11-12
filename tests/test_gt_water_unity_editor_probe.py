"""Source-only negative controls for GT's read-only imported water Shader pass audit."""
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "android-port/Editor/GTOriginalWaterPassImportProbe.cs"
NATIVE = ROOT / "android-port/Editor/AndroidNativeBuild.cs"


class ImportedWaterPassProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.probe = PROBE.read_text(encoding="utf-8")
        cls.native = NATIVE.read_text(encoding="utf-8")

    def test_exact_source_pass_count_not_runtime_floor(self):
        self.assertIn(
            'new Expected("spectrum", "UltimateWater/Spectrum/Water Spectrum", 7, 6)',
            self.probe)
        self.assertIn(
            'new Expected("foam_global", "UltimateWater/Foam/Global", 2, 2)',
            self.probe)

    def test_reports_dummy_and_bounded_imported_candidate_only(self):
        for text in (
            'Shader shader = AssetDatabase.LoadAssetAtPath<Shader>(path);',
            'int passCount = shader.passCount;',
            'file.Length > 8 * 1024 * 1024',
            'File.ReadAllText(absolute).Contains("//DummyShaderTextExporter")',
            'sourceStructureCandidateOnly=',
            'sourceGUIDAndMaterialVerified=false',
            'shaderProgramKeywordParityVerified=false',
            'AndroidGpuAndPhonePixelsVerified=false',
        ):
            self.assertIn(text, self.probe)

    def test_asset_path_restricted_to_imported_unity_project(self):
        for text in (
            'Path.GetFullPath(Application.dataPath)',
            'path.Substring("Assets/".Length)',
            'absolute.StartsWith(',
            'assetRoot + Path.DirectorySeparatorChar',
        ):
            self.assertIn(text, self.probe)

    def test_no_shader_or_material_or_meta_mutations(self):
        for forbidden in (
            "File.WriteAllText", "File.WriteAllBytes", "File.Move", "File.Delete",
            "AssetDatabase.CreateAsset", "AssetDatabase.DeleteAsset",
            "AssetDatabase.MoveAsset", "AssetDatabase.SaveAssets",
            "Shader.SetGlobal", "material.Set", ".SetTexture(",
            "BuildPipeline.BuildPlayer", "PlayerSettings.",
        ):
            self.assertNotIn(forbidden, self.probe)

    def test_next_native_build_will_call_diagnostic_exactly_once(self):
        self.assertEqual(
            len(re.findall(r'\bGTOriginalWaterPassImportProbe\.Report\(\);',
                           self.native)), 1)
        self.assertIn('cp android-port/Editor/*.cs', (
            ROOT / ".github/workflows/raft-unity-editor-android-import.yml"
        ).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
