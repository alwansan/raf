import copy
import json
import unittest
from scripts.probe_original_fft_resource_bindings import correlate, sha
from scripts.probe_fft_variant_table import EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT


class ResourceBindingTests(unittest.TestCase):
    def fixture(self):
        def resource(name, bind):
            return dict(name=name, bindPoint=bind, texDimension=2, samplerBindPoint=-1)
        tree = {'variants': [{'kernels': []}]}
        for x in EXPECTED_FFT_WORKGROUP_X_BY_COMPILED_SLOT:
            entry = dict(cbs=[], inBuffers=[], builtinSamplers=[],
                         textures=[resource('PrivateInput',0),resource('PrivateWeights',1)],
                         outBuffers=[resource('PrivateOutput',0)],threadGroupSize=[x,1,1])
            tree['variants'][0]['kernels'].append({'variantMap':[('',entry)]})
        source = '''class Example {
 void Run() {
  cs.SetTexture(index, "PrivateWeights", weights);
  cs.SetTexture(index, "PrivateInput", source);
  cs.SetTexture(index, "PrivateOutput", temporary);
  cs.Dispatch(index, 1, source.height, 1);
  cs.SetTexture(index+1, "PrivateWeights", weights);
  cs.SetTexture(index+1, "PrivateInput", temporary);
  cs.SetTexture(index+1, "PrivateOutput", target);
  cs.Dispatch(index+1, 1, source.height, 1);
 }
}'''
        return tree, source

    def test_all_program_roles_and_two_pass_intermediate_match(self):
        tree, source = self.fixture()
        result = correlate(tree, source, sha(source))
        self.assertEqual(result['compiled_slots_with_csharp_resource_names_matched'],20)
        self.assertTrue(result['two_pass_intermediate_output_to_input_matched'])
        self.assertTrue(result['same_butterfly_image_both_passes'])
        self.assertFalse(result['unity_runtime_kernel_indices_verified'])
        self.assertFalse(result['image_formats_and_numeric_outputs_verified'])
        self.assertNotIn('Private',json.dumps(result))
        self.assertNotIn('temporary',json.dumps(result))

    def test_modified_source_hash_is_refused(self):
        tree, source = self.fixture()
        with self.assertRaisesRegex(ValueError,'SHA256'):
            correlate(tree,source,'0'*64)

    def test_wrong_resource_name_or_dimension_is_refused(self):
        tree, source = self.fixture()
        for key, value in [('name','Wrong'),('texDimension',3),('samplerBindPoint',0)]:
            wrong=copy.deepcopy(tree)
            wrong['variants'][0]['kernels'][7]['variantMap'][0][1]['textures'][0][key]=value
            with self.assertRaises(ValueError):correlate(wrong,source,sha(source))

    def test_missing_extra_or_duplicate_registers_are_refused(self):
        tree, source = self.fixture()
        for mode in ('missing','extra','duplicate'):
            wrong=copy.deepcopy(tree);resources=wrong['variants'][0]['kernels'][0]['variantMap'][0][1]['textures']
            if mode=='missing':resources.pop()
            elif mode=='extra':resources.append(copy.deepcopy(resources[0]))
            else:resources[1]['bindPoint']=0
            with self.assertRaises(ValueError):correlate(wrong,source,sha(source))

    def test_broken_intermediate_or_changed_butterfly_is_refused(self):
        tree, source = self.fixture()
        for wrong in (source.replace('"PrivateInput", temporary','"PrivateInput", other'),
                      source.replace('index+1, "PrivateWeights", weights','index+1, "PrivateWeights", changed')):
            with self.assertRaisesRegex(ValueError,'dataflow'):correlate(tree,wrong,sha(wrong))

    def test_dispatch_offset_or_row_count_drift_is_refused(self):
        tree, source = self.fixture()
        for wrong in (source.replace('Dispatch(index+1','Dispatch(index+2'),
                      source.replace('Dispatch(index+1, 1, source.height','Dispatch(index+1, 2, source.height'),
                      source.replace('Dispatch(index+1, 1, source.height','Dispatch(index+1, 1, other.height')):
            with self.assertRaises(ValueError):correlate(tree,wrong,sha(wrong))

    def test_secondary_dispatch_shape_ignores_comments_strings_and_chars(self):
        tree, source = self.fixture()
        # The primary callsite audit masks non-code, but the secondary
        # dispatch-shape audit previously searched the raw original C# text.
        fake = (
            '  // cs.Dispatch(index, 99, fake.height, 9);\n'
            '  /* cs.Dispatch(index, 3, fake.height, 4); */\n'
            '  string quoted = "cs.Dispatch(index, 77, fake.height, 7)";\n'
            "  char example = 'D';\n"
            '  string verbatim = @"cs.Dispatch(index, 88, fake.height, 8)";\n'
        )
        marked = source.replace('  cs.Dispatch(index, 1, source.height, 1);',
                                fake + '  cs.Dispatch(index, 1, source.height, 1);')
        result = correlate(tree, marked, sha(marked))
        self.assertEqual(result['dispatch_x_groups'], 1)
        self.assertEqual(result['dispatch_z_groups'], 1)
        self.assertTrue(result['dispatch_y_same_original_texture_height_expression'])

        # An inert commented Dispatch must never replace a missing real call.
        missing = marked.replace('cs.Dispatch(index+1, 1, source.height, 1);',
                                 'cs.NoDispatch(index+1, 1, source.height, 1);')
        with self.assertRaises(ValueError):
            correlate(tree, missing, sha(missing))

    def test_slot_workgroup_order_is_required(self):
        tree, source = self.fixture();wrong=copy.deepcopy(tree)
        wrong['variants'][0]['kernels'][2]['variantMap'][0][1]['threadGroupSize']=[64,1,1]
        with self.assertRaisesRegex(ValueError,'workgroup'):correlate(wrong,source,sha(source))
