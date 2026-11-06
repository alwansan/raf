"""Synthetic CLI and live native pipeline contract for B46 texture links."""
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from tests.test_verify_exported_material_texture_links import material

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / ".github/workflows/raft-unity-editor-android-import.yml"
MARKER = "RAFT_B46_TEXTURE_LINKS "

class NativeMaterialTextureIntegration(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name) / "ExportedProject"
        assets = self.root / "Assets"
        assets.mkdir(parents=True)
        self.mat = assets / "m.mat"
        self.mat.write_text(material("{fileID: 2800000, guid: " + "b"*32 + ", type: 3}"))
        (assets / "m.mat.meta").write_text("guid: " + "a"*32 + "\nNativeFormatImporter:\n")
        (assets / "t.png").write_bytes(b"synthetic fixture only")
        (assets / "t.png.meta").write_text("guid: " + "b"*32 + "\nTextureImporter:\n")

    def cli(self):
        run = subprocess.run([sys.executable, "-m",
            "scripts.verify_exported_material_texture_links",
            "--project", str(self.root)], cwd=ROOT,
            capture_output=True, text=True, timeout=15, check=False)
        self.assertTrue(run.stdout.startswith(MARKER), run.stderr)
        payload = json.loads(run.stdout[len(MARKER):])
        for forbidden in (str(self.root), "m.mat", "t.png", "a"*32, "b"*32, "c"*32):
            self.assertNotIn(forbidden, run.stdout)
        return run, payload

    def test_real_cli_valid_texture_witness(self):
        proc, payload = self.cli()
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(payload["status"], "PASS")
        self.assertEqual(payload["texture_slots"], 1)
        self.assertEqual(payload["resolved_local_texture_refs"], 1)
        self.assertFalse(payload["ready_for_build"])
        self.assertFalse(payload["device_render_verified"])

    def test_real_cli_invalid_texture_is_reported_not_silenced(self):
        self.mat.write_text(material(
            "{fileID: 2800000, guid: " + "c"*32 + ", type: 3}"))
        proc, payload = self.cli()
        self.assertEqual(proc.returncode, 2, proc.stderr)
        self.assertEqual(payload["status"], "REJECTED")
        self.assertEqual(payload["error_code"], "missing_texture_guid")
        self.assertFalse(payload["ready_for_build"])

    def test_production_workflow_retains_postrestorer_witness(self):
        raw = NATIVE.read_text()
        label = "      - name: T5 inspect actual postrestorer Material-to-Texture references (non-mutating)"
        self.assertEqual(raw.count(label), 1)
        start = raw.index(label)
        end = raw.index("      - name:", start + len(label))
        stage = raw[start:end]
        self.assertIn("continue-on-error: true", stage)
        self.assertIn("set -euo pipefail", stage)
        self.assertIn("python3 -m scripts.verify_exported_material_texture_links", stage)
        self.assertIn('--project "$RUNNER_TEMP/project/ExportedProject"', stage)
        self.assertIn('| tee "$RUNNER_TEMP/t5-native-material-texture-links.txt"', stage)
        self.assertNotIn("--repair", stage)
        self.assertLess(raw.index("Restore exact-name Unity 2021.3.45f2 built-in"), start)
        self.assertLess(raw.index("T3 audit actual post-restoration"), start)
        self.assertLess(start, raw.index("Authentic water gate (strict)"))
        evidence = raw.index("      - name: Retain aggregate Material and water diagnostic evidence on prebuild failure")
        retained = raw[evidence:raw.index("      - name:", evidence + 10)]
        self.assertIn("if: always()", retained)
        self.assertIn("actions/upload-artifact@v4", retained)
        self.assertEqual(retained.count("${{ runner.temp }}/t5-native-material-texture-links.txt"), 1)

    def test_source_ci_tracks_native_workflow_wiring(self):
        raw = (ROOT / ".github/workflows/raft-b46-render-texture-links.yml").read_text()
        self.assertIn("- .github/workflows/raft-unity-editor-android-import.yml", raw)
        self.assertIn("- tests/test_t5_native_material_texture_integration.py", raw)
        self.assertIn("test_t5_native_material_texture_integration.py -v", raw)

if __name__ == "__main__":
    unittest.main()
