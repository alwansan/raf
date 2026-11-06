"""T2 synthetic adversarial controls for private original Foam descriptor overlap."""
import tempfile
from pathlib import Path
import unittest

from scripts.t2_foam_embedded_descriptor_layout import (
    reflected_descriptor_map, compare_cross_stage_descriptors, probe,
)
from scripts.t2_foam_private_shaderlab_candidate import assemble
from test_t2_foam_private_shaderlab_candidate import fixture, source_model_fixture


def candidate():
    parsed, stages, states = fixture()
    return assemble(parsed, stages, states, source_model_fixture())[0]


def ref(mode, *, ubos=None, samplers=None, images=None, combined=None):
    return {
        "entryPoints": [{"name":"main","mode":mode}],
        "ubos":ubos or [],
        "separate_samplers":samplers or [],
        "separate_images":images or [],
        "textures":combined or [],
    }


def row(set_id, binding, *, extent=None, dims=None):
    x={"set":set_id,"binding":binding,"name":"PRIVATE-original-identifier"}
    if extent is not None:
        x["block_size"]=extent
    if dims is not None:
        x["array"]=dims
    return x


class DescriptorVaryingConstraints(unittest.TestCase):
    def test_cross_stage_distinct_numbers_no_conflict(self):
        a=ref("vert",ubos=[row(0,0,extent=96),row(0,2,extent=128)])
        b=ref("frag",samplers=[row(0,1)],images=[row(0,3)])
        r=compare_cross_stage_descriptors(a,b)
        self.assertEqual(r["shared_descriptor_class_conflict_count"],0)
        self.assertTrue(r["same_type_pipeline_descriptor_set_layout_possible"])

    def test_shared_uniform_buffer_compatible(self):
        a=ref("vert",ubos=[row(0,0,extent=96)])
        b=ref("frag",ubos=[row(0,0,extent=96)])
        r=compare_cross_stage_descriptors(a,b)
        self.assertEqual(r["shared_exact_descriptor_and_buffer_range_count"],1)
        self.assertEqual(r["shared_descriptor_class_conflict_count"],0)

    def test_same_numeric_binding_ubo_and_sampler_conflict(self):
        a=ref("vert",ubos=[row(0,1,extent=64)])
        b=ref("frag",samplers=[row(0,1)])
        r=compare_cross_stage_descriptors(a,b)
        self.assertEqual(r["shared_descriptor_class_conflict_count"],1)
        self.assertEqual(r["conflict_descriptor_class_pairs"],
                         {"sampler_versus_uniform_buffer":1})
        self.assertFalse(r["same_type_pipeline_descriptor_set_layout_possible"])
        self.assertNotIn("PRIVATE-original",str(r))

    def test_same_numeric_binding_ubo_and_image_conflict(self):
        r=compare_cross_stage_descriptors(ref("vert",ubos=[row(0,2,extent=128)]),
                                          ref("frag",images=[row(0,2)]))
        self.assertEqual(r["conflict_descriptor_class_pairs"],
                         {"sampled_image_versus_uniform_buffer":1})

    def test_shared_cb_different_range_reported_not_automatic_type_conflict(self):
        r=compare_cross_stage_descriptors(ref("vert",ubos=[row(0,0,extent=96)]),
                                          ref("frag",ubos=[row(0,0,extent=128)]))
        self.assertEqual(r["shared_CB_buffer_extent_difference_count"],1)
        self.assertEqual(r["shared_descriptor_class_conflict_count"],0)
        self.assertTrue(r["same_type_pipeline_descriptor_set_layout_possible"])

    def test_shared_descriptor_array_shape_mismatch_blocks(self):
        r=compare_cross_stage_descriptors(ref("vert",samplers=[row(0,0,dims=[4])]),
                                          ref("frag",samplers=[row(0,0,dims=[2])]))
        self.assertEqual(r["shared_descriptor_array_shape_mismatch_count"],1)
        self.assertFalse(r["same_type_pipeline_descriptor_set_layout_possible"])

    def test_same_stage_binding_duplicate_rejected(self):
        x=ref("vert",samplers=[row(0,1)],ubos=[row(0,1,extent=64)])
        with self.assertRaises(ValueError):
            reflected_descriptor_map(x,mode="vert")
        x=ref("frag",samplers=[row(0,1),row(0,1)])
        with self.assertRaises(ValueError):
            reflected_descriptor_map(x,mode="frag")

    def test_unbound_or_unsafe_descriptor_rejected(self):
        for descriptor in [
            {"binding":0},
            {"set":0},
            row(True,1),
            row(0,True),
            row(-1,0),
            row(0,-1),
            row(0,65536),
            row(0,1,dims=[0]),
            row(0,1,dims=[True]),
            row(0,1,dims=[3,4,5,6]),
        ]:
            with self.subTest(descriptor=descriptor),self.assertRaises(ValueError):
                reflected_descriptor_map(ref("frag",samplers=[descriptor]),mode="frag")

    def test_invalid_block_extent_and_duplicate_spirv_id_rejected(self):
        for extent in (0,True,16*1024*1024+1):
            with self.subTest(extent=extent),self.assertRaises(ValueError):
                reflected_descriptor_map(ref("vert",ubos=[row(0,0,extent=extent)]),mode="vert")
        a=row(0,0,extent=64)
        b=row(0,1,extent=64)
        a["id"]=9;b["id"]=9
        with self.assertRaises(ValueError):
            reflected_descriptor_map(ref("vert",ubos=[a,b]),mode="vert")

    def test_incorrect_stage_entry_and_unsupported_category_rejected(self):
        with self.assertRaises(ValueError):
            reflected_descriptor_map(ref("frag"),mode="vert")
        x=ref("vert");x["push_constants"]=[{"type":"anything"}]
        with self.assertRaises(ValueError):
            reflected_descriptor_map(x,mode="vert")
        x=ref("frag");x["atomic_counters"]=[row(0,1)]
        with self.assertRaises(ValueError):
            reflected_descriptor_map(x,mode="frag")

    def test_empty_stage_reflection_does_not_fake_collision(self):
        r=compare_cross_stage_descriptors(ref("vert"),ref("frag"))
        self.assertEqual(r["vertex_descriptor_count"],0)
        self.assertEqual(r["fragment_descriptor_count"],0)
        self.assertTrue(r["same_type_pipeline_descriptor_set_layout_possible"])

    def test_private_compile_failure_only_bounded_codes(self):
        with tempfile.TemporaryDirectory() as temp:
            original=Path(temp)/"private.shader";original.write_text(candidate())
            r=probe(original,Path(temp),invoke=lambda _:False)
            self.assertEqual(r["status"],"blocked_real_original_stage_compilation")
            self.assertNotIn("PRIVATE-original",str(r))
            self.assertFalse(r["private_source_published"])

    def test_missing_shader_or_compiled_binary_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(ValueError):
                probe(Path(temp)/"absent.shader",Path(temp))
            path=Path(temp)/"original.shader";path.write_text(candidate())
            r=probe(path,Path(temp),invoke=lambda _:True)
            self.assertEqual(r["status"],"blocked_real_original_spirv_validation")

    def test_synthetic_all_four_stages_pipeline_reports_numeric_only(self):
        def compiler(argv):
            if argv[0]=="glslangValidator":
                Path(argv[argv.index("-o")+1]).write_bytes(b"\x03\x02\x23\x07"+b"\0"*36)
            return True
        def reflector(path):
            name=Path(path).name
            pi=0 if "pass0" in name else 1
            if "stage1" in name:
                return ref("vert",ubos=[row(0,0,extent=96),row(0,1,extent=64)])
            return ref("frag",ubos=[row(0,0,extent=128)],samplers=[row(0,1)])
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/"private.shader";path.write_text(candidate())
            result=probe(path,Path(temp),invoke=compiler,reflect=reflector)
            self.assertEqual(result["status"],
                             "original_private_foam_vulkan_stage_descriptor_layout_conflict")
            self.assertEqual(result["embedded_stages_recompiled_and_spirv_val"],4)
            self.assertEqual(result["total_descriptor_type_conflicts"],2)
            self.assertEqual(result["per_pass_descriptor_set_layout"][0][
                "shared_CB_buffer_extent_difference_count"],1)
            self.assertEqual(result["per_pass_descriptor_set_layout"][1][
                "shared_descriptor_class_conflict_count"],1)
            self.assertFalse(result["private_source_published"])
            self.assertNotIn("PRIVATE-original",str(result))


if __name__=="__main__":
    unittest.main()
