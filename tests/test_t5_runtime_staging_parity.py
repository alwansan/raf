"""Executable source-free parity controls for native Unity/managed Android runtime staging."""
import tempfile
from pathlib import Path
import unittest

from scripts.t5_validate_runtime_staging_parity import (
    MANAGED_HELPER, NATIVE_WORKFLOW, RUNTIME_DIR, managed_sources,
    native_sources, verify,
)


class AndroidSourceStagingParity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.managed = MANAGED_HELPER.read_text(encoding="utf-8")
        cls.native = NATIVE_WORKFLOW.read_text(encoding="utf-8")

    def test_actual_native_and_original_managed_staging_match(self):
        names = verify(self.managed, self.native, RUNTIME_DIR)
        self.assertGreaterEqual(len(names), 17)
        self.assertIn("AndroidExpansionArchiveProbe.cs", names)
        self.assertIn("AndroidTestDiagnostics.cs", names)
        self.assertEqual(set(names), set(managed_sources(self.managed)))
        self.assertEqual(set(names), set(native_sources(self.native)))

    def test_missing_native_probe_is_rejected(self):
        modified = self.native.replace(" AndroidExpansionArchiveProbe.cs", "", 1)
        self.assertNotEqual(modified, self.native)
        with self.assertRaisesRegex(ValueError, "staging drift"):
            verify(self.managed, modified, RUNTIME_DIR)

    def test_duplicate_native_copy_entry_is_rejected(self):
        modified = self.native.replace(
            " AndroidTestDiagnostics.cs",
            " AndroidTestDiagnostics.cs AndroidTestDiagnostics.cs", 1)
        self.assertNotEqual(modified, self.native)
        with self.assertRaisesRegex(ValueError, "duplicate"):
            verify(self.managed, modified, RUNTIME_DIR)

    def test_native_shell_metacharacter_or_path_escape_rejected(self):
        for injection in (" ../../Probe.cs", " Probe.cs&&id", " Probe.cs$(id)"):
            with self.subTest(injection=injection):
                mutated = self.native.replace(
                    " AndroidExpansionArchiveProbe.cs",
                    " AndroidExpansionArchiveProbe.cs" + injection, 1)
                with self.assertRaises(ValueError):
                    verify(self.managed, mutated, RUNTIME_DIR)

    def test_native_copy_target_mismatch_rejected(self):
        changed = self.native.replace(
            '/ExportedProject/Assets/RaftAndroid/Platform/"',
            '/ExportedProject/Assets/RaftAndroid/Other/"', 1)
        self.assertNotEqual(changed, self.native)
        with self.assertRaisesRegex(ValueError, "one exact native"):
            verify(self.managed, changed, RUNTIME_DIR)

    def test_missing_or_dynamic_original_managed_manifest_rejected(self):
        for bad in (
            "RUNTIME_COMPILE_SUPPORT_FILES = tuple(['AndroidTestDiagnostics.cs'])",
            "RUNTIME_COMPILE_SUPPORT_FILES = ('AndroidTestDiagnostics.cs', 'AndroidTestDiagnostics.cs')",
            "BROKEN_MANIFEST = ('AndroidTestDiagnostics.cs',)",
        ):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    managed_sources(bad)

    def test_missing_regular_runtime_file_rejected_before_any_unity_build(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime = Path(temp)
            # No game assets copied. One absent member must fail before
            # any expensive build or Unity staging operation.
            with self.assertRaisesRegex(ValueError, "Missing regular native"):
                verify(self.managed, self.native, runtime)

    def test_native_staging_copy_loop_is_not_duplicated(self):
        # A second copy block can overwrite project sources unexpectedly.
        lines = self.native.splitlines()
        idx = next(i for i, line in enumerate(lines)
                   if "for name in AndroidStreamingAssets.cs" in line)
        repeated = "\n".join(lines[idx:idx + 3])
        with self.assertRaisesRegex(ValueError, "one exact native"):
            verify(self.managed, self.native + "\n" + repeated, RUNTIME_DIR)


if __name__ == "__main__":
    unittest.main()
