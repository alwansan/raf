"""Source-free T4 axis/cursor-lock rewrite controls; no original game code included."""
import tempfile
import unittest
from pathlib import Path
from scripts.t4_adapt_original_mouse_axes import replacement_plan, EXPECTED, SHIM


def fixture(root, *, tamper=False):
    for idx in range(4):
        text = ('class Camera%d { void Tick() {\n' % idx
                + '  float a = Input.GetAxis("Mouse X");\n'
                + '  float b = UnityEngine.Input.GetAxisRaw("Mouse Y");\n'
                + ('  Cursor.lockState = (gameplay ? CursorLockMode.Locked : CursorLockMode.None);\n' if idx < 2 else '')
                + '}}\n')
        if tamper and idx == 3:
            text = text.replace('Mouse X', 'Mouse Z')
        (root / ('Camera%d.cs' % idx)).write_text(text)


class MouseOriginalPatchTests(unittest.TestCase):
    def test_exact_counts_and_raw_preservation(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fixture(root)
            changed, counts = replacement_plan(root)
            self.assertEqual(counts, EXPECTED)
            self.assertEqual(len(changed), 4)
            first = changed[root / 'Camera0.cs']
            self.assertIn(SHIM + '.GetAxis("Mouse X")', first)
            self.assertIn(SHIM + '.GetAxisRaw("Mouse Y")', first)
            self.assertIn(SHIM + '.ApplyCursorLock((gameplay ? CursorLockMode.Locked : CursorLockMode.None));', first)
            self.assertIn('class Camera0', first)
            self.assertIn('Cursor.lockState', (root / 'Camera0.cs').read_text()) # no apply
            self.assertNotIn(SHIM, (root / 'Camera0.cs').read_text())

    def test_unexpected_site_is_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fixture(root, tamper=True)
            with self.assertRaises(ValueError):
                replacement_plan(root)

    def test_comment_spoof_cannot_pass_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fixture(root)
            fake = root / "Fake.cs"
            fake.write_text('/* Input.GetAxis("Mouse X"); Cursor.lockState = CursorLockMode.Locked; */\n'
                            '// Input.GetAxis("Mouse Y");\n')
            _, counts = replacement_plan(root)
            self.assertEqual(counts, EXPECTED)

    def test_source_symlink_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fixture(root)
            (root / "Linked.cs").symlink_to(root / 'Camera0.cs')
            with self.assertRaises(ValueError):
                replacement_plan(root)

    def test_double_patch_cannot_silently_reapply(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            fixture(root)
            patches, _ = replacement_plan(root)
            for path, text in patches.items():
                path.write_text(text)
            with self.assertRaises(ValueError):
                replacement_plan(root)

    def test_assets_filter_prevents_sdk_rewrite(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            original = root / 'Scripts' / 'Assembly-CSharp'
            original.mkdir(parents=True)
            fixture(original)
            vendor = root / 'ThirdParty'
            vendor.mkdir()
            (vendor / 'Vendor.cs').write_text('Input.GetAxis("Mouse X");')
            changed, counts = replacement_plan(root, project_assets=True)
            self.assertEqual(counts, EXPECTED)
            self.assertEqual(len(changed), 4)
            self.assertNotIn(vendor / 'Vendor.cs', changed)

    def test_no_missing_input_silently_passes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "Camera.cs").write_text('class Camera {}')
            with self.assertRaises(ValueError):
                replacement_plan(root)


if __name__ == "__main__":
    unittest.main()
