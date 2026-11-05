"""Source-free T3 fourpass original DXBC + T1 raw SPIR-V stage test fixtures."""
import json
from pathlib import Path
import subprocess
from unittest.mock import patch
import tempfile
import unittest

from scripts import t3_original_921_t1_raw_spirv_audit as bridge

SECRET = "PRIVATE_ORIGINAL_SHADER_SEMANTIC_NEVER_ARTIFACT"
DXBC = b"PRIVATE_COMPILED_SHADER_BYTES"


def fake_source(code):
    is_v = code.endswith(b"_v")
    def row():
        return {"semantic": SECRET, "index": 0, "system_value": 0,
                "type": 3, "register": 1, "mask": 15, "used_mask": 3,
                "stream": 0}
    return {"input": [] if is_v else [row()],
            "output": [row()] if is_v else [],
            "input_tag": "ISGN", "output_tag": "OSGN"}


def good_translation(_code, _stage, _dst):
    return {"vulkan11_valid": True, "hlsl_recovered": True,
            "roundtrip_vulkan11_valid": True, "secret": SECRET}


def assembly(path):
    vertex = path.parent.name.endswith("stage-1")
    model = "Vertex" if vertex else "Fragment"
    storage = "Output" if vertex else "Input"
    return f"""
OpEntryPoint {model} %1 "main" %5 %7
OpDecorate %5 Location 1
OpDecorate %7 BuiltIn Position
%2 = OpTypeFloat 32
%3 = OpTypeVector %2 2
%4 = OpTypePointer {storage} %3
%5 = OpVariable %4 {storage}
%7 = OpVariable %4 {storage}
"""


