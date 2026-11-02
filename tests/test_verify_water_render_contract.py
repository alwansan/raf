"""Source-only fail-closed tests; no Unity Editor, original assets or LFS."""
from pathlib import Path
import tempfile
import unittest

from scripts.verify_water_render_contract import inspect, REQUIRED_PASS_COUNT


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

    def test_duplicate_original_shader_identifiers_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            assets = Path(temp) / "Assets"
            assets.mkdir()
            name = next(iter(REQUIRED_PASS_COUNT))
            write_shader(assets, name, 6)
            write_shader(assets, name, 6)
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                inspect(Path(temp))


if __name__ == "__main__":
    unittest.main()
