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

class AndroidResolutionPolicyTests(unittest.TestCase):
    def test_mouse_one_merge_preserves_original_call_structure_and_desktop_path(self):
        import hashlib
        from unittest.mock import patch
        original='using UnityEngine;\npublic class MyInput : MonoBehaviour {\n'+''.join('Input.'+name+'(key);\n' for name,count in [('GetKey',4),('GetKeyDown',2),('GetKeyUp',2)] for _ in range(count))+'}\n'
        with patch.dict('scripts.adapt_android_render_lifetimes.PINS', {'MyInput':(hashlib.sha256(original.encode()).hexdigest(),0)}):
            changed=adapt('MyInput',original)
        self.assertIn('using RaftAndroidLegacyInput = UnityEngine.Input;',changed)
        self.assertIn('#if UNITY_ANDROID && !UNITY_EDITOR',changed)
        self.assertEqual(changed.count('RaftAndroidLegacyInput.GetKey(key);'),4)
        self.assertEqual(changed.count('RaftAndroidLegacyInput.GetKeyDown(key);'),2)
        self.assertEqual(changed.count('RaftAndroidLegacyInput.GetKeyUp(key);'),2)

    def test_mobile_guard_preserves_original_desktop_body(self):
        import hashlib
        from unittest.mock import patch
        original = '\tpublic void ApplyCurrentResolutionAndFullscreenMode()\n\t{\n\t\tApplyDesktopDisplayMode();\n\t}\n'
        with patch.dict('scripts.adapt_android_render_lifetimes.PINS', {'GraphicsSettingsBox': (hashlib.sha256(original.encode()).hexdigest(), 0)}):
            changed = adapt('GraphicsSettingsBox', original)
        start = changed.index('#if UNITY_ANDROID && !UNITY_EDITOR')
        end = changed.index('#endif', start) + len('#endif\n')
        self.assertEqual(changed[:start] + changed[end:], original)
        self.assertLess(changed.index('return;'), changed.index('ApplyDesktopDisplayMode();'))
