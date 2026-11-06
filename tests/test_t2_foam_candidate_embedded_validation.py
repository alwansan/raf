"""T2 synthetic controls for compiling exact embedded original Foam program text."""
import unittest
from pathlib import Path
import tempfile

from scripts.t2_foam_candidate_embedded_validation import (
    extract_embedded_programs, compile_embedded,
)
from tests.test_t2_foam_private_shaderlab_candidate import (
    fixture, source_model_fixture,
)
from scripts.t2_foam_private_shaderlab_candidate import assemble


def source():
    parsed, stages, states = fixture()
    return assemble(parsed, stages, states, source_model_fixture())[0]


class EmbeddedTests(unittest.TestCase):
    def test_actual_completed_candidate_two_embedded_programs(self):
        programs = extract_embedded_programs(source())
        self.assertEqual(len(programs), 2)
        self.assertTrue(all("#pragma vertex main" in p for p in programs))
        self.assertTrue(all("#pragma fragment main" in p for p in programs))

    def test_extra_authoring_pass_is_not_accepted(self):
        original = source()
        broken = original.replace("SubShader {", "SubShader {\nPass {\nHLSLPROGRAM\nx\nENDHLSL\n}", 1)
        with self.assertRaises(ValueError):
            extract_embedded_programs(broken)

    def test_missing_fragment_or_unsupported_target_rejected(self):
        for old, replacement in [
            ("#pragma fragment main", "#pragma fragment unproven"),
            ("#pragma target 5.0", "#pragma target 6.0"),
            ("#elif defined(SHADER_STAGE_FRAGMENT)", "#elif defined(UNPROVEN)"),
        ]:
            with self.subTest(old=old), self.assertRaises(ValueError):
                extract_embedded_programs(source().replace(old, replacement, 1))

    def test_missing_program_end_rejected(self):
        with self.assertRaises(ValueError):
            extract_embedded_programs(source().replace("ENDHLSL", "", 1))

    def test_duplicate_target_pragma_rejected(self):
        broken = source().replace("#pragma target 5.0",
                                  "#pragma target 5.0\n#pragma target 5.0", 1)
        with self.assertRaises(ValueError):
            extract_embedded_programs(broken)

    def test_over_budget_and_empty_rejected(self):
        for candidate in ("", "X" * (4 * 1024 * 1024 + 1)):
            with self.assertRaises(ValueError):
                extract_embedded_programs(candidate)

    def test_compilation_failure_reports_only_safe_category(self):
        with tempfile.TemporaryDirectory() as t:
            private = Path(t) / "private.shader"
            private.write_text(source())
            safe = compile_embedded(private, Path(t), invoke=lambda _: False)
            self.assertEqual(safe["status"], "embedded_stage_compilation_blocked")
            self.assertEqual(safe["stage_count_validated"], 0)
            self.assertNotIn("float4", str(safe))
            self.assertNotIn("Synthetic source", str(safe))
            self.assertFalse(safe["private_source_published"])

    def test_missing_candidate_rejected(self):
        with tempfile.TemporaryDirectory() as t:
            with self.assertRaises(ValueError):
                compile_embedded(Path(t) / "missing.shader", Path(t))

    def test_scratch_inside_candidate_invalid(self):
        with tempfile.TemporaryDirectory() as t:
            candidate = Path(t) / "sample.shader"
            candidate.write_text(source())
            with self.assertRaises(ValueError):
                compile_embedded(candidate, candidate)

    def test_no_untrusted_executable_native_codegen_outside_scratch(self):
        # No source-free fixture is permitted to fake compiler or validator
        # success with a missing SPIR-V output file.
        with tempfile.TemporaryDirectory() as t:
            candidate = Path(t) / "sample.shader"
            candidate.write_text(source())
            safe = compile_embedded(candidate, Path(t), invoke=lambda _: True)
            self.assertEqual(safe["status"], "embedded_spirv_validation_blocked")
            self.assertFalse(safe["private_source_published"])


if __name__ == "__main__":
    unittest.main()
