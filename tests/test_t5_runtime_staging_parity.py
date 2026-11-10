"""Executable source-free parity controls for native Unity/managed Android runtime staging."""
import tempfile
from pathlib import Path
import unittest

from scripts.t5_validate_runtime_staging_parity import (
    MANAGED_HELPER, NATIVE_WORKFLOW, RUNTIME_DIR, managed_sources,
    native_sources, verify, verify_staged_runtime_bytes,
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

    def test_manifest_drift_names_are_actionable_and_safe(self):
        # Only Android-owned, validated basenames appear in diagnostics.
        missing = self.native.replace(" AndroidExpansionArchiveProbe.cs", "", 1)
        with self.assertRaises(ValueError) as error:
            verify(self.managed, missing, RUNTIME_DIR)
        message = str(error.exception)
        self.assertIn("managed_only=['AndroidExpansionArchiveProbe.cs']", message)
        self.assertIn("native_only=[]", message)

        extra = self.native.replace(
            " AndroidExpansionArchiveProbe.cs",
            " AndroidExpansionArchiveProbe.cs AdditionalProbe.cs", 1)
        with self.assertRaises(ValueError) as error:
            verify(self.managed, extra, RUNTIME_DIR)
        message = str(error.exception)
        self.assertIn("managed_only=[]", message)
        self.assertIn("native_only=['AdditionalProbe.cs']", message)

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


    def _staged_fixture(self, temp):
        base = Path(temp)
        runtime = base / "runtime"
        candidate = base / "unity-candidate"
        staged = candidate / "Assets" / "RaftAndroid" / "Platform"
        runtime.mkdir()
        staged.mkdir(parents=True)
        names = native_sources(self.native)
        for index, name in enumerate(names):
            data = (f"// synthetic runtime sample {index}: {name}\n").encode()
            (runtime / name).write_bytes(data)
            (staged / name).write_bytes(data)
        return runtime, candidate, staged, names

    def test_staged_final_native_candidate_exact_bytes_all_runtime_sources(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime, project, staged, names = self._staged_fixture(temp)
            found = verify_staged_runtime_bytes(runtime, project, names)
            self.assertEqual(found, tuple(sorted(names)))
            self.assertIn("LocalProfileStore.cs", found)

    def test_staged_runtime_byte_mutation_cannot_claim_same_source(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime, project, staged, names = self._staged_fixture(temp)
            (staged / "LocalProfileStore.cs").write_bytes(b"// stale offline identity source")
            with self.assertRaisesRegex(ValueError, "bytes changed"):
                verify_staged_runtime_bytes(runtime, project, names)

    def test_staged_source_absence_and_injected_cs_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime, project, staged, names = self._staged_fixture(temp)
            (staged / "LocalProfileStore.cs").unlink()
            with self.assertRaisesRegex(ValueError, "Missing or unexpected"):
                verify_staged_runtime_bytes(runtime, project, names)
            (staged / "LocalProfileStore.cs").write_bytes((runtime / "LocalProfileStore.cs").read_bytes())
            (staged / "UntrustedOverride.cs").write_bytes(b"class Foo {}")
            with self.assertRaisesRegex(ValueError, "Missing or unexpected"):
                verify_staged_runtime_bytes(runtime, project, names)

    def test_staged_runtime_symlink_and_linked_parent_fail_closed(self):
        with tempfile.TemporaryDirectory() as temp:
            runtime, project, staged, names = self._staged_fixture(temp)
            target = staged / "LocalProfileStore.cs"
            target.unlink()
            try:
                target.symlink_to(runtime / "LocalProfileStore.cs")
            except (OSError, NotImplementedError):
                self.skipTest("symlink creation unavailable")
            with self.assertRaisesRegex(ValueError, "Linked"):
                verify_staged_runtime_bytes(runtime, project, names)
            target.unlink()
            target.write_bytes((runtime / "LocalProfileStore.cs").read_bytes())
            alias = Path(temp) / "linked-candidate"
            alias.symlink_to(project, target_is_directory=True)
            with self.assertRaisesRegex(ValueError, "linked native runtime staging root"):
                verify_staged_runtime_bytes(runtime, alias, names)

    def test_final_unity_candidate_runtime_stage_is_before_compiler(self):
        label = "      - name: T5 attest final native Android runtime source bytes (read-only)"
        self.assertEqual(self.native.count(label), 1)
        start = self.native.index(label)
        before = self.native.index("      - name: Stage private Unity project candidate inside runner workspace")
        after = self.native.index("      - name: Unity Editor 2021.3.45f2 Android import and compile")
        self.assertLess(before, start)
        self.assertLess(start, after)
        block = self.native[start:self.native.index("      - name:", start + len(label))]
        self.assertIn("python3 -m scripts.t5_validate_runtime_staging_parity", block)
        self.assertIn('--project "$GITHUB_WORKSPACE/unity-candidate"', block)
        self.assertNotIn("continue-on-error:", block)

    def test_t4_durable_profile_writer_present_in_current_staging(self):
        self.assertIn("LocalProfileStore.cs", native_sources(self.native))
        current = (RUNTIME_DIR / "LocalProfileStore.cs").read_text()
        self.assertIn("Flush(flushToDisk: true)", current)


if __name__ == "__main__":
    unittest.main()
