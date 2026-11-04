import hashlib
from pathlib import Path
import tempfile
import unittest

from scripts.b37_probe_original_cursor import code_only, scan, classify_first_arguments


class CursorOriginalCallsiteTests(unittest.TestCase):
    def test_literal_and_comments_are_not_executable(self):
        text = ('// Cursor.SetCursor(x,y,z);\n'
                'string s="Cursor.SetCursor(a,b,c)";\n'
                '/* Cursor.SetCursor(q,w,e); */\n'
                'Cursor.SetCursor(cursor, Vector2.zero, CursorMode.Auto);\n')
        live = code_only(text)
        self.assertEqual(live.count('Cursor.SetCursor'), 1)
        self.assertEqual(len(live), len(text))
        self.assertEqual(live.count('\n'), text.count('\n'))

    def test_verbatim_and_char_literals_do_not_inflate(self):
        text = 'string a=@"a "" Cursor.SetCursor()"" ";\nchar c=\'x\';\nUnityEngine.Cursor.SetCursor(x,y,z);'
        live = code_only(text)
        self.assertEqual(live.count('Cursor.SetCursor'), 1)

    def test_classify_nullable_and_live_texture_call_arguments(self):
        source = ('Cursor.SetCursor(null, V2.Zero, CursorMode.Auto);\n'
                  'UnityEngine.Cursor.SetCursor(cursor, center, CursorMode.Auto);\n'
                  'Cursor.SetCursor(CreateTexture(a, b), center, CursorMode.Auto);\n')
        self.assertEqual(classify_first_arguments(code_only(source)), [True, False, False])
        for invalid in ('Cursor.SetCursor();', 'Cursor.SetCursor(x, y);',
                        'Cursor.SetCursor(x, y, z, extra);'):
            with self.assertRaises(ValueError):
                classify_first_arguments(code_only(invalid))

    def test_unknown_unterminated_tokens_fail_closed(self):
        for s in ('/* incomplete', '"incomplete', "'incomplete"):
            with self.assertRaises(ValueError):
                code_only(s)

    def test_authenticated_root_and_privacy(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dll = root / 'original.dll'
            dll.write_bytes(b'original-test')
            src = root / 'csharp'
            src.mkdir()
            (src / 'A.cs').write_text('class A { void Go() { Cursor.SetCursor(a,b,c); } }')
            (src / 'B.cs').write_text('class B { string x="Cursor.SetCursor"; }')
            sha = hashlib.sha256(dll.read_bytes()).hexdigest()
            result = scan(src, dll, size=dll.stat().st_size, sha=sha)
            self.assertEqual(result['direct_cursor_setcursor_calls'], 1)
            self.assertEqual(result['source_files_scanned'], 2)
            self.assertFalse(result['original_csharp_or_paths_published'])
            self.assertNotIn('A.cs', str(result))
            with self.assertRaisesRegex(ValueError, 'SHA mismatch'):
                scan(src, dll, size=dll.stat().st_size, sha='0' * 64)

    def test_symlinked_source_rejected(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dll = root / 'a.dll'
            dll.write_bytes(b'X')
            source = root / 'orig'
            source.mkdir()
            outside = root / 'else.cs'
            outside.write_text('Cursor.SetCursor(a,b,c);')
            (source / 'linked.cs').symlink_to(outside)
            with self.assertRaisesRegex(ValueError, 'Unsafe or oversized'):
                scan(source, dll, size=1, sha=hashlib.sha256(b'X').hexdigest())

    def test_nonmatching_original_dll_fails(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            dll = root / 'missing.dll'
            source = root / 'src'
            source.mkdir()
            with self.assertRaisesRegex(ValueError, 'exact regular'):
                scan(source, dll)


if __name__ == '__main__':
    unittest.main()
