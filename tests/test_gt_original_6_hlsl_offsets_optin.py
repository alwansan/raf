"""Source-free opt-in HLSL packing regressions for SHA-original six-Material shader.

All other Shader48 variants retain the legacy default command. SPIR-V
Vulkan 1.1 validation and reflection of original offsets are still required.
"""
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
from unittest.mock import patch
import unittest

from scripts.gt_original_921_cb_hlsl import verify_named_constant_buffers


class SourceOriginalHLSLOffsets(unittest.TestCase):
    def run_candidate(self, original_hlsl_offsets=False, *, validator_ok=True):
        with TemporaryDirectory() as td:
            directory=Path(td)
            (directory/"resource-bound.hlsl").write_text(
                "float4 main() : SV_Target {return float4(0,0,0,0);}",
                encoding="utf-8")
            recorded=[]
            def compiler(argv):
                recorded.append(list(argv))
                return True
            def subprocess_result(argv, **kwargs):
                if argv[0]=="spirv-val":
                    return SimpleNamespace(
                        returncode=0 if validator_ok else 1,
                        stderr=b"Type of Uniform block member is invalid",
                        stdout=b"")
                return SimpleNamespace(returncode=0, stderr=b"",
                    stdout=json.dumps({"ubos":[],"types":{}}).encode())
            with patch("scripts.gt_original_921_cb_hlsl.command",compiler), \
                 patch("scripts.gt_original_921_cb_hlsl.rebind_constant_buffers",
                       lambda source,buffers,**kwargs:source), \
                 patch("scripts.gt_original_921_cb_hlsl.subprocess.run",
                       side_effect=subprocess_result):
                if validator_ok:
                    result=verify_named_constant_buffers(
                        directory,0,[],original_hlsl_offsets=original_hlsl_offsets)
                    self.assertEqual(result,0)
                else:
                    with self.assertRaisesRegex(
                            ValueError,"named_constant_buffer_candidate_spirv_invalid"):
                        verify_named_constant_buffers(
                            directory,0,[],original_hlsl_offsets=original_hlsl_offsets)
                    self.assertTrue(
                        (directory/"original-validator-raw-private.log").is_file())
            return recorded


    def test_original_typed_array_holes_only_zero_if_source_reads_prove_safe(self):
        from scripts.gt_original_921_cb_hlsl import rebind_constant_buffers
        buffer = {
            "name": "ActualCB", "source_slot": 0,
            "members": [{
                "name": "SOURCE_ARRAY", "index": 0, "array_size": 4,
                "type": 0, "rows": 1, "columns": 1, "matrix": False,
            }],
            "structs": [],
            "original_named_lanes": [
                {"path": ["SOURCE_ARRAY", i // 4], "row": 0,
                 "column": 0, "type": 0, "matrix": False}
                if i % 4 == 0 else None for i in range(16)
            ],
        }
        header = (
            "cbuffer Old : register(b1) {\n"
            "float4 cb0_0_m0[4] : packoffset(c0);\n"
            "};\n"
        )
        valid = header + (
            "float4 main() : SV_Target { "
            "return float4(cb0_0_m0[1].x, 0, 0, 1); }\n"
        )
        result = rebind_constant_buffers(
            valid, [buffer], original_array_padding_zero=True)
        block = result.split(
            "cbuffer ActualCB : register(b1) {", 1)[1].split("};", 1)[0]
        self.assertIn("float SOURCE_ARRAY[4] : packoffset(c0.x);", block)
        self.assertNotIn("_pad", block)
        self.assertIn("0.0", result)
        legacy = rebind_constant_buffers(valid, [buffer])
        old_block = legacy.split(
            "cbuffer ActualCB : register(b1) {", 1)[1].split("};", 1)[0]
        self.assertIn("raft921_cb0_pad1", old_block)
        dynamic = header + (
            "float4 main() : SV_Target { "
            "return float4(cb0_0_m0[int(1)].y, 0, 0, 1); }\n"
        )
        with self.assertRaisesRegex(
                ValueError, "original_array_padding_dynamic_read_not_proven"):
            rebind_constant_buffers(
                dynamic, [buffer], original_array_padding_zero=True)
        literal = header + (
            "float4 main() : SV_Target { "
            "return float4(cb0_0_m0[1].y, 0, 0, 1); }\n"
        )
        with self.assertRaisesRegex(
                ValueError, "original_array_padding_raw_read_not_proven"):
            rebind_constant_buffers(
                literal, [buffer], original_array_padding_zero=True)
        with self.assertRaisesRegex(
                ValueError, "unverified_original_typed_padding_zero_optin"):
            rebind_constant_buffers(
                valid, [buffer], original_array_padding_zero="True")

    def test_original_named_cb_binding_diagnostics_fail_closed(self):
        from scripts.gt_original_921_cb_hlsl import verify_offsets
        source = [{"name": "OriginalCB", "source_slot": 0,
                   "translated_binding": 2, "members": [], "structs": []}]
        with self.assertRaisesRegex(
                ValueError, "named_constant_buffer_source_block_not_reflected"):
            verify_offsets({"ubos": [], "types": {}}, source)
        with self.assertRaisesRegex(
                ValueError, "named_constant_buffer_source_name_at_wrong_descriptor"):
            verify_offsets({"ubos": [
                {"set": 0, "binding": 3, "name": "OriginalCB"}],
                "types": {}}, source)
        with self.assertRaisesRegex(
                ValueError, "named_constant_buffer_source_block_name_changed"):
            verify_offsets({"ubos": [
                {"set": 0, "binding": 2, "name": "DIFFERENT_PRIVATE_NAME"}],
                "types": {}}, source)

    def test_vulkan_overlap_classifies_private_original_vs_padding_only_as_counts(self):
        from scripts.gt_original_921_cb_hlsl import (
            original_compiled_cb_numeric_offset_profile)
        block = {
            "translated_binding": 4,
            "members": [{"name": "SECRET_SOURCE_ARRAY", "index": 0,
                         "array_size": 4, "matrix": False}],
            "structs": [],
        }
        reflection = {
            "ubos": [{"set": 0, "binding": 4, "type": "SECRET_UBO"}],
            "types": {"SECRET_UBO": {"members": [
                {"name": "SECRET_SOURCE_ARRAY", "offset": 0,
                 "array_stride": 16, "array": [4]},
                {"name": "raft921_cb0_pad4", "offset": 16},
            ]}},
        }
        report = original_compiled_cb_numeric_offset_profile(
            reflection, [block],
            validator_text="Structure member 1 at offset 16 overlaps "
                           "previous member ending at offset 63; SECRET_UBO")
        self.assertEqual(report["validator_overlap_pair_reflection_matches"], 1)
        self.assertEqual(report["validator_overlap_previous_source_field"], 1)
        self.assertEqual(report["validator_overlap_current_synthetic_padding"], 1)
        self.assertEqual(report["validator_overlap_previous_original_array"], 1)
        self.assertEqual(report["original_source_array_field_count"], 1)
        self.assertEqual(
            report["compiled_synthetic_padding_within_original_array_span"], 1)
        self.assertEqual(
            report["compiled_synthetic_padding_outside_original_typed_spans"], 0)
        self.assertNotIn("SECRET", json.dumps(report))

    def test_compiled_cb_numeric_offset_profile_hides_original_names(self):
        from scripts.gt_original_921_cb_hlsl import (
            original_compiled_cb_numeric_offset_profile)
        block = {"translated_binding": 2,
                 "members": [
                     {"name": "PRIVATE_ALPHA", "index": 0,
                      "array_size": 0, "matrix": False},
                     {"name": "PRIVATE_BETA", "index": 80,
                      "array_size": 3, "matrix": False}],
                 "structs": []}
        reflection = {
            "ubos": [{"set": 0, "binding": 2, "type": "PRIVATE_STRUCT"}],
            "types": {"PRIVATE_STRUCT": {
                "members": [
                    {"name": "PRIVATE_ALPHA", "offset": 0},
                    {"name": "PRIVATE_BETA", "offset": 16, "array": [4], "array_stride": 32}]
            }}
        }
        counts = original_compiled_cb_numeric_offset_profile(
            reflection, [block])
        self.assertEqual(counts["compiled_member_offsets_match_original"], 1)
        self.assertEqual(counts["compiled_member_offsets_differ_original"], 1)
        self.assertEqual(counts["compiled_array_strides_differ_original"], 1)
        self.assertEqual(counts["compiled_array_element_counts_differ_original"], 1)
        self.assertNotIn("PRIVATE_ALPHA", json.dumps(counts))
        self.assertNotIn("PRIVATE_BETA", json.dumps(counts))
        self.assertNotIn("PRIVATE_STRUCT", json.dumps(counts))

    def test_original_hlsl_cb_declarations_are_sorted_by_byte_offset(self):
        # Source fields may be reversed and padding is generated afterward.
        # Strict SPIR-V uniform layouts require monotonic member offsets.
        from scripts.gt_original_921_cb_hlsl import rebind_constant_buffers
        import re
        source = (
            "cbuffer Old : register(b1) {\n"
            "float4 cb0_0_m0[4] : packoffset(c0);\n"
            "};\n"
            "float4 main() : SV_Target { return cb0_0_m0[0]; }\n"
        )
        lanes = [None] * 16
        for index, name in ((0, "low"), (12, "high")):
            lanes[index] = {
                "path": [name], "row": 0, "column": 0,
                "type": 0, "matrix": False,
            }
        def member(name, offset):
            return {
                "name": name, "index": offset, "type": 0,
                "array_size": 0, "rows": 1, "columns": 1, "matrix": False,
            }
        buffer = {
            "name": "ActualCB", "source_slot": 0,
            "original_named_lanes": lanes,
            "members": [member("high", 48), member("low", 0)],
            "structs": [],
        }
        result = rebind_constant_buffers(source, [buffer])
        cbuffer = result.split("cbuffer ActualCB : register(b1) {", 1)[1].split("};", 1)[0]
        addresses = [
            int(reg) * 4 + "xyzw".index(lane)
            for reg, lane in re.findall(r"packoffset\(c(\d+)\.([xyzw])\)", cbuffer)
        ]
        self.assertEqual(addresses, sorted(addresses))
        self.assertEqual(addresses, list(range(16)))
        self.assertIn("float low : packoffset(c0.x);", cbuffer)
        self.assertIn("float high : packoffset(c3.x);", cbuffer)

    def test_all_existing_shaders_still_use_default_strict_offsets(self):
        recorded=self.run_candidate()
        self.assertEqual(len(recorded),1)
        self.assertNotIn("--hlsl-offsets",recorded[0])
        self.assertIn("glslangValidator",recorded[0])

    def test_explicit_sha_original_six_uses_hlsl_offsets_only_opt_in(self):
        recorded=self.run_candidate(True)
        self.assertEqual(len(recorded),1)
        self.assertIn("--hlsl-offsets",recorded[0])

    def test_original_shader_still_requires_real_vulkan_validator(self):
        self.assertIn("--hlsl-offsets",self.run_candidate(True,validator_ok=False)[0])

    def test_untrusted_non_boolean_opt_in_is_never_accepted(self):
        with TemporaryDirectory() as td:
            directory=Path(td)
            (directory/"resource-bound.hlsl").write_text("source")
            with patch("scripts.gt_original_921_cb_hlsl.rebind_constant_buffers",
                       lambda source,buffers,**kwargs:source):
                with self.assertRaisesRegex(ValueError,"unverified_original_hlsl_offsets_opt_in"):
                    verify_named_constant_buffers(
                        directory,0,[],original_hlsl_offsets="true")


if __name__=="__main__":
    unittest.main()
