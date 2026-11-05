"""T1 synthetic Unity fixture: no game data, license or original source."""
import json
from pathlib import Path
import tempfile
import unittest

from scripts.t1_sourcefree_unity_fixture import (
    ASSET_FILE, ASSEMBLY_FILE, ASSET_PATH, EDITOR_VERSION,
    TEST_FRAMEWORK, construct
)


class T1SourcefreeFixtureTests(unittest.TestCase):
    def test_fixture_is_exactly_unity2021_with_single_editmode_test(self):
        with tempfile.TemporaryDirectory() as d:
            project = Path(d) / "sourcefree"
            result = construct(project)
            self.assertTrue(result["synthetic_unity_test_fixture_created"])
            self.assertFalse(result["unity_activation_verified"])
            self.assertFalse(result["private_game_source_used"])
            self.assertFalse(result["original_raft_data_acquired"])
            self.assertFalse(result["original_fft_import_or_device_proven"])
            version = (project/"ProjectSettings/ProjectVersion.txt").read_text()
            self.assertEqual(version, "m_EditorVersion: " + EDITOR_VERSION + "\n")
            manifest = json.loads((project/"Packages/manifest.json").read_text())
            self.assertEqual(manifest, {"dependencies":{"com.unity.test-framework":TEST_FRAMEWORK}})
            asmdef = json.loads((project/ASSET_PATH/ASSEMBLY_FILE).read_text())
            self.assertEqual(asmdef["optionalUnityReferences"], ["TestAssemblies"])
            self.assertEqual(asmdef["includePlatforms"], ["Editor"])
            self.assertEqual(asmdef["precompiledReferences"], ["nunit.framework.dll"])
            source = (project/ASSET_PATH/ASSET_FILE).read_text()
            self.assertEqual(source.count("[Test]"), 1)
            self.assertIn("Application.unityVersion", source)
            self.assertNotIn("ComputeShader", source)

    def test_existing_project_never_overwritten(self):
        with tempfile.TemporaryDirectory() as d:
            project = Path(d) / "prior"
            project.mkdir()
            data = project / "keep"
            data.write_text("do not replace")
            with self.assertRaises(ValueError):
                construct(project)
            self.assertEqual(data.read_text(), "do not replace")

    def test_symlink_project_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            other = root / "other"
            other.mkdir()
            link = root / "linked"
            link.symlink_to(other, target_is_directory=True)
            with self.assertRaises(ValueError):
                construct(link)
            with self.assertRaises(ValueError):
                construct(link / "nested")

    def test_missing_parent_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                construct(Path(d) / "not-existing" / "project")


if __name__ == "__main__":
    unittest.main()
