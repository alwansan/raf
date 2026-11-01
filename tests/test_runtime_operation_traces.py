import hashlib
import unittest
from scripts.instrument_android_runtime_operations import body_bounds, wrap, instrument


class OperationTraceTests(unittest.TestCase):
    def test_braces_inside_strings_and_comments_do_not_close_body(self):
        text = 'void Save() { var s = "}"; /* } */ if (true) { Run(); } } void Other() {}'
        start, end = body_bounds(text, 'void Save()')
        self.assertEqual(text[end:], '} void Other() {}')

    def test_returns_exceptions_and_original_body_remain(self):
        text = 'int Load() { if (x) return 1; throw new System.Exception(); }'
        result = wrap(text, 'int Load()', 'save')
        self.assertIn('if (x) return 1; throw new System.Exception();', result)
        self.assertIn('finally', result)
        self.assertIn('throw;', result)
        self.assertIn('#if UNITY_ANDROID && !UNITY_EDITOR', result)

    def test_unknown_revision_and_duplicate_application_fail(self):
        text = 'void Start() { Run(); }'
        manifest = {'sources': {'Demo': {'sha256': hashlib.sha256(text.encode()).hexdigest(), 'area': 'startup', 'methods': [{'signature': 'void Start()'}]}}}
        result = instrument('Demo', text, manifest)
        with self.assertRaises(ValueError): instrument('Demo', result, manifest)
        with self.assertRaises(ValueError): wrap(text + text, 'void Start()', 'startup')
