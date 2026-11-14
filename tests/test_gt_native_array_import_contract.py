"""GT native build pipeline source-authentic Texture2DArray restore contract.

Source-free static guard: real ZIP2 originals + same AssetRipper export trace
must verify all nine native array payloads before T5's existing
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
        restore=body.index("      - name: GT verify nine native Texture2DArray assets before every Material and Shader link gate")
        color=body.index("      - name: B04 restore original Linear color space")
        material=body.index("      - name: T5 inspect actual postrestorer Material-to-Texture references")
        final=body.index("      - name: Stage private Unity project candidate inside runner workspace")
        self.assertLess(source,restore)
        self.assertLess(restore,color)
        self.assertLess(restore,material)
        self.assertLess(restore,final)

    def test_strict_source_verified_guids_and_all_28_materials_or_fail(self):
        body=self.workflow
        stage=body.split("      - name: GT verify nine native Texture2DArray assets",1)[1].split(
              "      - name: GT publish native array and Material",1)[0]
        self.assertNotIn("continue-on-error",stage)
        self.assertIn("--mesh-lineage --native-texture-arrays",body)
        self.assertIn("scripts.gt_write_unity_array_import_contract",stage)
        self.assertIn("zip2-original/RAFT_FILE_MANIFEST.tsv",stage)
        self.assertIn("$RUNNER_TEMP/private-export-lineage.json",stage)
        self.assertIn('scripts.gt_stage_serialized_owners',stage)
        self.assertIn('--source zip2-original/Raft/Raft_Data',stage)
        self.assertIn('--original-source "$original_owners"',stage)
        self.assertIn('--native-stream-source "$RUNNER_TEMP/input/Raft_Data"',stage)
        self.assertIn('rm -rf -- "$original_owners"',stage)
        self.assertNotIn('gt_repair_array_flipbook_importers',stage)

    def test_all_416_source_external_texture_references_must_match_same_export_before_android(self):
        body=self.workflow
        stage=body.split("      - name: GT verify nine native Texture2DArray assets",1)[1].split(
              "      - name: GT publish native array and Material",1)[0]
        self.assertIn('python3 -m scripts.gt_external_original_texture_links',stage)
        self.assertIn('--source "$original_owners"',stage)
        self.assertIn('--manifest zip2-original/RAFT_FILE_MANIFEST.tsv',stage)
        self.assertIn('--trace "$RUNNER_TEMP/private-export-lineage.json"',stage)
        self.assertIn("d['authenticated_owner_tables']==82",stage)
        self.assertIn("d['original_external_texture_slots']==416",stage)
        self.assertIn("d['exact_cross_owner_source_export_texture_links']==416",stage)
        self.assertIn("d['external_links_not_yet_proven']==0",stage)
        self.assertIn("d['all_external_links_verified'] is True",stage)
        self.assertLess(stage.index('scripts.gt_external_original_texture_links'),
                        stage.index('rm -rf -- "$original_owners"'))
        self.assertNotIn("continue-on-error",stage)
        self.assertIn('gt-native-original-external-texture-links.json',body)
        # The source trace must not be rewritten to a guessed flat Texture2D.
        self.assertNotIn('sed -i',stage)
        self.assertNotIn('git lfs',stage.lower())

    def test_full_native_mip_and_material_gate_uses_same_export_before_cleanup(self):
        stage=self.workflow.split("      - name: GT verify nine native Texture2DArray assets",1)[1].split(
              "      - name: GT publish native array and Material",1)[0]
        self.assertIn('--project "$RUNNER_TEMP/project/ExportedProject"',stage)
        self.assertIn('gt-native-unity-array-import-contract.json',stage)
        self.assertLess(stage.index('scripts.gt_write_unity_array_import_contract'),
                        stage.index('rm -rf -- "$original_owners"'))
        self.assertNotIn("continue-on-error",stage)
        self.assertNotIn("|| true",stage)

    def test_actual_exporter_emits_private_texture_identity_trace_for_class187(self):
        # Without this opt-in, the production CSharp exporter only emits
        # Material and Shader objects. Nine ClassID187 entries are absent,
        # even though the separate GT full AssetRipper smoke succeeds.
        exporter=self.workflow.split("      - name: Export 40 scenes",1)[1].split(
            "      - name: GT verify nine native Texture2DArray",1)[0]
        self.assertIn("RAFT_PRIVATE_EXPORT_LINEAGE:",exporter)
        self.assertIn("RAFT_PRIVATE_EXPORT_TEXTURE_LINEAGE: '1'",exporter)
        self.assertNotIn("continue-on-error",exporter)

    def test_Unity_Editor_really_checks_nine_native_array_assets_from_private_source_contract(self):
        self.assertIn("OriginalTextureArrayImportGuard.Validate();",self.editor)
        self.assertIn("OriginalTextureArrayImportGuard",self.guard)
        self.assertIn("GTOriginalArrayImportContract.json",self.guard)
        self.assertIn("AssetDatabase.TryGetGUIDAndLocalFileIdentifier",self.guard)
        self.assertIn("importedArray.graphicsFormat",self.guard)
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
