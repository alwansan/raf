"""Synthetic deterministic normal/negative Foam stage-I/O ABI controls."""
import tempfile
from pathlib import Path
import unittest

from scripts.t2_foam_embedded_stage_io import (
    interface_rows, compare_varying_abi, verify_embedded_abi,
)
from scripts.t2_foam_private_shaderlab_candidate import assemble
from test_t2_foam_private_shaderlab_candidate import fixture, source_model_fixture


def candidate():
    parsed, stages, states = fixture()
    return assemble(parsed, stages, states, source_model_fixture())[0]


def stage(kind, inputs=None, outputs=None):
    return {"entryPoints": [{"name": "main", "mode": kind}],
            "inputs": inputs or [], "outputs": outputs or []}


class T2OriginalFoamInterfaceControls(unittest.TestCase):
    def test_exact_location_and_types_match_even_if_names_differ(self):
        vs=stage("vert", outputs=[
            {"name": "private_v_foo", "location": 0, "type": "vec2"},
            {"name": "private_v_bar", "location": 1, "type": "vec4"}])
        fs=stage("frag", inputs=[
            {"name": "other_private_name", "location": 1, "type": "vec4"}])
        result=compare_varying_abi(vs,fs)
        self.assertTrue(result["numerical_location_type_interface_compatible"])
        self.assertEqual(result["vertex_outputs_not_consumed_by_fragment"],1)
        self.assertEqual(result["fragment_varyings_location_type_matched"],1)

    def test_missing_vertex_location_is_blocker(self):
        result=compare_varying_abi(stage("vert", outputs=[
            {"location": 0, "type": "vec2"}]),stage("frag", inputs=[
            {"location": 1, "type": "vec2"}]))
        self.assertFalse(result["numerical_location_type_interface_compatible"])
        self.assertEqual(result["fragment_varyings_missing_vertex_output"],1)

    def test_same_location_incompatible_type_blocks(self):
        result=compare_varying_abi(stage("vert", outputs=[
            {"location": 0, "type": "vec3"}]),stage("frag", inputs=[
            {"location": 0, "type": "vec4"}]))
        self.assertFalse(result["numerical_location_type_interface_compatible"])
        self.assertEqual(result["fragment_varyings_type_or_array_mismatch"],1)

    def test_unknown_location_and_duplicate_rejected(self):
        for rows in (
            [{"type":"vec4"}],
            [{"location":0,"type":"vec3"},{"location":0,"type":"vec4"}],
            [{"location":True,"type":"vec4"}],
            [{"location":0,"type":"private_symbol_or_struct"}],
            [{"location":0,"type":"vec4","array":[0]}],
            [{"location":0,"type":"vec4","array":[True]}],
            [{"location":0,"type":"vec4","component":4}],
            [{"location":0,"type":"vec4","index":1}],
        ):
            with self.subTest(rows=rows),self.assertRaises(ValueError):
                interface_rows(stage("frag", inputs=rows),"inputs","frag")

    def test_builtin_without_location_skipped(self):
        x=stage("vert",outputs=[{"builtin":"Position","type":"vec4"},
                                {"location":1,"type":"vec2"}])
        self.assertEqual(len(interface_rows(x,"outputs","vert")),1)

    def test_same_location_different_component_not_equal(self):
        x=compare_varying_abi(stage("vert",outputs=[
            {"location":0,"component":2,"type":"vec2"}]),stage("frag",inputs=[
            {"location":0,"component":0,"type":"vec2"}]))
        self.assertFalse(x["numerical_location_type_interface_compatible"])

    def test_array_size_is_part_of_signature(self):
        x=compare_varying_abi(stage("vert",outputs=[
            {"location":0,"type":"vec2","array":[4]}]),stage("frag",inputs=[
            {"location":0,"type":"vec2","array":[5]}]))
        self.assertEqual(x["fragment_varyings_type_or_array_mismatch"],1)

    def test_empty_fragment_inputs_explicitly_marked(self):
        x=compare_varying_abi(stage("vert"),stage("frag"))
        self.assertTrue(x["numerical_location_type_interface_compatible"])
        self.assertTrue(x["empty_fragment_varying_interface"])

    def test_wrong_entry_point_stage_rejected(self):
        with self.assertRaises(ValueError):
            interface_rows(stage("frag"),"inputs","vert")
        with self.assertRaises(ValueError):
            interface_rows({"entryPoints": [],"inputs":[]},"inputs","frag")

    def test_compiler_failure_private_only(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"candidate.shader";p.write_text(candidate())
            safe=verify_embedded_abi(p,Path(root),invoke=lambda _: False)
            self.assertEqual(safe["status"],"blocked_compilation_of_embedded_original_stage")
            self.assertNotIn("private_v_foo",str(safe))
            self.assertFalse(safe["private_source_published"])

    def test_fake_spirv_val_success_with_no_binary_still_fails(self):
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"candidate.shader";p.write_text(candidate())
            safe=verify_embedded_abi(p,Path(root),invoke=lambda _: True)
            self.assertEqual(safe["status"],"blocked_spirv_validation")

    def test_missing_candidate_rejected(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(ValueError):
                verify_embedded_abi(Path(root)/"none.shader",Path(root))

    def test_positive_fake_reflection_pipeline_in_private_scratch(self):
        def compiler(cmd):
            if cmd[0]=="glslangValidator":
                Path(cmd[cmd.index("-o")+1]).write_bytes(b"\x03\x02\x23\x07"+b"\0"*36)
            return True
        def reflector(path):
            name=Path(path).name
            if "stage1" in name:
                return stage("vert",outputs=[{"location":0,"type":"vec2"}])
            return stage("frag",inputs=[{"location":0,"type":"vec2"}])
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"candidate.shader";p.write_text(candidate())
            safe=verify_embedded_abi(p,Path(root),invoke=compiler,reflect=reflector)
            self.assertEqual(safe["status"],
                             "source_original_embedded_two_pass_numeric_varyings_compatible")
            self.assertEqual(safe["compiled_stage_variants"],4)
            self.assertEqual(len(safe["per_pass_user_varying_counts"]),2)
            self.assertFalse(safe["actual_adreno_or_device_pixels_verified"])

    def test_negative_synthetic_pipeline_reports_mismatch_not_success(self):
        def compiler(cmd):
            if cmd[0]=="glslangValidator":
                Path(cmd[cmd.index("-o")+1]).write_bytes(b"\x03\x02\x23\x07"+b"\0"*36)
            return True
        def reflector(path):
            if "stage1" in Path(path).name:
                return stage("vert",outputs=[{"location":0,"type":"vec2"}])
            return stage("frag",inputs=[{"location":1,"type":"vec2"}])
        with tempfile.TemporaryDirectory() as root:
            p=Path(root)/"candidate.shader";p.write_text(candidate())
            safe=verify_embedded_abi(p,Path(root),invoke=compiler,reflect=reflector)
            self.assertEqual(safe["status"],"source_original_embedded_pass_varying_abi_mismatch")
            self.assertFalse(safe["all_fragment_inputs_have_matching_vertex_outputs"])
            self.assertEqual(safe["per_pass_user_varying_counts"][0][
                "fragment_varyings_missing_vertex_output"],1)


if __name__=="__main__":
    unittest.main()