class OriginalRawDisassemblyTests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory(prefix="t3-original-spv-sourcefree-")
        self.addCleanup(t.cleanup)
        self.root = Path(t.name)
        self.pairs = [(DXBC + b"_v", DXBC + b"_f") for _ in range(4)]

    def run_probe(self, **overrides):
        args = {"translator": good_translation,
                "disassembler": assembly, "original_parser": fake_source}
        args.update(overrides)
        return bridge.original_fourpass_private(self.pairs, self.root, **args)

    def test_original_four_pass_binary_direct_T1_validator_linkage(self):
        x = self.run_probe()
        c = x["counts"]
        self.assertEqual(c["passes_examined"], 4)
        self.assertEqual(c["original_DXBC_declared_fragment_component_lanes"], 16)
        self.assertEqual(c["original_DXBC_read_component_lanes"], 8)
        self.assertEqual(c["source_spirv_vertex_components"], 8)
        self.assertEqual(c["roundtrip_spirv_vertex_components"], 8)
        self.assertEqual(c["source_spirv_fragment_components"], 8)
        self.assertEqual(c["roundtrip_spirv_fragment_components"], 8)
        self.assertEqual(c["source_passes_numeric_compatible"], 4)
        self.assertEqual(c["roundtrip_passes_numeric_compatible"], 4)
        self.assertEqual(c["source_passes_readmask_equals_direct_fragment_components"], 4)
        self.assertEqual(c["roundtrip_passes_readmask_equals_direct_fragment_components"], 4)
        self.assertEqual(c["source_and_roundtrip_passes_direct_fragment_count_equal"], 4)

    def test_source_private_synthetic_program_not_exported(self):
        x = self.run_probe()
        s = json.dumps(x)
        for secret in (SECRET, DXBC.decode(), str(self.root), "source-pass"):
            self.assertNotIn(secret, s)
        self.assertFalse(x["original_DXBC_semantic_name_index_to_SPIRV_Location_mapping_proven"])
        self.assertFalse(x["original_interpolation_and_pixel_equivalence_proven"])
        self.assertFalse(x["original_Android_Adreno_device_pixels_verified"])

    def test_T1_direct_validator_location_mismatch_is_counted(self):
        def shifted(path):
            x = assembly(path)
            if path.parent.name.endswith("stage-0"):
                x = x.replace("Location 1", "Location 2")
            return x
        d = self.run_probe(disassembler=shifted)["counts"]
        self.assertEqual(d["source_passes_numeric_compatible"], 0)
        self.assertEqual(d["source_spirv_missing_fragment_components"], 8)
        self.assertEqual(d["source_spirv_unused_vertex_components"], 8)

    def test_T1_direct_validator_scalar_type_mismatch_is_counted(self):
        def typed(path):
            x = assembly(path)
            if path.parent.name.endswith("stage-0"):
                x = x.replace("OpTypeFloat 32", "OpTypeInt 32 0")
            return x
        d = self.run_probe(disassembler=typed)["counts"]
        self.assertEqual(d["source_spirv_missing_fragment_components"], 0)
        self.assertEqual(d["source_spirv_type_mismatches"], 8)
        self.assertEqual(d["source_passes_numeric_compatible"], 0)

    def test_T1_unsupported_SPIRV_layout_fails_closed(self):
        def unsupported(path):
            return assembly(path).replace("OpTypeVector %2 2", "OpTypeMatrix %2 2")
        with self.assertRaises(bridge.PrivateInterfaceUnsupported) as cm:
            self.run_probe(disassembler=unsupported)
        self.assertEqual(cm.exception.category, "TYPE_UNSUPPORTED")
        self.assertEqual(cm.exception.original_pass_ordinal, 0)
        self.assertEqual(cm.exception.source_or_roundtrip, "source")
        self.assertNotIn(SECRET, str(cm.exception))

    def test_unknown_private_T1_validator_error_does_not_expose_names(self):
        def leaking_checker(_v, _f):
            raise ValueError(SECRET)
        with self.assertRaises(bridge.PrivateInterfaceUnsupported) as cm:
            self.run_probe(numeric_checker=leaking_checker)
        self.assertEqual(cm.exception.category, "VALIDATION_OTHER")
        self.assertNotIn(SECRET, str(cm.exception))
        self.assertEqual(cm.exception.original_pass_ordinal, 0)

    def test_missing_original_SPIRV_variable_id_has_safe_failure_category(self):
        def missing_id(_v, _f):
            raise KeyError("%PRIVATE_ID")
        with self.assertRaises(bridge.PrivateInterfaceUnsupported) as cm:
            self.run_probe(numeric_checker=missing_id)
        self.assertEqual(cm.exception.category, "INTERFACE_DEFINITION_UNRESOLVED")
        self.assertNotIn("%PRIVATE_ID", str(cm.exception))

    def test_roundtrip_input_change_is_preserved_not_hidden(self):
        def shifted_roundtrip(path):
            x = assembly(path)
            if path.name == "roundtrip.spv" and path.parent.name.endswith("stage-0"):
                return x.replace("Location 1", "Location 3")
            return x
        d = self.run_probe(disassembler=shifted_roundtrip)["counts"]
        self.assertEqual(d["source_passes_numeric_compatible"], 4)
        self.assertEqual(d["roundtrip_passes_numeric_compatible"], 0)
        self.assertEqual(d["roundtrip_spirv_missing_fragment_components"], 8)

    def test_compiled_stage_status_requires_every_flag(self):
        def fail(_code, stage, _dest):
            return {"vulkan11_valid": True, "hlsl_recovered": True,
                    "roundtrip_vulkan11_valid": stage == 1}
        with self.assertRaisesRegex(ValueError, "compiler_incomplete"):
            self.run_probe(translator=fail)

    def test_original_semantic_linkage_failure_is_not_silent(self):
        def missing_vertex(code):
            x = fake_source(code)
            if code.endswith(b"_v"):
                x["output"][0]["semantic"] = "WRONG"
            return x
        with self.assertRaisesRegex(ValueError, "semantic_baseline_has_deficit"):
            self.run_probe(original_parser=missing_vertex)

    def test_no_three_pass_fake_proof(self):
        with self.assertRaisesRegex(ValueError, "not_four"):
            bridge.original_fourpass_private(self.pairs[:3], self.root)

    def test_numeric_checker_forbidden_extra_names_fail_closed(self):
        fake = {"vertex_components": 2, "fragment_components": 2,
                "missing_components": 0, "scalar_type_mismatches": 0,
                "unused_vertex_components": 0,
                "compatible_numeric_coverage": True,
                "private_debug_name": SECRET}
        with self.assertRaisesRegex(ValueError, "numeric_contract_shape"):
            bridge.safe_numeric_audit("vertex", "fragment", checker=lambda a,b:fake)

    def test_numeric_checker_contradictory_success_rejected(self):
        wrong = {"vertex_components": 2, "fragment_components": 2,
                 "missing_components": 1, "scalar_type_mismatches": 0,
                 "unused_vertex_components": 0, "compatible_numeric_coverage": True}
        with self.assertRaisesRegex(ValueError, "contradictory"):
            bridge.safe_numeric_audit("vertex", "fragment", checker=lambda a,b:wrong)

    def test_numeric_checker_bool_as_int_rejected(self):
        wrong = {"vertex_components": True, "fragment_components": 2,
                 "missing_components": 0, "scalar_type_mismatches": 0,
                 "unused_vertex_components": 0, "compatible_numeric_coverage": True}
        with self.assertRaisesRegex(ValueError, "numeric_count"):
            bridge.safe_numeric_audit("vertex", "fragment", checker=lambda a,b:wrong)

    def test_no_source_spv_length_or_symlink_outside_scope(self):
        with self.assertRaisesRegex(ValueError, "untrusted_private"):
            bridge.safe_numeric_audit("", "fake")

    def test_real_linux_posixpath_is_accepted_for_private_disassembly(self):
        path = self.root / "fixture.spv"
        path.write_bytes(b"SPV" + b"X" * 21)
        calls = []
        def trusted_fake(command, **_kwargs):
            calls.append(command[0])
            return subprocess.CompletedProcess(
                command, 0, stdout="OpEntryPoint Fragment %1 \\"main\\" %2"
                if command[0] == "spirv-dis" else "")
        with patch.object(bridge.subprocess, "run", side_effect=trusted_fake):
            text = bridge.private_module_disassemble(path)
        self.assertIn("OpEntryPoint Fragment", text)
        self.assertEqual(calls, ["spirv-val", "spirv-dis"])

    def test_private_disassembler_symlink_and_nonPath_inputs_fail_closed(self):
        actual = self.root / "real.spv"
        actual.write_bytes(b"SPV" + b"X" * 21)
        link = self.root / "linked.spv"
        link.symlink_to(actual)
        for obj in (link, str(actual), self.root / "missing.spv"):
            with self.subTest(value=type(obj).__name__), self.assertRaisesRegex(
                    ValueError, "invalid_private_original_SPIRV_stage_size"):
                bridge.private_module_disassemble(obj)

    def test_t1_original_owned_code_remains_unchanged(self):
        from scripts import t1_spirv_interface_component_audit as t1
        a = t1.audit(assembly(Path("pass-stage-1/original.spv")),
                     assembly(Path("pass-stage-0/original.spv")))
        self.assertTrue(a["compatible_numeric_coverage"])
        self.assertEqual(a["fragment_components"], 2)


if __name__ == "__main__":
    unittest.main()
