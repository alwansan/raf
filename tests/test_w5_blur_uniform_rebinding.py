import copy
import unittest

from scripts.w5_blur_uniform_rebinding import rebind


def fixture():
    # Wholly authored fixture, not original property names or shader source.
    return {"buffers": [{"name": "FixtureUniforms", "slot": 0,
                         "allocation_bytes": 112, "partial": True, "members": [
        dict(name="FixtureMatrix", kind="matrix", serialized_index=0,
             serialized_dimension=4, serialized_type=0, serialized_array_size=0),
        dict(name="FixtureScale", kind="vector", serialized_index=80,
             serialized_dimension=1, serialized_type=0, serialized_array_size=0),
        dict(name="FixtureTint", kind="vector", serialized_index=96,
             serialized_dimension=3, serialized_type=0, serialized_array_size=0),
    ]}]}


SOURCE = '''cbuffer cb7_struct : register(b3)
{
    float4 cb0_0_m0[7] : packoffset(c0);
};
float4 fixture_main() { return cb0_0_m0[1u] + cb0_0_m0[5u].xxxx + cb0_0_m0[6u]; }
'''


class UniformTests(unittest.TestCase):
    def test_offsets_columns_holes_and_descriptor_preserved(self):
        candidate, summary = rebind(SOURCE, fixture())
        self.assertIn('FixtureUniforms : register(b3)', candidate)
        self.assertIn('column_major float4x4 FixtureMatrix : packoffset(c0.x)', candidate)
        self.assertIn('float FixtureScale : packoffset(c5.x)', candidate)
        self.assertIn('float3 FixtureTint : packoffset(c6.x)', candidate)
        self.assertIn('transpose(FixtureMatrix)[1].x', candidate)
        self.assertIn('__raft_w5_hole_0_27 : packoffset(c6.w)', candidate)
        self.assertNotIn('cb0_0_m0', candidate)
        self.assertEqual(summary['unmapped_bytes_preserved'], 32)
        self.assertEqual(summary['static_register_reads_rebound'], 3)
        self.assertFalse(summary['unity_uniform_upload_verified'])

    def test_reject_unknown_type_array_matrix_orientation_shape(self):
        for field, value in [('serialized_type', 1), ('serialized_array_size', 2),
                             ('serialized_dimension', 3), ('serialized_index', 4)]:
            plan = fixture()
            plan['buffers'][0]['members'][0][field] = value
            with self.subTest(field=field), self.assertRaises(ValueError):
                rebind(SOURCE, plan)

    def test_compiler_global_buffer_keeps_named_fields(self):
        plan = fixture()
        plan['buffers'][0]['name'] = '$Globals'
        candidate, _ = rebind(SOURCE, plan)
        self.assertIn('cbuffer __raft_w5_Globals : register(b3)', candidate)
        self.assertIn('FixtureScale : packoffset(c5.x)', candidate)
        plan['buffers'][0]['name'] = '$Unknown'
        with self.assertRaises(ValueError):
            rebind(SOURCE, plan)

    def test_reject_ambiguous_names_overlap_and_slots(self):
        for case in range(4):
            plan = fixture()
            if case == 0:
                plan['buffers'][0]['members'][1]['name'] = 'FixtureMatrix'
            elif case == 1:
                plan['buffers'][0]['members'][1]['serialized_index'] = 16
            elif case == 2:
                plan['buffers'].append(copy.deepcopy(plan['buffers'][0]))
            else:
                plan['buffers'][0]['name'] = '__raft_w5_bad'
            with self.subTest(case=case), self.assertRaises(ValueError):
                rebind(SOURCE, plan)

    def test_reject_unsupported_reads_or_declarations(self):
        for source in [SOURCE.replace('[1u]', '[dynamic_index]'),
                       SOURCE.replace('[1u]', '[7u]'),
                       SOURCE.replace('cb0_0_m0', 'cb9_0_m0'),
                       SOURCE.replace('[7]', '[8]'),
                       SOURCE.replace('float4 cb0', 'uint4 cb0'),
                       SOURCE + 'cbuffer Other { float4 Unknown; };']:
            with self.subTest(source=source), self.assertRaises(ValueError):
                rebind(source, fixture())

    def test_preserves_nonuniform_arithmetic_and_no_zero_fallback(self):
        original = SOURCE.replace('return ', 'float sentinel = 0.375; return ')
        candidate, _ = rebind(original, fixture())
        self.assertIn('float sentinel = 0.375; return ', candidate)
        self.assertNotIn('= 0;', candidate)
        self.assertEqual(candidate.count('float4('), 3)


if __name__ == '__main__':
    unittest.main()
