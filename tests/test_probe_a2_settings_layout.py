"""Synthetic-only private Settings layout scanner checks (never original code)."""
import tempfile
from pathlib import Path
import unittest

from scripts.probe_a2_settings_layout import inspect, relevant, source_sites


class A2SettingsLayoutTests(unittest.TestCase):
    def test_reference_signals_do_not_imply_aspect_cause(self):
        source = '''class GraphicsSettingsBox {
          // Screen.SetResolution(10,10,false);
          string value = "Screen.width CanvasScaler referenceResolution =";
          void Apply(){ Screen.SetResolution(1200, 800, false);
            float w = Screen.width, h = Screen.height;
            scaler.referenceResolution = size;
            scaler.matchWidthOrHeight = match;
            transform.sizeDelta = delta;
            bool unchanged = transform.anchorMin == anchor;
            transform.anchorMax = anchor;
            camera.aspect = ratio;
          }
        }'''
        kinds = [site['category'] for site in source_sites(source)]
        self.assertEqual(kinds.count('screen_set_resolution'), 1)
        self.assertEqual(kinds.count('screen_width_read'), 1)
        self.assertEqual(kinds.count('screen_height_read'), 1)
        self.assertEqual(kinds.count('reference_resolution_write'), 1)
        self.assertEqual(kinds.count('width_or_height_match_write'), 1)
        self.assertEqual(kinds.count('size_delta_write'), 1)
        self.assertEqual(kinds.count('anchor_write'), 1)
        self.assertEqual(kinds.count('camera_aspect_write'), 1)
        self.assertNotIn('1200', str(source_sites(source)))
        self.assertNotIn('ratio', str(source_sites(source)))

    def test_target_scope_prevents_unrelated_gameplay_claims(self):
        self.assertTrue(relevant('Settings.cs'))
        self.assertTrue(relevant('GraphicsSettingsBox.cs'))
        self.assertTrue(relevant('AudioSettingsBox.cs'))
        self.assertTrue(relevant('DynamicResolution.cs'))
        self.assertFalse(relevant('PersonController.cs'))

    def test_read_only_inventory_and_negative_controls(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'Settings.cs').write_text('class Settings { void Open() { var x = Screen.safeArea; } }')
            (root / 'GraphicsSettingsBox.cs').write_text('class GraphicsSettingsBox { void Open() { Screen.SetResolution(1,2,false); } }')
            (root / 'DynamicResolution.cs').write_text('class DynamicResolution { void Tick() { ScalableBufferManager.ResizeBuffers(1,1); } }')
            (root / 'Player.cs').write_text('class Player { void T() { Screen.SetResolution(3,4,false); } }')
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            result = inspect(root, require_pins=False)
            self.assertEqual(result['source_files_examined'], 4)
            self.assertEqual(result['settings_files_examined'], 3)
            self.assertEqual(result['category_counts']['screen_set_resolution'], 1)
            self.assertFalse(result['settings_aspect_cause_proven'])
            self.assertFalse(result['native_or_device_tested'])
            self.assertFalse(result['source_modified'])
            self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})
            with self.assertRaisesRegex(ValueError, 'Authenticated'):
                inspect(root)

    def test_reject_symlink_in_original_source_inventory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'Bad.cs').symlink_to('/etc/passwd')
            with self.assertRaisesRegex(ValueError, 'Unsafe'):
                inspect(root, require_pins=False)


if __name__ == '__main__':
    unittest.main()
