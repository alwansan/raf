"""Isolated source-only regression tests for final Unity runtime staging parity.

Run: python -m unittest discover -s tests -p 'test_t5_runtime_staging_bytes.py'
No game assets, Unity Editor, Android SDK or external dependencies.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "t5_validate_runtime_staging_parity.py"
SPEC = importlib.util.spec_from_file_location("t5_runtime_parity", MODULE_PATH)
assert SPEC and SPEC.loader
parity = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(parity)


class FinalRuntimeStagingBytesTests(unittest.TestCase):
    NAMES = ("LocalProfileStore.cs", "RuntimeExample.cs")

    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        root = Path(self.temp.name)
        self.runtime = root / "runtime"
        self.runtime.mkdir()
        self.project = root / "project"
        self.platform = self.project / "Assets" / "RaftAndroid" / "Platform"
        self.platform.mkdir(parents=True)
        for name in self.NAMES:
            data = ("// " + name + "\n").encode("utf-8")
            (self.runtime / name).write_bytes(data)
            (self.platform / name).write_bytes(data)

    def check(self):
        return parity.verify_staged_runtime_bytes(self.runtime, self.project, self.NAMES)

    def test_matching_final_candidate_passes(self):
        self.assertEqual(self.check(), tuple(sorted(self.NAMES)))

    def test_changed_byte_fails(self):
        (self.platform / "RuntimeExample.cs").write_bytes(b"// altered\n")
        with self.assertRaisesRegex(ValueError, "RuntimeExample.cs"):
            self.check()

    def test_missing_staged_source_fails(self):
        (self.platform / "RuntimeExample.cs").unlink()
        with self.assertRaisesRegex(ValueError, "RuntimeExample.cs"):
            self.check()

    def test_unexpected_staged_source_fails(self):
        (self.platform / "Extra.cs").write_text("// unexpected")
        with self.assertRaisesRegex(ValueError, "Extra.cs"):
            self.check()

    def test_linked_staged_source_fails(self):
        path = self.platform / "RuntimeExample.cs"
        path.unlink()
        try:
            path.symlink_to(self.runtime / "RuntimeExample.cs")
        except (OSError, NotImplementedError):
            self.skipTest("Symlinks unavailable on this filesystem")
        with self.assertRaisesRegex(ValueError, "Linked runtime candidate source"):
            self.check()

    def test_missing_required_profile_source_fails(self):
        with self.assertRaisesRegex(ValueError, "offline profile"):
            parity.verify_staged_runtime_bytes(
                self.runtime, self.project, ("RuntimeExample.cs",)
            )


if __name__ == "__main__":
    unittest.main()
