"""Synthetic-only C# display mutation fixtures; no original Raft source."""
import tempfile
from pathlib import Path
import unittest
from scripts.probe_original_android_display_paths import inspect_source, mask_csharp_noncode, probe


class DisplayMutationProbeTests(unittest.TestCase):
    def test_actual_mutators_distinguished_from_reads_and_comments(self):
        source = '''class GraphicsSettingsBox {
 // Screen.SetResolution(1, 1, true);
 string example = "Screen.fullScreen = false";
 void Apply() { Screen.SetResolution(1280, 720, false); }
 void NoChange() { bool old = Screen.fullScreen == true; }
 void Change() { UnityEngine.Screen.fullScreenMode = mode; }
 /* Screen.orientation = ScreenOrientation.Portrait; */
 void Rotate() { Screen.orientation = desired; }
 }'''
        self.assertEqual([x['category'] for x in inspect_source(source)],
                         ['screen_set_resolution', 'screen_fullscreen_mode_assignment', 'screen_orientation_assignment'])
        self.assertEqual(len(mask_csharp_noncode(source)), len(source))
        self.assertEqual(mask_csharp_noncode(source).count('\n'), source.count('\n'))

    def test_verbatim_interpolated_and_char_literals_are_not_calls(self):
        source = '''var a = @"Screen.SetResolution(1,2,3)";
var b = $@"Screen.orientation = Portrait;";
var c = '\\'';
ScalableBufferManager.ResizeBuffers(0.5f, 0.5f);'''
        self.assertEqual([x['category'] for x in inspect_source(source)], ['scalable_buffer_resize'])

    def test_scalable_buffer_arguments_are_compared_without_source_output(self):
        source = ('ScalableBufferManager.ResizeBuffers(scale, scale);\n'
                  'ScalableBufferManager.ResizeBuffers(width, height);\n'
                  'ScalableBufferManager.ResizeBuffers(Mathf.Clamp(x, 0, 1), Mathf.Clamp(x, 0, 1));\n'
                  'ScalableBufferManager.ResizeBuffers(Mix(a, b), Mix(a, c));')
        values = [site['xy_arguments_syntactically_identical'] for site in inspect_source(source)]
        self.assertEqual(values, [True, False, True, False])
        self.assertNotIn('Mathf.Clamp', str(inspect_source(source)))

    def test_read_only_inventory_and_source_revision(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'GraphicsSettingsBox.cs').write_text('class A { void X() { Screen.SetResolution(1,2,false); } }')
            (root / 'Other.cs').write_text('class B { void X() { Display.main.SetRenderingResolution(1,2); } }')
            before = [(p.name, p.read_bytes()) for p in root.glob('*.cs')]
            report = probe(root)
            self.assertEqual(report['mutation_sites'], 2)
            self.assertEqual(report['source_files_examined'], 2)
            self.assertFalse(report['graphics_settings_only_assumption_verified'])
            self.assertFalse(report['source_modified'])
            self.assertFalse(report['unity_or_device_tested'])
            self.assertNotIn('class A', str(report))
            self.assertEqual(before, [(p.name, p.read_bytes()) for p in root.glob('*.cs')])

    def test_refuse_unsafe_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / 'x.cs').symlink_to('/etc/passwd')
            with self.assertRaisesRegex(ValueError, 'Unsafe'):
                probe(root)


if __name__ == '__main__':
    unittest.main()
