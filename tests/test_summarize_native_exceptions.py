import unittest
from scripts.summarize_native_exceptions import summarize


class ExceptionSummaryTests(unittest.TestCase):
    def test_counts_occurrences_and_only_first_frame_without_source_or_arguments(self):
        result = summarize([
            '2026-10-31T12:00:00Z NullReferenceException: private message\n',
            '2026-10-31T12:00:00Z Tile.OnValidate (Secret value) (at /private/file.cs:4)\n',
            '2026-10-31T12:00:00Z Other.Method ()\n',
            'System.DllNotFoundException: secret path\n',
            '  at Audio.Load (System.String secret)\n'])
        self.assertEqual(result['exception_occurrences'], {'NullReferenceException': 1, 'System.DllNotFoundException': 1})
        self.assertEqual(result['first_stack_method_occurrences'], {'NullReferenceException @ Tile.OnValidate': 1, 'System.DllNotFoundException @ Audio.Load': 1})
        self.assertNotIn('private', str(result))
        self.assertNotIn('Secret', str(result))

    def test_shell_echo_is_not_exception_and_interrupted_stack_is_not_attributed(self):
        result = summarize(['echo NullReferenceException: x', 'NullReferenceException: x', 'ordinary output', 'Wrong.Frame ()'])
        self.assertEqual(result['exception_occurrences'], {'NullReferenceException': 1})
        self.assertEqual(result['first_stack_method_occurrences'], {})

    def test_fixed_categories_do_not_emit_messages(self):
        result = summarize(['Shader error in private shader', 'Error: private data'])
        self.assertEqual(result['diagnostic_pattern_occurrences'], {'shader_error': 1, 'error_prefixed': 1})
