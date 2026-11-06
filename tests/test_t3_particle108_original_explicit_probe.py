"""Synthetic-only one-shot SHA-original Shader48 explicit VKD3D A/B runner tests."""
import json
from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from scripts import t3_particle108_original_explicit_probe as m

LAYOUT=(("cbuffer",89,(2,8)),("srv",88,(3,)),("sampler",90,(1,)))
SOURCE=[(b"X"*40,b"Y"*40) for _ in range(4)]

def proof(_a,_b,_spv_a,_spv_b,_stage):
    return {
        "status":m.dual.STATUS,
        "chosen_explicit_target_layouts_verified":2,
        "same_source_to_spirv_variable_identity_across_profiles":True,
        "whole_spirv_program_identical_except_descriptor_literals":True,
        "source_register_numbers_spirv_IDS_descriptor_coordinates_published":False,
        "shaderlab_compiled_or_android_pixels_verified":False,
        "source_registers_mapped_under_both_profiles":3,
    }

class OriginalExplicitStageRunnerTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.temp=Path(self.tmp.name)
        self.helper=self.temp/"synthetic-executable"
        self.helper.write_bytes(b"test")
        self.helper.chmod(0o700)
        self.job=self.temp/"runner-private"
        self.job.mkdir()
        self.calls=[]
    def execute(self,argv,**kwargs):
        self.calls.append(tuple(argv))
        if argv[0]!="spirv-val":
            # SPV payload never leaves private temporary folder in this fixture.
            Path(argv[2]).write_bytes(b"safe-fake-spv"*3)
        return SimpleNamespace(returncode=0)
    def run_probe(self,*,pairs=SOURCE,runner=None,verifier=proof):
        return m.classify(pairs,self.job,self.helper,
                          layout=lambda *_:LAYOUT,
                          verifier=verifier,
                          runner=runner or self.execute)

    def test_four_original_keyword_pairs_sixteen_private_compilations(self):
        result=self.run_probe()
        self.assertEqual(result["counts"]["verified_source_keyword_pairs"],4)
        self.assertEqual(result["counts"]["source_stages_with_two_explicit_profiles_verified"],8)
        self.assertEqual(result["counts"]["private_compiler_invocations"],16)
        self.assertEqual(result["counts"]["private_spirv_val_invocations"],16)
        self.assertEqual(result["counts"]["verified_original_register_rows"],24)
        self.assertEqual(len(self.calls),32)
        self.assertTrue(result["explicit_DX_source_register_to_chosen_VK_target_proven_by_dual_profile"])
        self.assertFalse(result["ShaderLab_program_recovered_or_Unity_Android_pixels_proven"])
        for value in ("safe-fake-spv","T3MAP1","source.dxbc","private-pair-"):
            self.assertNotIn(value,json.dumps(result))

    def test_nonzero_compiler_is_not_laundered_as_valid_original_proof(self):
        def no_compile(argv,**kwargs):
            return SimpleNamespace(returncode=7)
        with self.assertRaisesRegex(ValueError,"T3_PRIVATE_COMPILER_NONZERO_EXIT_7"):
            self.run_probe(runner=no_compile)

    def test_invalid_spirv_validator_is_fatal_before_pair_verification(self):
        def invalid_spv(argv,**kwargs):
            if argv[0]=="spirv-val":
                return SimpleNamespace(returncode=1)
            Path(argv[2]).write_bytes(b"test-spv"*4)
            return SimpleNamespace(returncode=0)
        with self.assertRaisesRegex(ValueError,"T3_PRIVATE_SPIRV_INVALID"):
            self.run_probe(runner=invalid_spv)

    def test_missing_compiler_output_is_an_error(self):
        with self.assertRaisesRegex(ValueError,"T3_PRIVATE_OUTPUT_MISSING"):
            self.run_probe(runner=lambda *_a,**_k:SimpleNamespace(returncode=0))

    def test_dual_profile_identity_not_forgeable_by_boolean(self):
        def counterfeit(*args):
            result=proof(*args)
            result["same_source_to_spirv_variable_identity_across_profiles"]=1
            return result
        with self.assertRaisesRegex(ValueError,"T3_PRIVATE_RESULT_CONTRACT"):
            self.run_probe(verifier=counterfeit)

    def test_dual_profile_verifier_rejection_is_safe_and_fatal(self):
        def reject(*args):
            raise ValueError("private path and register must never appear in log")
        with self.assertRaisesRegex(ValueError,"T3_PRIVATE_DUAL_PROFILE_PAIR_REJECTED"):
            self.run_probe(verifier=reject)

    def test_wrong_four_pair_scope_rejected_before_source_read(self):
        with self.assertRaisesRegex(ValueError,"T3_PRIVATE_SCOPE_INVALID"):
            self.run_probe(pairs=SOURCE[:3])
        with self.assertRaisesRegex(ValueError,"T3_PRIVATE_SCOPE_INVALID"):
            self.run_probe(pairs=[(b"X"*40,"wrong")]*4)

    def test_helper_symlink_does_not_cross_trust_boundary(self):
        outside=self.temp/"outside"
        outside.write_bytes(b"dummy")
        link=self.temp/"symlink"
        link.symlink_to(outside)
        with self.assertRaisesRegex(ValueError,"T3_PRIVATE_SCOPE_INVALID"):
            m.classify(SOURCE,self.job,link)

if __name__=="__main__":
    unittest.main()
