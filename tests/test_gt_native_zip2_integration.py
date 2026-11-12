"""GT: structural safety gates for the *real* native AssetRipper ZIP2 intake.

Never triggers the full Android build; validates that the production YAML still
uses the SHA-pinned transient originals for every graphics dependency.
"""
from __future__ import annotations

from pathlib import Path
import re
import unittest


WORKFLOW=Path(__file__).resolve().parents[1]/".github/workflows/raft-unity-editor-android-import.yml"


class NativeSourceIntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text=WORKFLOW.read_text(encoding="utf-8")

    def test_full_source_sparse_checkout_is_pinned_without_lfs(self):
        text=self.text
        self.assertIn("ref: 15964ea8f246b6e076ce26b60931ee2e1a9a2385",text)
        block=text.split("- name: Read pinned ZIP2 provider without LFS",1)[1].split(
            "- name: Authenticate ZIP2 owners",1)[0]
        self.assertIn("lfs: false",block)
        self.assertIn("sparse-checkout-cone-mode: false",block)
        self.assertIn("/Raft/Raft_Data/**",block)

    def test_full_graphics_are_materialized_into_exporter_input_twice_checked(self):
        text=self.text
        self.assertEqual(len(re.findall(r"python3 -m scripts\.gt_zip2_export_resources",text)),2)
        for start in (
            "GT restore every original mesh and texture stream into AssetRipper input from ZIP2",
            "GT freeze SHA-pinned original Unity input",
        ):
            body=text.split("- name: "+start,1)[1].split("\n      - name: ",1)[0]
            self.assertIn("--zip2-checkout zip2-original",body)
            self.assertIn("--profile full",body)
            self.assertIn("--byte-budget 10000000000",body)
        self.assertIn("original_resources_verified']==134",text)
        self.assertIn("files_verified_and_reused']==134",text)
        self.assertNotIn("python3 -m scripts.hydrate_render_payloads --apply",text)

    def test_original_streams_drive_compute_texture_mesh_and_wrapper(self):
        text=self.text
        self.assertIn('scripts.audit_texture_stream_coverage --root "$RUNNER_TEMP/input/Raft_Data"',text)
        self.assertIn('scripts.audit_original_compute_metadata --source "$RUNNER_TEMP/input/Raft_Data"',text)
        self.assertIn('scripts/audit_mesh_stream_dependencies.py --root "$RUNNER_TEMP/input/Raft_Data"',text)
        self.assertIn('scripts.w1_build_depth_wrapper --source "$RUNNER_TEMP/input/Raft_Data"',text)
        mesh=text.split("- name: Restore pinned Mesh ranges from full local ZIP2-authenticated streams only",1)[1].split(
            "\n      - uses: ",1)[0]
        self.assertIn('--source-root "$RUNNER_TEMP/input/Raft_Data"',mesh)
        self.assertNotIn("GH_TOKEN:",mesh)
        self.assertNotIn("git lfs",mesh.lower().replace("# no gh_token or git lfs fallback is available to this restoration.",""))
        self.assertIn("scripts.inline_verified_mesh_ranges",mesh)
        self.assertIn("scripts.audit_original_mesh_positions",mesh)

    def test_native_resource_request_gate_unchanged(self):
        text=self.text
        self.assertIn("native-request-gate:",text)
        self.assertIn("test \"$NATIVE_REQUESTED\" = \"true\"",text)
        self.assertIn("cancel-in-progress: false",text)
        self.assertNotIn("[raft-native-build]",text.split("on:",1)[1].split("jobs:",1)[0])


if __name__=="__main__":
    unittest.main()
