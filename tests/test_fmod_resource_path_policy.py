"""Static safety regression for original FMOD resource discovery.

Unity's Resources.LoadAll("FMODStudioSettings") addresses a directory/resource
of that name, not sibling files named FMODStudioSettingsPlatform_*.asset.
Real import/serialization/Android validation must still run in Unity CI.
"""
from pathlib import Path
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "android-port/Editor/FmodAndroidValidation.cs"


class FmodResourcePathPolicyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.code = SOURCE.read_text(encoding="utf-8")

    def test_discovers_original_platform_asset_filenames_without_creating_defaults(self):
        self.assertIn('Directory.GetFiles(resourceRoot, "FMODStudioSettingsPlatform*.asset"', self.code)
        self.assertIn("SearchOption.TopDirectoryOnly", self.code)
        self.assertNotIn('Resources.LoadAll<FMODUnity.Platform>("FMODStudioSettings")', self.code)
        self.assertNotIn("Settings.Instance;", self.code)

    def test_each_original_platform_is_checked_through_editor_and_player_resource_lookups(self):
        self.assertIn('Path.GetFileNameWithoutExtension(path)', self.code)
        self.assertIn('AssetDatabase.LoadAssetAtPath<FMODUnity.Platform>(assetPath)', self.code)
        self.assertIn('Resources.Load<FMODUnity.Platform>("FMODStudioSettings/" + name)', self.code)
        self.assertIn('original != runtime', self.code)

    def test_duplicate_identity_gate_precedes_vendor_settings_loading(self):
        self.assertLess(self.code.index('FindProperty("identifier")'),
                        self.code.index('Resources.Load<FMODUnity.Settings>("FMODStudioSettings")'))
        self.assertIn('android != 1 || defaults != 1', self.code)
        self.assertIn('version.intValue != 0x00020215', self.code)


if __name__ == "__main__":
    unittest.main()
