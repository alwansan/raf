import unittest

from scripts.t1_fft_local_store_writers import analyze


HEAD = """
OpDecorate %source DescriptorSet 0
OpDecorate %source Binding 0
OpDecorate %butter DescriptorSet 0
OpDecorate %butter Binding 1
%f32 = OpTypeFloat 32
%i32 = OpTypeInt 32 1
%v2f = OpTypeVector %f32 2
%v2i = OpTypeVector %i32 2
%ptr = OpTypePointer Function %v2f
%local = OpVariable %ptr Function
%floatcoord = OpCompositeConstruct %v2f %zero %zero
%zero = OpConstant %f32 0
%sourceCoord = OpBitcast %v2i %floatcoord
%sourceFetch = OpImageFetch %v2f %source %sourceCoord
"""
TAIL = """
%read = OpLoad %v2f %local
%cast = OpBitcast %v2i %read
%butter1 = OpImageFetch %v2f %butter %cast
%butter2 = OpImageFetch %v2f %butter %cast
"""


class LocalWriterTests(unittest.TestCase):
    def test_single_direct_store_is_candidate_not_proof(self):
        text = HEAD + "%producer = OpIAdd %v2i %vectorInt %vectorInt\n%written = OpBitcast %v2f %producer\nOpStore %local %written\n" + TAIL
        report = analyze(text, require_original_layout=True)
        self.assertEqual([s['role'] for s in report['sites']], ['source', 'butterfly', 'butterfly'])
        site = report['sites'][1]
        self.assertEqual(site['lanes']['x']['direct_store_candidates'], 1)
        self.assertEqual(site['lanes']['x']['writer_opcodes'], {'OpBitcast': 1})
        self.assertEqual(site['lanes']['x']['writer_numeric_kinds'], {'float32': 1})
        self.assertEqual(site['lanes']['x']['lane_bitcasts'], {'float32_to_sint32': 1})
        self.assertFalse(site['lanes']['x']['reaching_definition_proven'])
        self.assertNotIn('%', str(report))

    def test_multiple_stores_remain_ambiguous(self):
        text = HEAD + "OpStore %local %floatcoord\nOpStore %local %floatcoord\n" + TAIL
        writer = analyze(text)['sites'][1]['lanes']['y']
        self.assertEqual(writer['direct_store_candidates'], 2)
        self.assertFalse(writer['reaching_definition_proven'])

    def test_no_store_does_not_claim_uninitialized_value(self):
        writer = analyze(HEAD + TAIL)['sites'][1]['lanes']['x']
        self.assertEqual(writer['direct_store_candidates'], 0)
        self.assertFalse(writer['reaching_definition_proven'])

    def test_indirect_pointer_cannot_be_assigned_direct_writers(self):
        text = HEAD + "%alias = OpCopyObject %ptr %local\n%read = OpLoad %v2f %alias\n%cast = OpBitcast %v2i %read\n%butter1 = OpImageFetch %v2f %butter %cast\n%butter2 = OpImageFetch %v2f %butter %cast\n"
        self.assertEqual(analyze(text)['sites'][1]['lanes']['x']['boundary'], 'nonlocal_or_indirect_load')

    def test_constant_lane_is_not_reported_as_writer(self):
        text = HEAD + "%read = OpLoad %v2f %local\n%x = OpCompositeExtract %f32 %read 0\n%both = OpCompositeConstruct %v2f %x %zero\n%cast = OpBitcast %v2i %both\n%butter1 = OpImageFetch %v2f %butter %cast\n%butter2 = OpImageFetch %v2f %butter %cast\n"
        report = analyze(text)['sites'][1]['lanes']
        self.assertEqual(report['x']['boundary'], 'function_load')
        self.assertEqual(report['y']['boundary'], 'constant')

    def test_wrong_role_or_duplicate_binding_rejected(self):
        with self.assertRaises(ValueError):
            analyze(HEAD.replace('OpDecorate %butter Binding 1', 'OpDecorate %butter Binding 2') + TAIL,
                    require_original_layout=True)
        with self.assertRaises(ValueError):
            analyze(HEAD + 'OpDecorate %butter Binding 1\n' + TAIL)

    def test_bound_on_static_stores(self):
        with self.assertRaisesRegex(ValueError, 'store count'):
            analyze(HEAD + ('OpStore %local %floatcoord\n' * 33) + TAIL)

    def test_no_spirv_ids_in_sanitized_report(self):
        report = analyze(HEAD + 'OpStore %local %floatcoord\n' + TAIL)
        self.assertNotIn('%source', str(report))
        self.assertNotIn('%local', str(report))
        self.assertTrue(report['direct_writers_are_static_candidates_only'])


if __name__ == '__main__':
    unittest.main()
