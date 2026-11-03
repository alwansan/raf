"""Synthetic-only negative-control tests; no original proprietary Raft code."""
import tempfile
from pathlib import Path
import unittest

from scripts.probe_a2_controls_layout_context import inspect_text, inspect_root


class A2ControlsLayoutContextTests(unittest.TestCase):
    def test_nested_block_nearest_method_and_same_target(self):
        source = '''class ControlsSettingsBox {
private RectTransform row;
private void UpdateRow() {
    RectTransform row = null;
    if (active) { row.sizeDelta = new Vector2(height, width); }
}
}'''
        result = inspect_text(source, strict_line=False)
        self.assertEqual(result['size_delta_assignment_count'], 1)
        self.assertTrue(result['target_has_local_recttransform_declaration'])
        self.assertEqual(result['target_form'], 'direct_identifier')
        self.assertTrue(result['rhs_uses_new_vector2'])
        self.assertFalse(result['rhs_uses_screen_dimension'])
        self.assertEqual(result['method_explicit_local_invocations'], 0)
        self.assertFalse(result['settings_stretch_cause_proven'])
        self.assertNotIn('height', str(result))
        self.assertNotIn('UpdateRow', str(result))

    def test_comments_strings_comparison_not_executable_writes(self):
        source = '''class A { string x = "rect.sizeDelta = nope";
// row.sizeDelta = something;
void T() { bool x = row.sizeDelta == size; row.sizeDelta = Scale(); }
}'''
        result = inspect_text(source, strict_line=False)
        self.assertEqual(result['size_delta_assignment_count'], 1)
        self.assertFalse(result['rhs_uses_new_vector2'])
        self.assertFalse(result['target_has_local_recttransform_declaration'])
        self.assertFalse(result['source_mutated'])

    def test_source_drift_and_duplicate_writes_rejected(self):
        with self.assertRaisesRegex(ValueError, 'exactly one'):
            inspect_text('class A { void B() { one.sizeDelta = v; two.sizeDelta = x; } }', strict_line=False)
        with self.assertRaisesRegex(ValueError, 'location changed'):
            inspect_text('class A { void B() { one.sizeDelta = v; } }')
        with self.assertRaisesRegex(ValueError, 'enclosing method'):
            inspect_text('class A { object a = (box.sizeDelta = value); }', strict_line=False)

    def test_read_only_pins_and_symlink_input(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            f = root/'ControlsSettingsBox.cs'
            contents='class A { void B() { row.sizeDelta = new Vector2(1,2); } }'
            f.write_text(contents)
            self.assertEqual(inspect_root(root, verify=False)['size_delta_assignment_count'], 1)
            with self.assertRaisesRegex(ValueError, 'SHA256'):
                inspect_root(root, verify=True)
            self.assertEqual(f.read_text(), contents)
            (root/'another').mkdir()
            (root/'another'/'ControlsSettingsBox.cs').write_text(contents)
            with self.assertRaisesRegex(ValueError, 'duplicated'):
                inspect_root(root, verify=False)
            (root/'another'/'ControlsSettingsBox.cs').unlink()
            f.unlink()
            f.symlink_to('/etc/passwd')
            with self.assertRaisesRegex(ValueError, 'Unsafe'):
                inspect_root(root, verify=False)


if __name__ == '__main__':
    unittest.main()
