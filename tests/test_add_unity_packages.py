import json
import tempfile
import unittest
from pathlib import Path
from scripts.add_unity_packages import PACKAGES, ensure

class UnityPackagesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        d = self.root / "Packages"
        d.mkdir()
        self.manifest = d / "manifest.json"
        self.original = {"dependencies": {"com.unity.modules.ui": "1.0.0"}}
        self.manifest.write_text(json.dumps(self.original))
    def tearDown(self):
        self.temp.cleanup()
    def test_dry_run_and_apply_preserve_builtin(self):
        ensure(self.root, apply=False)
        self.assertEqual(json.loads(self.manifest.read_text()), self.original)
        r = ensure(self.root, apply=True)
        self.assertEqual(r["added"], PACKAGES)
        deps = json.loads(self.manifest.read_text())["dependencies"]
        self.assertEqual(deps["com.unity.modules.ui"], "1.0.0")
        self.assertEqual({k: deps[k] for k in PACKAGES}, PACKAGES)
        self.assertEqual(ensure(self.root, apply=True)["added"], {})
    def test_reject_conflicting_installed_dll(self):
        p = self.root / "Assets/Plugins/RaftManagedReferences"
        p.mkdir(parents=True)
        (p/"Unity.TextMeshPro.dll").write_bytes(b"placeholder")
        with self.assertRaises(ValueError):
            ensure(self.root, apply=True)
    def test_reject_package_version_override(self):
        self.manifest.write_text(json.dumps({"dependencies": {"com.unity.ugui": "8.0.0"}}))
        with self.assertRaises(ValueError):
            ensure(self.root, apply=True)
    def test_reject_invalid_manifest(self):
        self.manifest.write_text("[]")
        with self.assertRaises(ValueError):
            ensure(self.root, apply=True)

if __name__ == "__main__":
    unittest.main()
