"""T2: exercise the real Foam crosscheck CLI JSON boundary without private data."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import importlib.util

_fixture_path = Path(__file__).with_name("test_t2_foam_pass_crosscheck_original_integration.py")
_spec = importlib.util.spec_from_file_location("t2_original_fixture", _fixture_path)
_fixture = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_fixture)
full_safe_fixture, sites = _fixture.full_safe_fixture, _fixture.sites


class FoamCrosscheckCLIJsonBoundary(unittest.TestCase):
    def run_cli(self, original_text, roles_text):
        with tempfile.TemporaryDirectory() as folder:
            a, b = Path(folder) / "original.json", Path(folder) / "roles.json"
            a.write_text(original_text, encoding="utf-8")
            b.write_text(roles_text, encoding="utf-8")
            return subprocess.run(
                [sys.executable, "-m", "scripts.t2_foam_pass_crosscheck", str(a), str(b)],
                capture_output=True, text=True, check=False,
            )

    def test_valid_full_schema_succeeds(self):
        p = self.run_cli(json.dumps(full_safe_fixture()),
                         json.dumps(sites("RenderTexture", "unknown", "RenderTexture", "unknown")))
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertTrue(json.loads(p.stdout)["independent_summaries_agree"])

    def test_duplicate_original_member_rejected_before_validation(self):
        original = json.dumps(full_safe_fixture())
        original = original[:-1] + ', "status": "forged"}'
        p = self.run_cli(original,
                         json.dumps(sites("RenderTexture", "unknown", "RenderTexture", "unknown")))
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("duplicate_json_key", p.stderr)

    def test_duplicate_nested_role_member_rejected(self):
        roles = '{"sites":[{"pass":0,"source":"RenderTexture","source":"Texture","destination":"RenderTexture"},{"pass":1,"source":"unknown","destination":"unknown"}]}'
        p = self.run_cli(json.dumps(full_safe_fixture()), roles)
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("duplicate_json_key", p.stderr)

    def test_nonfinite_original_member_rejected(self):
        original = json.dumps(full_safe_fixture()).replace('"original_typed_Shader_Find_calls": 81',
                                                            '"original_typed_Shader_Find_calls": NaN')
        p = self.run_cli(original,
                         json.dumps(sites("RenderTexture", "unknown", "RenderTexture", "unknown")))
        self.assertNotEqual(p.returncode, 0)
        self.assertIn("nonfinite_json", p.stderr)


if __name__ == "__main__":
    unittest.main()
