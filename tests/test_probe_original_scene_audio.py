"""No-Unity structural tests of privacy-safe private source probe."""
import tempfile
from pathlib import Path
import unittest
from scripts.probe_original_scene_audio import inspect, inspect_player, inspect_ground_control, inspect_audio_settings, method_body


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


    def test_ground_control_dependency_probe_does_not_fabricate_init(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "PersonController.cs").write_text(
                "class PersonController {\n"
                "private void Start() { DoOtherSetup(); }\n"
                "private void GroundControll(int hit) { actionMove.Process(); settings.Update(); }\n"
                "}\n"
            )
            result = inspect_ground_control(root)
            self.assertEqual(result["settings"]["method_reads"], 1)
            self.assertEqual(result["actionMove"]["method_reads"], 1)
            self.assertEqual(result["settings"]["start_assignments"], 0)
            self.assertEqual(result["actionMove"]["start_assignments"], 0)

    def test_original_audio_settings_vca_probe_is_redacted(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "AudioSettingsBox.cs").write_text(
                "class AudioSettingsBox {\n"
                "private void SettingStart() {\n"
                "  masterVca = RuntimeManager.GetVCA(sensitivePath);\n"
                "  Ready();\n"
                "}\n}\n"
            )
            report = inspect_audio_settings(root)
            self.assertTrue(report["returns_void"])
            self.assertEqual(report["vca_call_count"], 1)
            self.assertTrue(report["vca_calls_simple_assignments"])
            self.assertNotIn("sensitivePath", str(report))
            self.assertFalse(report["modified_source"])

    def test_ground_control_probe_is_private_and_identifies_early_init_dependencies(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "PersonController.cs").write_text(
                "class PersonController {\n"
                "private void Start() { actionMove = InitializeMovement(); settings = Setup(); }\n"
                "private void GroundControll(int groundHit) {\n"
                "  actionMove.Process();\n"
                "  settings.Update();\n"
                "  AuditGround(secretData);\n"
                "}\n}\n"
            )
            report = inspect_ground_control(root)
            self.assertTrue(report["method_void"])
            self.assertEqual(report["settings"]["method_reads"], 1)
            self.assertEqual(report["actionMove"]["method_reads"], 1)
            self.assertEqual(report["actionMove"]["start_assignments"], 1)
            self.assertFalse(report["modified_source"])
            self.assertNotIn("secretData", str(report))


if __name__ == "__main__":
    unittest.main()
