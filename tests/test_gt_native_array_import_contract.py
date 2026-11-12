"""GT native build pipeline source-authentic Texture2DArray restore contract.

Source-free static guard: real ZIP2 originals + same AssetRipper export trace
must repair all nine original imported PNG array grids before T5's existing
B46 Material and shader gates. No XAPK launch or changes to scene/asset data.
"""
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
WORKFLOW=ROOT/".github/workflows/raft-unity-editor-android-import.yml"
EDITOR=ROOT/"android-port/Editor/AndroidNativeBuild.cs"
GUARD=ROOT/"android-port/Editor/OriginalTextureArrayImportGuard.cs"


class GTNativeArrayImportContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.workflow=WORKFLOW.read_text(encoding="utf-8")
        cls.editor=EDITOR.read_text(encoding="utf-8")
        cls.guard=GUARD.read_text(encoding="utf-8")

    def test_source_authentic_array_stage_in_actual_native_lane_before_all_material_checks(self):
        body=self.workflow
        source=body.index("      - name: Export 40 scenes into a Unity Editor project with correct MonoScript metadata")
        restore=body.index("      - name: GT restore nine original Texture2DArray importer grids before every native Material/Shader link gate")
        color=body.index("      - name: B04 restore original Linear color space")
        material=body.index("      - name: T5 inspect actual postrestorer Material-to-Texture references")
        final=body.index("      - name: Stage private Unity project candidate inside runner workspace")
        self.assertLess(source,restore)
        self.assertLess(restore,color)
        self.assertLess(restore,material)
        self.assertLess(restore,final)

    def test_strict_source_verified_guids_and_all_28_materials_or_fail(self):
        body=self.workflow
        stage=body.split("      - name: GT restore nine original Texture2DArray importer grids",1)[1].split(
              "      - name: GT publish source-authentic array importer",1)[0]
        self.assertNotIn("continue-on-error",stage)
        self.assertIn("scripts.gt_repair_array_flipbook_importers",stage)
        self.assertIn("scripts.gt_verify_original_array_material_refs",stage)
        self.assertIn("zip2-original/RAFT_FILE_MANIFEST.tsv",stage)
        self.assertIn("$RUNNER_TEMP/private-export-lineage.json",stage)
        # Mesh inlining mutates the export input. Class187 provenance must come
        # from immutable, SHA-verified ZIP2 serialized owners, never that input.
        self.assertIn('scripts.gt_stage_serialized_owners',stage)
        self.assertIn('--source zip2-original/Raft/Raft_Data',stage)
        self.assertIn('original_owners="$RUNNER_TEMP/gt-native-pristine-serialized-owners"',stage)
        self.assertEqual(stage.count('--original-source "$original_owners"'),3)
        self.assertNotIn('--original-source "$RUNNER_TEMP/input/Raft_Data"',stage)
        self.assertIn('rm -rf -- "$original_owners"',stage)
        self.assertIn("exact_original_class187_array_material_refs']==28",stage)
        self.assertIn("distinct_source_array_guids_referenced_by_materials']==9",stage)
        self.assertIn("original_exported_asset_guids_preserved",stage)
        self.assertIn("meta_files_outside_the_exactly_verified_array_set_changed",stage)
        self.assertIn("source_images_or_binaries_edited",stage)
        self.assertNotIn("git lfs",stage.lower())

    def test_Unity_Editor_really_checks_nine_native_array_assets_from_private_source_contract(self):
        self.assertIn("OriginalTextureArrayImportGuard.Validate();",self.editor)
        self.assertIn("OriginalTextureArrayImportGuard",self.guard)
        self.assertIn("GTOriginalArrayImportContract.json",self.guard)
        self.assertIn("TextureImporterShape.Texture2DArray",self.guard)
        self.assertIn("AssetDatabase.GUIDToAssetPath",self.guard)
        self.assertIn("AssetDatabase.LoadAssetAtPath<Texture2DArray>",self.guard)
        self.assertIn("importedArray.mipmapCount != array.mipmap_count",self.guard)
        self.assertIn("importedArray.depth != array.depth",self.guard)
        self.assertIn("seen.Count != 9",self.guard)
        self.assertIn("originalPixelLayers != 50",self.guard)
        self.assertIn("throw new BuildFailedException",self.guard)
        self.assertIn("Unity Editor 2021.3.45f2 Android import and compile",self.workflow)
        self.assertIn("scripts.gt_write_unity_array_import_contract",self.workflow)
        self.assertIn("test -s \"$RUNNER_TEMP/project/ExportedProject/Assets/Editor/RaftAndroid/GTOriginalArrayImportContract.json\"",self.workflow)

    def test_existing_T5_build_request_gates_and_shader_water_acceptance_unchanged(self):
        body=self.workflow
        self.assertIn("'.github/raft-native-build-request.json'",body)
        self.assertIn("T5 inspect actual postrestorer Material-to-Texture references",body)
        self.assertIn("Authentic water gate (strict)",body)
        self.assertIn("Raft full native APK OBB XAPK build and delivery",body)
        self.assertIn("lfs: false",body)
        self.assertIn("Stage private Unity project candidate inside runner workspace",body)


if __name__=="__main__":
    unittest.main()
