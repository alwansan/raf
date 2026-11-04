"""Source-only fail-closed tests; no Unity Editor, original assets or LFS."""
from pathlib import Path
import tempfile
import unittest

from scripts.verify_water_render_contract import inspect, native_ready, REQUIRED_PASS_COUNT


def write_shader(assets, name, passes, program=True):
    filename = "source_" + str(len(list(assets.rglob("*.shader")))) + ".shader"
    source = 'Shader "' + name + '" { SubShader {\n'
    source += "Pass { CGPROGRAM\nvoid main() {}\nENDCG\n}\n" if program else "Pass { /* empty placeholder */ }\n"
    source += "Pass { CGPROGRAM\nvoid main() {}\nENDCG\n}\n" * (passes - 1)
    source += "} }\n"
    path = assets / filename
    path.write_text(source)
    Path(str(path) + ".meta").write_text("guid: " + str(len(list(assets.rglob("*.shader")))).zfill(32))
    return path


class WaterRenderGateTests(unittest.TestCase):
    def test_exact_observed_passes_and_water_kernel_are_required(self):
        with tempfile.TemporaryDirectory() as temp:
            project = Path(temp)
            assets = project / "Assets"
            assets.mkdir()
            for name, count in REQUIRED_PASS_COUNT.items():
                write_shader(assets, name, count)
            source = assets / "FFT.compute"
            source.write_text("#pragma kernel Horizontal\n[numthreads(8,8,1)]\nvoid Horizontal() {}\n")
            Path(str(source) + ".meta").write_text("guid: " + "a"*32)
            result = inspect(project)
            self.assertTrue(result["all_logged_shader_pass_requirements_satisfied"])
            self.assertTrue(result["water_compute_source_candidate_present"])
            self.assertFalse(result["authentic_water_kernel_identity_verified"])
            self.assertFalse(result["device_execution_verified"])
            # A source-identical-looking test asset is not authenticated
            # Raft water content. Reject it in the actual native gate.
            self.assertFalse(native_ready(result))
            self.assertFalse(result["modified_source"])

    def test_single_pass_exports_fail_for_all_multi_pass_programs(self):
        with tempfile.TemporaryDirectory() as temp:
            assets = Path(temp) / "Assets"
            assets.mkdir()
            for name in REQUIRED_PASS_COUNT:
                write_shader(assets, name, 1)
            result = inspect(Path(temp))
            self.assertFalse(result["all_logged_shader_pass_requirements_satisfied"])
            self.assertEqual(len(result["shader_contracts"]), len(REQUIRED_PASS_COUNT))
            self.assertFalse(result["water_compute_source_candidate_present"])
            self.assertFalse(native_ready(result))

    def test_source_names_and_comments_cannot_fake_a_real_pass_or_program(self):
        with tempfile.TemporaryDirectory() as temp:
            assets = Path(temp) / "Assets"
            assets.mkdir()
            name = next(iter(REQUIRED_PASS_COUNT))
            p = write_shader(assets, name, 1, program=False)
            with p.open("a") as out:
                out.write("/* Pass { CGPROGRAM } */\n// Pass { HLSLPROGRAM\n")
            result = inspect(Path(temp))
            self.assertFalse(result["shader_contracts"][name]["contract_satisfied"])

    def test_commented_compute_kernel_is_not_a_candidate(self):
        with tempfile.TemporaryDirectory() as temp:
            assets = Path(temp) / "Assets"
            assets.mkdir()
            source = assets / "FFT.compute"
            source.write_text("/*\n#pragma kernel Fake\n*/\n")
            Path(str(source) + ".meta").write_text("guid: " + "a"*32)
            result = inspect(Path(temp))
            self.assertEqual(result["compute_files_with_kernels"], 0)
            self.assertFalse(result["water_compute_source_candidate_present"])

    def test_duplicate_original_shader_identifiers_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            assets = Path(temp) / "Assets"
            assets.mkdir()
            name = next(iter(REQUIRED_PASS_COUNT))
            write_shader(assets, name, 6)
            write_shader(assets, name, 6)
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                inspect(Path(temp))


    def test_rejects_external_assets_root_symlink(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "project").mkdir()
            (root / "outside").mkdir()
            (root / "project" / "Assets").symlink_to(root / "outside", target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "redirected"):
                inspect(root / "project")

    def test_rejects_linked_project_root(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "real" / "Assets").mkdir(parents=True)
            (root / "redirected-project").symlink_to(root / "real", target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "redirected"):
                inspect(root / "redirected-project")

    def test_rejects_external_shader_meta_instead_of_counting_it(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            assets = root / "Assets"
            assets.mkdir()
            name = next(iter(REQUIRED_PASS_COUNT))
            shader = write_shader(assets, name, REQUIRED_PASS_COUNT[name])
            external = root / "external.meta"
            external.write_text("guid: " + "f" * 32)
            meta = Path(str(shader) + ".meta")
            meta.unlink()
            meta.symlink_to(external)
            with self.assertRaisesRegex(ValueError, "linked"):
                inspect(root)

    def test_rejects_external_compute_meta_instead_of_counting_it(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            assets = root / "Assets"
            assets.mkdir()
            source = assets / "FFT.compute"
            source.write_text("#pragma kernel Horizontal\\n[numthreads(8,8,1)]\\nvoid Horizontal() {}\\n")
            external = root / "outside.meta"
            external.write_text("guid: " + "b" * 32)
            Path(str(source) + ".meta").symlink_to(external)
            with self.assertRaisesRegex(ValueError, "linked"):
                inspect(root)

    def test_absent_unlinked_sidecar_remains_unmet_not_forged(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            assets = root / "Assets"
            assets.mkdir()
            name = next(iter(REQUIRED_PASS_COUNT))
            shader = write_shader(assets, name, REQUIRED_PASS_COUNT[name])
            Path(str(shader) + ".meta").unlink()
            result = inspect(root)
            self.assertFalse(result["shader_contracts"][name]["contract_satisfied"])
            self.assertFalse(result["shader_contracts"][name]["observed"]["original_meta_present"])


    def test_b13_rejects_malformed_water_shader_metadata_guid(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            assets = root / "Assets"
            assets.mkdir()
            name = next(iter(REQUIRED_PASS_COUNT))
            shader = write_shader(assets, name, REQUIRED_PASS_COUNT[name])
            meta = Path(str(shader) + ".meta")
            meta.write_text("guid: not-a-32-character-unity-identity\n")
            with self.assertRaisesRegex(ValueError, "Malformed.*GUID"):
                inspect(root)

    def test_b13_rejects_duplicate_water_shader_guid_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            assets = root / "Assets"
            assets.mkdir()
            names = list(REQUIRED_PASS_COUNT)[:2]
            first = write_shader(assets, names[0], REQUIRED_PASS_COUNT[names[0]])
            second = write_shader(assets, names[1], REQUIRED_PASS_COUNT[names[1]])
            Path(str(second) + ".meta").write_bytes(Path(str(first) + ".meta").read_bytes())
            with self.assertRaisesRegex(ValueError, "Duplicate.*GUID"):
                inspect(root)

    def test_b13_rejects_duplicate_shader_and_water_compute_guid_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            assets = root / "Assets"
            assets.mkdir()
            name = next(iter(REQUIRED_PASS_COUNT))
            shader = write_shader(assets, name, REQUIRED_PASS_COUNT[name])
            compute = assets / "FFT.compute"
            compute.write_text("#pragma kernel Horizontal\n[numthreads(8,8,1)]\nvoid Horizontal() {}\n")
            Path(str(compute) + ".meta").write_bytes(Path(str(shader) + ".meta").read_bytes())
            with self.assertRaisesRegex(ValueError, "Duplicate.*GUID"):
                inspect(root)

    def test_b13_rejects_ambiguous_water_compute_guid_fields(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            assets = root / "Assets"
            assets.mkdir()
            compute = assets / "FFT.compute"
            compute.write_text("#pragma kernel Horizontal\n[numthreads(8,8,1)]\nvoid Horizontal() {}\n")
            Path(str(compute) + ".meta").write_text(
                "guid: " + "a"*32 + "\nguid: " + "b"*32 + "\n"
            )
            with self.assertRaisesRegex(ValueError, "ambiguous.*GUID"):
                inspect(root)


if __name__ == "__main__":
    unittest.main()
