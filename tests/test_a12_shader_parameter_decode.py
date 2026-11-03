"""Synthetic Unity2021.3 Shader ParameterBlob specification regressions (no game bytes)."""
import json
import struct
import unittest

from scripts.a12_shader_parameter_decode import parse_parameter_blob
from scripts.w1_depth_shaderlab import decode_empty_parameters


def i32(value):
    return struct.pack("<i", value)


def packed_name(name):
    source = name.encode("utf-8")
    result = i32(len(source)) + source
    return result + b"\0" * ((-len(source)) % 4)


def fixture(groups=1, numeric=0, resources=0, struct_count=0, cb_size=0):
    output = bytearray(i32(202012090) + i32(groups))
    for ix in range(groups):
        output += packed_name("SyntheticGlobal" if ix == 0 else "SyntheticCB")
        output += i32((cb_size if ix else 0) or (16 if numeric and ix else 0))
        output += i32(numeric)
        for _ in range(numeric):
            output += packed_name("SyntheticFloat4")
            output += i32(0)  # authored ShaderParamType float
            output += i32(1)  # row
            output += i32(4)  # columns
            output += i32(0)  # vector
            output += i32(0)  # array
            output += i32(0)  # index
        output += i32(struct_count)
        for _ in range(struct_count):
            output += packed_name("SyntheticStruct")
            output += i32(0) + i32(0) + i32(16) + i32(1)
            output += packed_name("SyntheticMember")
            output += i32(0) + i32(1) + i32(4) + i32(0) + i32(0) + i32(0)
    output += i32(resources)
    for i in range(resources):
        output += packed_name("SyntheticTexture")
        output += i32(0) + i32(i) + i32(i) + struct.pack("<I", 4)
    return bytes(output)


class A12OriginalShaderParameterTests(unittest.TestCase):
    def test_empty_parameter_layout_matches_existing_depth_parser(self):
        raw = fixture()
        w1 = decode_empty_parameters(raw)
        a12 = parse_parameter_blob(raw)
        self.assertTrue(w1["overrides_empty"])
        self.assertTrue(a12["parameters_empty"])
        self.assertEqual(a12["bytes_consumed"], len(raw))
        self.assertEqual(a12["group_count"], 1)

    def test_global_numeric_parameter_was_outside_legacy_empty_decoder(self):
        raw = fixture(numeric=1)
        with self.assertRaises(ValueError):
            decode_empty_parameters(raw)
        got = parse_parameter_blob(raw)
        self.assertEqual(got["numeric_parameter_count"], 1)
        self.assertEqual(got["vector_parameter_count"], 1)
        self.assertFalse(got["parameters_empty"])
        self.assertEqual(got["bytes_consumed"], len(raw))

    def test_exact_original_texture_record_requires_extra_u32(self):
        got = parse_parameter_blob(fixture(resources=1))
        self.assertEqual(got["resource_parameter_count"], 1)
        self.assertEqual(got["texture_count"], 1)
        self.assertEqual(got["resource_kind_counts"], {"resource_kind_0": 1})
        self.assertFalse(got["parameters_empty"])

    def test_named_original_constant_buffer_is_not_treated_as_zero(self):
        raw = fixture(groups=2)
        got = parse_parameter_blob(raw)
        self.assertEqual(got["constant_buffer_count"], 1)
        self.assertFalse(got["parameters_empty"])
        self.assertTrue(got["only_zero_size_empty_cb_groups"])
        self.assertEqual(got["all_group_used_bytes"], 0)
        self.assertEqual(got["nonzero_size_constant_buffers"], 0)

    def test_nonzero_size_empty_constant_buffer_not_omitted(self):
        got = parse_parameter_blob(fixture(groups=2, cb_size=16))
        self.assertEqual(got["constant_buffer_used_bytes"], 16)
        self.assertEqual(got["nonzero_size_constant_buffers"], 1)
        self.assertFalse(got["only_zero_size_empty_cb_groups"])

    def test_struct_parameter_schema_counted_without_leaking_names(self):
        got = parse_parameter_blob(fixture(struct_count=1))
        self.assertEqual(got["struct_count"], 1)
        self.assertEqual(got["struct_numeric_member_count"], 1)
        self.assertFalse(got["parameters_empty"])

    def test_truncated_integer_and_string_fail_closed(self):
        for raw in (b"", b"\0" * 7, fixture()[:-1],
                    i32(202012090) + i32(1) + i32(700) + b"word"):
            with self.subTest(size=len(raw)), self.assertRaises(ValueError):
                parse_parameter_blob(raw)

    def test_trailing_data_not_silently_ignored(self):
        with self.assertRaisesRegex(ValueError, "trailing"):
            parse_parameter_blob(fixture() + b"\0\0\0\0")

    def test_wrong_version_and_absurd_group_count_fail_closed(self):
        for raw in (i32(0) + fixture()[4:],
                    i32(202012090) + i32(500) + fixture()[8:]):
            with self.assertRaises(ValueError):
                parse_parameter_blob(raw)

    def test_original_name_contents_not_returned(self):
        report = parse_parameter_blob(fixture(numeric=1, resources=1))
        output = json.dumps(report)
        for private in ("SyntheticGlobal", "SyntheticFloat4", "SyntheticTexture"):
            self.assertNotIn(private, output)
        self.assertFalse(report["original_shader_names_published"])
        self.assertFalse(report["shaderlab_binding_verified"])
        self.assertFalse(report["parameters_empty"])

    def test_altered_texture_dimension_fails(self):
        raw = bytearray(fixture(resources=1))
        raw[-4:] = struct.pack("<I", 0xFFFFFFFF)
        with self.assertRaisesRegex(ValueError, "dimension"):
            parse_parameter_blob(bytes(raw))

    def test_group_name_padding_corruption_fails(self):
        raw = bytearray(fixture())
        raw[8:12] = i32(1)
        raw[12] = ord("A")
        raw[13] = 1
        with self.assertRaises(ValueError):
            parse_parameter_blob(bytes(raw))


if __name__ == "__main__":
    unittest.main()
