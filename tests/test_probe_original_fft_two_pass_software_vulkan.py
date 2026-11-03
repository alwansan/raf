"""Source-free controls for A1 true two-dispatch private Vulkan result parser."""
import json
import unittest

from scripts.probe_original_fft_two_pass_software_vulkan import (
    MARKER, EXTRA_FLAGS, parse_two_pass_result, validate_original_compiled_pairs,
)
from scripts.probe_original_fft_software_vulkan import IMAGE_FORMATS
def example():
    return {
        "cpu_software_vulkan":True,
        "extent_width":8,"extent_height":1,
        "input_seed":0,"dispatch_group_y":1,
        "original_written_pixels":8,"roundtrip_written_pixels":8,
        "write_coverage_mismatch_pixels":0,
        "nonfinite_components":0,"max_abs_difference":0.0,
        "relative_l2_difference":0.0,"within_selected_tolerance":True,
        "synthetic_canary_verified":True,
        "unity_gpu_or_android_device_verified":False,
    }


def report(**changes):
    record = example()
    record.pop("rgba32f_linear_only",None)
    record.update({
        "vulkan_image_format":"rgba32f","image_channels":4,"image_component_bits":32,
        **{field:True for field in EXTRA_FLAGS},
    })
    record.update(changes)
    return MARKER+json.dumps(record)


class AuthenticTwoPassVulkanTests(unittest.TestCase):
    def test_positive_two_pass_source_and_readback_flags(self):
        result=parse_two_pass_result(report())
        self.assertTrue(result["first_pass_output_feeds_second_source"])
        self.assertTrue(result["intermediate_compute_write_read_barrier"])
        self.assertFalse(result["unity_gpu_or_android_device_verified"])

    def test_shader_first_second_dataflow_is_not_optional(self):
        for flag in EXTRA_FLAGS:
            with self.subTest(flag=flag),self.assertRaisesRegex(ValueError,"dependency"):
                parse_two_pass_result(report(**{flag:False}))

    def test_unknown_original_image_format_is_rejected(self):
        with self.assertRaises(ValueError):
            parse_two_pass_result(report(vulkan_image_format="unknown"))

    def test_nonexistent_writes_never_succeed(self):
        with self.assertRaisesRegex(ValueError,"image writes"):
            parse_two_pass_result(report(original_written_pixels=0))

    def test_wrong_second_pass_result_is_disagreement(self):
        result=parse_two_pass_result(report(
            max_abs_difference=0.5,relative_l2_difference=0.3,
            within_selected_tolerance=False))
        self.assertFalse(result["within_selected_tolerance"])

    def test_duplicate_private_report_and_fields_blocked(self):
        with self.assertRaisesRegex(ValueError,"ambiguous"):
            parse_two_pass_result(report()+"\n"+report())
        with self.assertRaisesRegex(ValueError,"schema"):
            parse_two_pass_result(report(private_shader_text="LEAK"))

    def test_format_families_validate_true_packed_component_layout(self):
        for name,(channels,bits) in IMAGE_FORMATS.items():
            with self.subTest(name=name):
                result=parse_two_pass_result(report(vulkan_image_format=name,
                    image_channels=channels,image_component_bits=bits))
                self.assertEqual(result["image_channels"],channels)

    def test_zero_bytecode_is_not_valid_as_original_serialized_pairs(self):
        for tree, scan in (({},[]),({"variants":[]},[])):
            with self.assertRaises(ValueError):
                validate_original_compiled_pairs(tree,scan)

    def test_small_corrupt_serialized_variant_table_is_rejected(self):
        tree={"variants":[{"kernels":[{"name":"fake","variantMap":[]}] * 20}]}
        with self.assertRaises(ValueError):
            validate_original_compiled_pairs(tree,[{"binary_sha256":"00"}]*20)

    def test_bad_json_or_unsupported_platform_claim_rejected(self):
        with self.assertRaises(ValueError):
            parse_two_pass_result(MARKER+"{this is invalid json}")
        with self.assertRaises(ValueError):
            parse_two_pass_result(report(cpu_software_vulkan=False))
        with self.assertRaises(ValueError):
            parse_two_pass_result(report(unity_gpu_or_android_device_verified=True))


if __name__=="__main__":
    unittest.main()
