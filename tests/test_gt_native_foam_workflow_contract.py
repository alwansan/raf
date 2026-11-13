"""GT: no-fake-pass source-only production Foam stage ordering and safety contract."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
WORKFLOW=ROOT/".github/workflows/raft-unity-editor-android-import.yml"

class OriginalFoamNativeIntegrationContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.flow=WORKFLOW.read_text(encoding="utf-8")

    def test_source_authentic_two_pass_foam_after_spectrum_before_material_audit(self):
        names=re.findall(r"^\s{6}- name: (.+)$", self.flow, re.M)
        spectrum="GT recover original SHA-backed 7Pass Spectrum with two keyword variants and replace only its unique original exported GUID"
        foam="GT restore original Foam Global two-pass source shader into unique exported GUID"
        inventory="Inventory actual exported Material Shader references without modifying assets"
        self.assertEqual(names.count(spectrum),1)
        self.assertEqual(names.count(foam),1)
        self.assertLess(names.index(spectrum),names.index(foam))
        self.assertLess(names.index(foam),names.index(inventory))

    def test_original_zip2_only_four_stage_private_source_and_existing_guid(self):
        begin=self.flow.index("      - name: GT restore original Foam Global")
        end=self.flow.index("      - name: Inventory actual exported Material")
        code=self.flow[begin:end]
        for snippet in (
            'original="$RUNNER_TEMP/w1-original/Raft_Data"',
            'test -s "$original/sharedassets0.assets"',
            "scripts.b20_private_foam_packet",
            "scripts.t2_foam_private_shaderlab_candidate",
            "scripts.t2_foam_private_installer",
            '--source-stage-report "$foam/candidate-safe.json"',
            '--project "$RUNNER_TEMP/project/ExportedProject"',
            '--expected-candidate-sha256 "$original_foam_sha"',
            "assert r['unique_original_foam_exported_target_installed']==1",
            "assert r['original_export_meta_bytes_unchanged'] is True",
            "assert r['original_Material_CB0_runtime_binding_verified'] is False",
            "assert r['Android_water_pixels_verified'] is False",
        ):
            self.assertIn(snippet,code)
        self.assertNotIn("git lfs pull",code.lower())
        self.assertNotIn("git lfs fetch",code.lower())
        self.assertNotIn("guid: ",code.lower())

    def test_cleanup_and_only_numeric_safe_receipt_uploaded(self):
        start=self.flow.index("      - name: GT restore original Foam Global")
        end=self.flow.index("      - name: Recover original Particle108 ShaderLab")
        block=self.flow[start:end]
        self.assertEqual(block.count("actions/upload-artifact@v4"),1)
        self.assertIn('rm -rf -- "$RUNNER_TEMP/gt-native-foam-private"',block)
        upload=block.split("      - name: Retain only safe Foam")[1].split(
            "      - name: Remove private original Foam")[0]
        self.assertIn("gt-native-original-foam-install-safe.json",upload)
        for forbidden in ("*.shader","*.hlsl","packet.json","candidate-safe.json"):
            self.assertNotIn(forbidden,upload)

    def test_native_synthetic_foam_installer_and_source_tests_before_build(self):
        for pattern in ("test_t2_foam_private_installer.py",
                        "test_t2_foam_private_shaderlab_candidate.py"):
            self.assertIn("python3 -m unittest discover -s tests -p "+pattern,self.flow)

if __name__=="__main__":
    unittest.main()
