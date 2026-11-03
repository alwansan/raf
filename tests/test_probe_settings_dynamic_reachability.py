"""Synthetic fixtures only; original source is never exposed."""
from pathlib import Path
import tempfile
import unittest
from scripts.probe_settings_dynamic_reachability import inspect


class SettingsGraphTests(unittest.TestCase):
    def test_distinguish_explicit_references_and_mutations(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'GraphicsSettingsBox.cs').write_text('''
                void Apply() { ApplyCurrentResolutionAndFullscreenMode();
                // DynamicResolution.m_widthScale = 0f;
                string x = "DynamicResolution.m_heightScale = 0f";
                }
                ''')
            (root / 'DynamicResolution.cs').write_text('''
                class DynamicResolution {
                static void A() { ScalableBufferManager.ResizeBuffers(1f,1f); }
                }
                ''')
            (root / 'Other.cs').write_text('''
                void T() { DynamicResolution.m_widthScale += 0.1f;
                   DynamicResolution.m_heightScale = 0.6f;
                   var current = DynamicResolution.m_widthScale == 0.6f;
                }
                ''')
            report = inspect(root, require_pins=False)
            self.assertEqual(report['external_qualified_scale_writes'], 2)
            self.assertEqual(report['reference_counts']['dynamic_resize_call'], 1)
            self.assertFalse(report['settings_has_explicit_dynamic_resolution_reference'])
            self.assertFalse(report['full_call_graph_proven'])
            self.assertFalse(report['settings_aspect_cause_proven'])
            self.assertNotIn('0.6f', str(report))

    def test_explicit_settings_reference_is_not_proof_of_causality(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'GraphicsSettingsBox.cs').write_text('class A { void A() { DynamicResolution.Enable(); } }')
            (root / 'DynamicResolution.cs').write_text('class DynamicResolution {}')
            report = inspect(root, require_pins=False)
            self.assertTrue(report['settings_has_explicit_dynamic_resolution_reference'])
            self.assertFalse(report['settings_aspect_cause_proven'])

    def test_reject_pinned_input_drift_and_symlinks(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'GraphicsSettingsBox.cs').write_text('class A {}')
            with self.assertRaisesRegex(ValueError, 'SHA mismatch'):
                inspect(root)
            (root / 'link.cs').symlink_to('/etc/passwd')
            with self.assertRaisesRegex(ValueError, 'Unsafe'):
                inspect(root, require_pins=False)


if __name__ == '__main__':
    unittest.main()
