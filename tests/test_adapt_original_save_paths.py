from collections import Counter
import unittest
from scripts.adapt_original_save_paths import adapt, fingerprint, SUFFIX


class SavePathTests(unittest.TestCase):
    def test_path_expression_preserves_literal_and_every_other_source_character(self):
        text = 'var path = root + "World\\\\"; var extension = ".rgd";'
        result = adapt(text, fingerprint(text), Counter({'World\\': 1}))
        self.assertEqual(result.replace(SUFFIX, ''), text)
        self.assertIn('"World\\\\"' + SUFFIX, result)
        self.assertEqual(adapt(result, fingerprint(text), Counter({'World\\': 1})), result)

    def test_comment_and_verbatim_content_are_not_path_expressions(self):
        text = '// "C:\\\\example"\n/* "\\\\" */ var a = @"C:\test"; var b = "\\\\";'
        result = adapt(text, fingerprint(text), Counter({'\\': 1}))
        self.assertEqual(result.count(SUFFIX), 1)

    def test_unknown_source_and_path_inventory_fail(self):
        text = 'var path = "World\\\\";'
        with self.assertRaises(ValueError):
            adapt(text)
        with self.assertRaises(ValueError):
            adapt(text, fingerprint(text), Counter({'Player\\': 1}))

    def test_misplaced_existing_adaptation_fails(self):
        text = 'var path = "World\\\\";'
        with self.assertRaises(ValueError):
            adapt(text + SUFFIX, fingerprint(text), Counter({'World\\': 1}))
