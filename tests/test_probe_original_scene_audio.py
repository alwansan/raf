"""No-Unity structural tests of privacy-safe private source probe."""
import tempfile
from pathlib import Path
import unittest
from scripts.probe_original_scene_audio import inspect, method_body


class SceneAudioProbeTests(unittest.TestCase):
    def test_inspects_original_style_callback_without_echoing_source(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / "SoundManager.cs").write_text(
                'class SoundManager { public void OnSceneEvent(int sceneEvent) '
                '{ RuntimeManager.CreateInstance(secret); } '
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
            method_body('public void OnSceneEvent() {} public void OnSceneEvent() {}', "OnSceneEvent")
        with self.assertRaises(ValueError):
            method_body('private void Awake() {}', "OnSceneEvent")


if __name__ == "__main__":
    unittest.main()
