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
                       lambda source,buffers:source), \
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
                       lambda source,buffers:source):
                with self.assertRaisesRegex(ValueError,"unverified_original_hlsl_offsets_opt_in"):
                    verify_named_constant_buffers(
                        directory,0,[],original_hlsl_offsets="true")


if __name__=="__main__":
    unittest.main()
