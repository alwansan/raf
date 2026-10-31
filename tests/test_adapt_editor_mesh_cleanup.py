import unittest
from scripts.adapt_editor_mesh_cleanup import adapt, fingerprint, GUARD


class SourceSafetyTests(unittest.TestCase):
    # Synthetic callback, not original game source.
    SOURCE = 'class Fixture { private void OnDestroy() { Record(42); } }'

    def test_insertion_preserves_every_original_character(self):
        result = adapt(self.SOURCE, fingerprint(self.SOURCE))
        self.assertEqual(result.replace(GUARD, '', 1), self.SOURCE)
        self.assertEqual(adapt(result, fingerprint(self.SOURCE)), result)

    def test_unknown_original_refused(self):
        with self.assertRaises(ValueError):
            adapt(self.SOURCE)

    def test_changed_existing_guard_refused(self):
        result = adapt(self.SOURCE, fingerprint(self.SOURCE))
        with self.assertRaises(ValueError):
            adapt(result.replace('!SkipGC', 'SkipGC'), fingerprint(self.SOURCE))

    def test_changed_original_body_refused(self):
        result = adapt(self.SOURCE, fingerprint(self.SOURCE))
        with self.assertRaises(ValueError):
            adapt(result.replace('Record(42)', 'Record(0)'), fingerprint(self.SOURCE))

    def test_ambiguous_callback_refused(self):
        source = self.SOURCE + self.SOURCE
        with self.assertRaises(ValueError):
            adapt(source, fingerprint(source))


if __name__ == '__main__':
    unittest.main()
