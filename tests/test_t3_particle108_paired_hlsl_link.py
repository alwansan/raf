"""No Raft assets: strict four-pair joint glslang SPIR-V validation and stage evidence."""
import struct
import tempfile
from pathlib import Path
from unittest import TestCase

from scripts.t3_particle108_paired_hlsl_link import (
    PAIRS, OPTIONS, COUNT_KEYS, entrypoint_execution_models,
    stage_result, classify_joint_result, joint_compile, evaluate,
)

def fake_spv(models):
    words=[0x07230203,0x00010300,0,64,0]
    for model in models:
        words.extend([(5<<16)|15,model,1,0x6e69616d,0])
    return struct.pack("<"+"I"*len(words),*words)

def stage(inputs=(),outputs=()):
    return {
        "inputs":[{"location":loc,"type":kind} for loc,kind in inputs],
        "outputs":[{"location":loc,"type":kind} for loc,kind in outputs],
        "resource_slots":{},
    }

class PrivateOriginalPairedGlslangTests(TestCase):
    def test_four_exact_configuration_options(self):
        self.assertEqual(set(OPTIONS),{"linked","linked_iomap","linked_aml","linked_iomap_aml"})
        self.assertEqual(OPTIONS["linked"],())
        self.assertEqual(OPTIONS["linked_iomap"],("--hlsl-iomap",))

    def test_stage_parser_detects_single_vertex(self):
        self.assertEqual(entrypoint_execution_models(fake_spv([0])),[0])
        self.assertEqual(stage_result([0])["only_one"],1)

    def test_stage_parser_detects_both_execution_models(self):
        self.assertEqual(entrypoint_execution_models(fake_spv([0,4])),[0,4])
        self.assertEqual(stage_result([0,4])["both"],1)
        self.assertEqual(stage_result([0,4])["other"],0)

    def test_spv_bad_header_rejected(self):
        bad=bytearray(fake_spv([0]))
        bad[0]=0x12
        with self.assertRaisesRegex(ValueError,"invalid_private_spirv_header"):
            entrypoint_execution_models(bytes(bad))

    def test_spv_broken_word_count_rejected(self):
        bad=bytearray(fake_spv([0]))
        bad[20:24]=struct.pack("<I",15)
        with self.assertRaisesRegex(ValueError,"invalid_private_spirv_instruction"):
            entrypoint_execution_models(bytes(bad))

    def test_spv_missing_name_terminator_rejected(self):
        bad=bytearray(fake_spv([0]))
        bad[-4:]=struct.pack("<I",0x61616161)
        with self.assertRaisesRegex(ValueError,"unterminated_private_spirv_entrypoint_name"):
            entrypoint_execution_models(bytes(bad))

    def test_stage_result_rejects_boolean_and_unknown_shapes(self):
        with self.assertRaisesRegex(ValueError,"invalid_private_spirv_execution_models"):
            stage_result([True,4])
        self.assertEqual(stage_result([0,4,5])["other"],1)

    def test_classifier_both_models_counted_only_if_valid(self):
        good={"command_success":1,"vulkan11_valid":1,
              "missing_spirv_binary":0,"models":[0,4]}
        row=classify_joint_result(good)
        self.assertEqual(row["modules_with_both_vertex_fragment_entries"],1)
        self.assertEqual(row["modules_with_only_one_graphics_entry"],0)
        good["vulkan11_valid"]=0
        self.assertEqual(classify_joint_result(good)["modules_with_both_vertex_fragment_entries"],0)

    def test_classify_invalid_private_linker_result_rejected(self):
        with self.assertRaisesRegex(ValueError,"invalid_private_linker_result"):
            classify_joint_result({"command_success":True,"vulkan11_valid":1,
                                   "missing_spirv_binary":0,"models":[0]})

    def test_joint_compile_unsafe_options_rejected_before_start(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            v=root/"v.hlsl"; f=root/"f.hlsl"
            v.write_text("float4 main() : SV_Position { return 0; }")
            f.write_text("float4 main() : SV_Target { return 1; }")
            with self.assertRaisesRegex(ValueError,"unsafe_private_paired_hlsl_compilation"):
                joint_compile(v,f,root/"out.spv",("--unknown",))
            with self.assertRaisesRegex(ValueError,"unsafe_private_paired_hlsl_compilation"):
                joint_compile(v,v,root/"out.spv",())

    def test_fake_four_pairs_source_baseline_independent_stages_two_of_four(self):
        with tempfile.TemporaryDirectory() as d:
            pairs=[(b"synthetic VS",b"synthetic FS") for _ in range(PAIRS)]
            def translator(code,stage,folder):
                (folder/"private.hlsl").write_text("synthetic HLSL")
                (folder/"original.spv").write_text("dummy")
                (folder/"roundtrip.spv").write_text("dummy")
                return {"vulkan11_valid":True,"hlsl_recovered":True,
                        "roundtrip_vulkan11_valid":True}
            def reflector(path):
                stage_is_vertex=path.parent.name.endswith("stage-1")
                pair_index=int(path.parent.name.split("-")[1])
                bad=path.name=="roundtrip.spv" and pair_index%2
                if stage_is_vertex:
                    return stage(outputs=[(0,"vec3" if bad else "vec4")])
                return stage(inputs=[(0,"vec4")])
            def linker(vertex,fragment,target,flags):
                return {"command_success":1,"vulkan11_valid":1,
                        "missing_spirv_binary":0,
                        "models":[0,4] if flags==OPTIONS["linked_iomap"] else [4]}
            report=evaluate(pairs,Path(d),translator=translator,
                            reflector=reflector,linker=linker)
            counts=report["counts"]
            self.assertEqual(set(counts),set(COUNT_KEYS))
            self.assertEqual(counts["source_pairs_linked"],4)
            self.assertEqual(counts["separate_roundtrip_pairs_linked"],2)
            self.assertEqual(counts["linked_iomap_modules_with_both_vertex_fragment_entries"],4)
            self.assertEqual(counts["linked_modules_with_only_one_graphics_entry"],4)
            self.assertNotIn("synthetic HLSL",str(report))

    def test_private_hlsl_bytecode_not_returned_as_result(self):
        row=classify_joint_result({
            "command_success":0,"vulkan11_valid":0,
            "missing_spirv_binary":1,"models":[]})
        self.assertEqual(row["modules_with_both_vertex_fragment_entries"],0)
        self.assertEqual(row["modules_missing_spirv_binary"],1)

if __name__=="__main__":
    import unittest
    unittest.main()
