import unittest
from scripts.adapt_android_render_lifetimes import protect_temporaries,adapt,isolate_player_start_fmod,isolate_audio_settings_vca
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
    def test_mouse_zero_merge_preserves_original_call_structure_and_desktop_path(self):
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


class WorldSceneAudioIsolationTests(unittest.TestCase):
    def test_only_missing_fmod_scene_event_is_isolated_on_android(self):
        import hashlib
        from unittest.mock import patch
        original = ('class SoundManager {\n'
                    '    private void OnSceneEvent(int sceneEvent)\n'
                    '    {\n'
                    '        FMODUnity.StudioEventEmitter sound = emitter;\n'
                    '        sound.Play();\n'
                    '        UpdateSceneAudioState();\n'
                    '    }\n'
                    '}\n')
        with patch.dict('scripts.adapt_android_render_lifetimes.PINS',
                        {'SoundManager': (hashlib.sha256(original.encode()).hexdigest(), 0)}):
            result = adapt('SoundManager', original)
        self.assertIn('catch (FMODUnity.EventNotFoundException __raftMissingSceneSound)', result)
        self.assertIn('"scene_event_missing_fmod_event"', result)
        self.assertNotIn('catch (System.Exception', result)
        self.assertEqual(result.count('sound.Play();'), 1)
        self.assertEqual(result.count('UpdateSceneAudioState();'), 1)
        original_body = original[original.index('sound.Play();'):original.index('    }\n')]
        self.assertIn(original_body, result)

    def test_unexpected_original_callback_shape_is_rejected(self):
        import hashlib
        from unittest.mock import patch
        original = ('class SoundManager {\n'
                    '    private void OnSceneEvent(int code) { MissingEmitter(); }\n'
                    '}\n')
        with patch.dict('scripts.adapt_android_render_lifetimes.PINS',
                        {'SoundManager': (hashlib.sha256(original.encode()).hexdigest(), 0)}):
            with self.assertRaisesRegex(ValueError, 'original FMOD scene callback contract changed|Original FMOD scene callback contract changed'):
                adapt('SoundManager', original)


class PlayerAudioInitializationTests(unittest.TestCase):
    def test_exact_two_original_player_events_are_guarded_without_skipping_settings(self):
        import hashlib
        from unittest.mock import patch
        original = (
            "class PersonController {\n"
            "    private void Start()\n"
            "    {\n"
            "        soundA = RuntimeManager.CreateInstance(eventOne);\n"
            "        soundB = RuntimeManager.CreateInstance(eventTwo);\n"
            "        settings = RestoreSettings();\n"
            "        actionMove = CreateMovement();\n"
            "    }\n"
            "}\n"
        )
        with patch.dict('scripts.adapt_android_render_lifetimes.PINS',
                        {'PersonController': (hashlib.sha256(original.encode()).hexdigest(), 0)}):
            result = adapt('PersonController', original)
        self.assertEqual(result.count("catch (FMODUnity.EventNotFoundException __raftMissingPlayerSound)"), 2)
        self.assertEqual(result.count("player_start_missing_fmod_event"), 2)
        self.assertEqual(result.count("RuntimeManager.CreateInstance("), 2)
        self.assertEqual(result.count("settings = RestoreSettings();"), 1)
        self.assertEqual(result.count("actionMove = CreateMovement();"), 1)
        self.assertLess(result.index("soundA = "), result.index("settings = "))
        self.assertNotIn("catch (System.Exception", result)
        self.assertNotIn("WorldHasBeenRecieved", result)
        self.assertNotIn("return;", result)

    def test_broken_call_shape_or_changed_initialization_order_fails_closed(self):
        base = (
            "class PersonController {\n"
            "private void Start() {\n"
            "soundA = RuntimeManager.CreateInstance(one);\n"
            "soundB = RuntimeManager.CreateInstance(two);\n"
            "settings = RestoreSettings();\n"
            "actionMove = SetupMove();\n"
            "}\n}\n"
        )
        self.assertEqual(isolate_player_start_fmod(base).count("player_start_missing_fmod_event"), 2)
        with self.assertRaisesRegex(ValueError, "audio-before-settings"):
            isolate_player_start_fmod(base.replace("settings = RestoreSettings();\n",
                                                   "settings = RestoreSettings();\n", 1)
                                     .replace("soundB = RuntimeManager.CreateInstance(two);\n",
                                              "settings = ReadFromDisk();\nsoundB = RuntimeManager.CreateInstance(two);\n"))
        with self.assertRaisesRegex(ValueError, "Unrecognized player FMOD event assignment"):
            isolate_player_start_fmod(base.replace(
                "soundB = RuntimeManager.CreateInstance(two);",
                "FinishInitialization(RuntimeManager.CreateInstance(two));"))
        with self.assertRaisesRegex(ValueError, "statement count drift|audio-before-settings"):
            isolate_player_start_fmod(base.replace(
                "soundB = RuntimeManager.CreateInstance(two);\n", ""))




class AndroidAudioSettingsVcaTests(unittest.TestCase):
    def test_six_missing_vcas_do_not_abort_later_original_settings(self):
        import hashlib
        from unittest.mock import patch
        assignments = "".join(
            "    master" + str(i) + ' = RuntimeManager.GetVCA("vca:/test' + str(i) + '");\n'
            for i in range(6)
        )
        original = (
            "class AudioSettingsBox {\n"
            "  private void SettingStart() {\n" +
            assignments +
            "    CompleteOtherSettings();\n"
            "  }\n"
            "}\n"
        )
        with patch.dict('scripts.adapt_android_render_lifetimes.PINS',
                        {'AudioSettingsBox': (hashlib.sha256(original.encode()).hexdigest(), 0)}):
            output = adapt("AudioSettingsBox", original)
        self.assertEqual(output.count("FMODUnity.VCANotFoundException __raftMissingAudioVca"), 6)
        self.assertEqual(output.count("settings_missing_fmod_vca"), 6)
        self.assertEqual(output.count("RuntimeManager.GetVCA("), 6)
        self.assertEqual(output.count("CompleteOtherSettings();"), 1)
        self.assertNotIn("catch (System.Exception", output)
        self.assertNotIn("SetWorld", output)

    def test_vca_adapter_rejects_missing_call_or_expression_drift(self):
        assignments = "".join("    f" + str(i) + " = RuntimeManager.GetVCA(v" + str(i) + ");\n"
                              for i in range(6))
        fixture = "class AudioSettingsBox {\n  public void SettingStart() {\n" + assignments + "  }\n}"
        self.assertEqual(isolate_audio_settings_vca(fixture).count("settings_missing_fmod_vca"), 6)
        with self.assertRaisesRegex(ValueError, "exactly six"):
            isolate_audio_settings_vca(fixture.replace("    f5 = RuntimeManager.GetVCA(v5);\n", ""))
        with self.assertRaisesRegex(ValueError, "assignment shape"):
            isolate_audio_settings_vca(fixture.replace(
                "f5 = RuntimeManager.GetVCA(v5);",
                "PlayWithoutField(RuntimeManager.GetVCA(v5));"))
