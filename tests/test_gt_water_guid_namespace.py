"""Source-free regression: selected water GUIDs must be unique in Assets.

All files are temporary authored fixtures. No original game or Unity execution.
"""
import json
from pathlib import Path
import tempfile
import unittest

from scripts.verify_water_render_contract import inspect, native_ready, REQUIRED_PASS_COUNT
from scripts.record_documented_water_limitation import check, unmet_conditions

SHADER_GUID = "ab" * 16
COMPUTE_GUID = "cd" * 16
OTHER_GUID = "ef" * 16
RESERVED = ("0" * 32, "0000000000000000e000000000000000",
            "0000000000000000f000000000000000", "0000000deadbeef15deadf00d0000000")
NAME = "UltimateWater/Utilities/FFT Utilities"


class WaterGuidNamespace(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.project = self.root / "Project"
        self.assets = self.project / "Assets"
        self.assets.mkdir(parents=True)
        self.shader = self.assets / "Water.shader"
        self.shader.write_text('Shader "' + NAME + '" { SubShader {\n' +
            "Pass { HLSLPROGRAM\nvoid main() {}\nENDHLSL\n}\n" * REQUIRED_PASS_COUNT[NAME] + "} }\n")
        self.compute = self.assets / "FFT.compute"
        self.compute.write_text("#pragma kernel Horizontal\n[numthreads(8,8,1)]\nvoid Horizontal() {}\n")
        self.meta(self.shader, SHADER_GUID)
        self.meta(self.compute, COMPUTE_GUID)

    def sidecar(self, target):
        return Path(str(target) + ".meta")

    def meta(self, target, guid):
        self.sidecar(target).write_text("fileFormatVersion: 2\nguid: " + guid + "\n")

    def asset(self, name, guid, text="authored fixture"):
        path = self.assets / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)
        self.meta(path, guid)
        return path

    def reject(self, reason):
        with self.assertRaisesRegex(ValueError, reason):
            inspect(self.project)

    def test_texture_collision_case_insensitive(self):
        self.asset("Textures/Color.png", SHADER_GUID.upper())
        self.reject("Duplicate.*water GUID")

    def test_model_collision(self):
        self.asset("Models/WhiteMesh.fbx", COMPUTE_GUID)
        self.reject("Duplicate.*water GUID")

    def test_unselected_shader_collision(self):
        self.asset("Unrelated.shader", SHADER_GUID, 'Shader "Authored/Other" { SubShader {} }')
        self.reject("Duplicate.*water GUID")

    def test_unselected_compute_collision(self):
        self.asset("Unrelated.compute", COMPUTE_GUID, "#pragma kernel Other\n[numthreads(1,1,1)]\nvoid Other() {}\n")
        self.reject("Duplicate.*water GUID")

    def test_folder_collision(self):
        folder = self.assets / "Folder"
        folder.mkdir()
        self.meta(folder, SHADER_GUID)
        self.reject("Duplicate.*water GUID")

    def test_orphan_meta_collision(self):
        self.meta(self.assets / "Missing.asset", COMPUTE_GUID)
        self.reject("Duplicate.*water GUID")

    def test_reserved_selected_identities(self):
        for target, original in ((self.shader, SHADER_GUID), (self.compute, COMPUTE_GUID)):
            for guid in RESERVED:
                with self.subTest(target=target.name, kind=RESERVED.index(guid)):
                    self.meta(target, guid)
                    try:
                        self.reject("Reserved.*GUID")
                    finally:
                        self.meta(target, original)

    def test_ambiguous_unrelated_meta(self):
        target = self.asset("Ambiguous.mat", OTHER_GUID)
        with self.sidecar(target).open("a") as out:
            out.write("guid: " + SHADER_GUID + "\n")
        self.reject("ambiguous.*GUID")

    def test_malformed_unrelated_meta(self):
        self.asset("Broken.asset", "not-a-guid")
        self.reject("Malformed.*GUID")

    def test_oversized_unrelated_meta(self):
        target = self.asset("Large.asset", OTHER_GUID)
        with self.sidecar(target).open("ab") as out:
            out.write(b"x" * (4 * 1024 * 1024))
        self.reject("oversized.*GUID")

    def test_linked_directory_hiding_collision(self):
        outside = self.root / "outside"
        outside.mkdir()
        self.meta(outside / "Hidden.asset", SHADER_GUID)
        (self.assets / "Linked").symlink_to(outside, target_is_directory=True)
        self.reject("linked.*Assets GUID")

    def test_linked_meta_hiding_collision(self):
        target = self.assets / "Linked.asset"
        target.write_text("authored")
        outside = self.root / "outside.meta"
        outside.write_text("guid: " + COMPUTE_GUID + "\n")
        self.sidecar(target).symlink_to(outside)
        self.reject("linked.*Assets GUID")

    def test_redirected_project_ancestor(self):
        alias = self.root / "alias"
        alias.symlink_to(self.root, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "redirected"):
            inspect(alias / "Project")

    def test_acknowledged_limits_cannot_bypass_collision(self):
        request = self.root / "request.json"
        request.write_text(json.dumps({"request_id": "authored-test",
            "documented_water_limitations": unmet_conditions(inspect(self.project))}))
        self.asset("Collision.mat", SHADER_GUID)
        out = self.root / "experimental.json"
        with self.assertRaisesRegex(ValueError, "Duplicate.*water GUID"):
            check(self.project, request, out)
        self.assertFalse(out.exists())

    def test_positive_folder_and_nested_guid_reference(self):
        folder = self.assets / "Folder"
        folder.mkdir()
        self.meta(folder, OTHER_GUID)
        target = self.asset("Folder/Color.png", "12" * 16)
        with self.sidecar(target).open("a") as out:
            out.write("TextureImporter:\n  externalObjects:\n  - reference:\n      guid: " + SHADER_GUID + "\n")
        report = inspect(self.project)
        self.assertTrue(report["shader_contracts"][NAME]["contract_satisfied"])
        self.assertTrue(report["water_compute_source_candidate_present"])
        self.assertFalse(report["authentic_water_kernel_identity_verified"])
        self.assertFalse(native_ready(report))

    def test_missing_selected_sidecars_stay_unmet(self):
        self.sidecar(self.shader).unlink()
        self.sidecar(self.compute).unlink()
        report = inspect(self.project)
        self.assertFalse(report["shader_contracts"][NAME]["contract_satisfied"])
        self.assertFalse(report["water_compute_source_candidate_present"])
        self.assertFalse(native_ready(report))


if __name__ == "__main__":
    unittest.main()
