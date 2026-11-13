"""GT source-only safeguard: full native stage uses exact exported GUID Spectrum and source ZIP2."""
from pathlib import Path
import re
import unittest

ROOT=Path(__file__).resolve().parent.parent
FLOW=ROOT/".github/workflows/raft-unity-editor-android-import.yml"


class NativeSpectrumWorkflowContract(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.source=FLOW.read_text(encoding="utf-8")
        cls.steps=re.findall(r"^\s{6}- name: (.+)$",cls.source,re.M)

    def test_real_full_native_reconstruct_contains_exact_stage_in_order(self):
        labels=self.steps
        selected=[x for x in labels if x.startswith("GT recover original SHA-backed 7Pass")]
        self.assertEqual(len(selected),1)
        stage=selected[0]
        self.assertLess(labels.index("Stage B45 authenticated original two-pass Blur only if exact imported shader identity is found"),
                        labels.index(stage))
        self.assertLess(labels.index(stage),
                        labels.index("Inventory actual exported Material Shader references without modifying assets"))
        self.assertIn("GT original",self.source)

    def test_same_authentic_original_owner_and_real_export_without_guid_fabrication(self):
        text=self.source
        start=text.index("      - name: GT recover original SHA-backed 7Pass")
        end=text.index("      - name: Inventory actual exported Material Shader references")
        block=text[start:end]
        for snippet in (
            'original="$RUNNER_TEMP/w1-original/Raft_Data"',
            'scripts.b09_stage_original_spectrum',
            'scripts.gt_spectrum_original_pass_states',
            'scripts.gt_spectrum_original_private_seven_pass_shaderlab',
            '--source-authentic-resource-names',
            'scripts.gt_spectrum_private_keyword_routed_shaderlab',
            'scripts.gt_install_original_spectrum',
            '--project "$RUNNER_TEMP/project/ExportedProject"',
            '--source-proof "$work/router.json"',
            '--backup "$RUNNER_TEMP/gt-original-spectrum-export-backup"',
            '--out "$RUNNER_TEMP/gt-native-spectrum-install-safe.json" --apply',
            "assert r['exported_target_unique_GUID'] is True",
            "assert r['exported_original_meta_preserved'] is True",
        ):
            self.assertIn(snippet,block)
        self.assertNotIn("git lfs pull",block.lower())
        self.assertNotIn("guid: ",block.lower())

    def test_private_program_bytes_not_uploaded_and_are_scrubbed(self):
        start=self.source.index("      - name: GT recover original SHA-backed 7Pass")
        end=self.source.index("      - name: Inventory actual exported Material Shader references")
        block=self.source[start:end]
        self.assertEqual(block.count("actions/upload-artifact@v4"),1)
        self.assertIn("gt-native-spectrum-install-safe.json",block)
        self.assertIn('rm -rf -- "$RUNNER_TEMP/gt-native-spectrum-private"',block)
        upload=block.split("      - name: Retain only safe GT Spectrum production staging receipts")[1].split(
            "      - name: Destroy private original Spectrum")[0]
        self.assertNotIn("*.shader",upload)
        self.assertNotIn("packet",upload)
        self.assertNotIn("original-spectrum-",upload)

    def test_native_unit_test_gate_before_source(self):
        self.assertIn("unittest discover -s tests -p test_gt_install_original_spectrum.py",self.source)
        self.assertIn("if: always()",self.source)


if __name__=="__main__":
    unittest.main()
