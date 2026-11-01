import unittest
from scripts.adapt_android_render_lifetimes import protect_temporaries,adapt
class LifetimeTests(unittest.TestCase):
    def test_single_failure_path_has_finally(self):
        s='\tTemporaryRenderTexture temporary = cache.GetTemporary();\n\tWork(temporary);\n\ttemporary.Dispose();\n'
        out=protect_temporaries(s,1)
        self.assertIn('finally',out);self.assertEqual(out.count('Work(temporary);'),1);self.assertEqual(out.count('temporary.Dispose();'),1)
    def test_second_allocation_is_inside_first_finally_scope(self):
        s='\tTemporaryRenderTexture temporary = cache.GetTemporary();\n\tTemporaryRenderTexture temporary2 = cache.GetTemporary();\n\tWork(temporary, temporary2);\n\ttemporary.Dispose();\n\ttemporary2.Dispose();\n'
        out=protect_temporaries(s,2)
        self.assertEqual(out.count('finally'),2)
        self.assertLess(out.index('try'),out.index('TemporaryRenderTexture temporary2'))
        self.assertLess(out.index('temporary2.Dispose();'),out.index('temporary.Dispose();'))
    def test_unknown_revision_and_missing_cleanup_rejected(self):
        with self.assertRaises(ValueError):adapt('Dx11FFT','unknown original')
        with self.assertRaises(ValueError):protect_temporaries('TemporaryRenderTexture temporary = cache.GetTemporary();\nWork();\n',1)
