"""No-Unity structural tests of privacy-safe private source probe."""
import tempfile
from pathlib import Path
import unittest
from scripts.probe_original_scene_audio import inspect, inspect_player, method_body


class SceneAudioProbeTests(unittest.TestCase):
    def test_inspects_original_style_callback_without_echoing_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "SoundManager.cs").write_text(
                'class SoundManager {\n    public void OnSceneEvent(int sceneEvent) '
                '{ RuntimeManager.CreateInstance(secret); }\n    '
                'private void Awake() { Ready(); } }'
            )
            result = inspect(root)
            self.assertEqual(result["methods"]["OnSceneEvent"]["return_void"], True)
            self.assertEqual(result["methods"]["OnSceneEvent"]["event_creation_calls"], 1)
            self.assertTrue(result["methods"]["OnSceneEvent"]["has_fmod_runtime_manager"])
            self.assertNotIn("secret", str(result))
            self.assertFalse(result["modified_source"])
            self.assertFalse(result["unity_compiled"])

    def test_fails_closed_for_duplicate_or_missing_callbacks(self):
        with self.assertRaises(ValueError):
            method_body('\npublic void OnSceneEvent() {}\npublic void OnSceneEvent() {}', "OnSceneEvent")
        with self.assertRaises(ValueError):
            method_body('private void Awake() {}', "OnSceneEvent")


    def test_player_audio_probe_reports_initialization_order_without_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "PersonController.cs").write_text(
                'class PersonController {\n'
                '  private void Start()\n'
                '  {\n'
                '    FMOD.Studio.EventInstance instance1 = RuntimeManager.CreateInstance(firstSecret);\n'
                '    FMOD.Studio.EventInstance instance2 = RuntimeManager.CreateInstance(secondSecret);\n'
                '    settings = ReadSettings();\n'
                '    actionMove = ReadyInput();\n'
                '  }\n'
                '}\n'
            )
            report = inspect_player(root)
            self.assertTrue(report["start_void"])
            self.assertEqual(report["fmod_event_creation_calls"], 2)
            self.assertEqual(report["settings_assignment_count"], 1)
            self.assertEqual(report["action_move_assignment_count"], 1)
            self.assertTrue(all(x["before_settings_assignment"] for x in report["event_creation_sites"]))
            self.assertTrue(all(x["has_assignment"] for x in report["event_creation_sites"]))
            self.assertNotIn("firstSecret", str(report))
            self.assertNotIn("secondSecret", str(report))

    def test_missing_player_sound_creation_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "PersonController.cs").write_text('class PersonController {\nprivate void Start() { settings = null; }\n}')
            with self.assertRaises(ValueError):
                inspect_player(root)


if __name__ == "__main__":
    unittest.main()
