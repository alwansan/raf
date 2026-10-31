from pathlib import Path
import tempfile
import unittest
from scripts.recover_empty_ilspy_sources import recover


class EmptyOriginalSourceTests(unittest.TestCase):
    def test_exact_original_is_recovered_without_changing_meta_or_nonempty_code(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'A.cs').write_text('')
            (root / 'A.cs.meta').write_bytes(b'original-guid')
            (root / 'B.cs').write_text('class B { public int Value = 3; }')
            report = recover(root, {('', 'A'): ['A']}, lambda name: 'public class A { public int Value = 7; }')
            self.assertEqual(report['focused_original_sources_recovered'], 1)
            self.assertEqual((root / 'A.cs.meta').read_bytes(), b'original-guid')
            self.assertIn('Value = 3', (root / 'B.cs').read_text())

    def test_ambiguous_original_identity_refuses_all_writes(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for name in ('A', 'B'):
                (root / (name + '.cs')).write_text('')
            with self.assertRaises(ValueError):
                recover(root, {('', 'A'): ['A'], ('', 'B'): ['B', 'B`1']}, lambda name: 'class A {}')
            self.assertEqual((root / 'A.cs').read_text(), '')

    def test_wrong_type_or_namespace_is_refused(self):
        for body in ('class Other {}', 'namespace Wrong { class A {} }'):
            with tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                (root / 'A.cs').write_text('')
                with self.assertRaises(ValueError):
                    recover(root, {('', 'A'): ['A']}, lambda name: body)
                self.assertEqual((root / 'A.cs').read_text(), '')

    def test_nonempty_originals_never_trigger_replacement(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            (root / 'A.cs').write_text('class A {}')
            report = recover(root, {}, lambda name: self.fail('Should not decompile a nonempty source'))
            self.assertEqual(report['focused_original_sources_recovered'], 0)
