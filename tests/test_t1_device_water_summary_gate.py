"""Synthetic regression fixtures for the device water root-accounting gate."""
import unittest
from scripts.t1_device_water_summary_gate import summarize

def fixture():
    return {'session': '20261105-220911-559',
            'final_render_failure_breakdown': {
                'ultimate_water_invalid_pass_by_material': {
                    'spectrum': 8484, 'foam_global': 15400, 'subsurface_blur': 0,
                    'utility_noise': 0, 'other_ultimate_water': 0},
                'invalid_kernel_index_root_lines': {'index_6': 3850, 'other_index': 0}},
            'final_error_category_breakdown': {
                'ultimate_water_invalid_pass': {'count': 23884},
                'water_fft_invalid_compute_kernel': {'count': 3850}},
            'final_shader_pass_errors_total': 23884,
            'final_compute_kernel_errors_total': 3850}

class GateTests(unittest.TestCase):
    def test_real_summary_aggregate(self):
        result = summarize(fixture())
        self.assertEqual(result['invalid_pass_total'], 23884)
        self.assertFalse(result['kernel_index_6_is_fft_proven'])

    def test_second_session(self):
        s = fixture()
        s['final_render_failure_breakdown']['ultimate_water_invalid_pass_by_material'].update(spectrum=15028, foam_global=24104)
        s['final_render_failure_breakdown']['invalid_kernel_index_root_lines']['index_6'] = 6026
        s['final_error_category_breakdown']['ultimate_water_invalid_pass']['count'] = 39132
        s['final_error_category_breakdown']['water_fft_invalid_compute_kernel']['count'] = 6026
        s['final_shader_pass_errors_total'] = 39132
        s['final_compute_kernel_errors_total'] = 6026
        self.assertEqual(summarize(s)['invalid_kernel_total'], 6026)

    def test_mismatch_rejected(self):
        s = fixture()
        s['final_render_failure_breakdown']['ultimate_water_invalid_pass_by_material']['spectrum'] += 1
        with self.assertRaises(ValueError):
            summarize(s)

    def test_bad_counts_rejected(self):
        for value in (-1, True, 1.5):
            s = fixture()
            s['final_render_failure_breakdown']['invalid_kernel_index_root_lines']['index_6'] = value
            with self.assertRaises(ValueError):
                summarize(s)

    def test_unrecognized_index_rejected(self):
        s = fixture()
        s['final_render_failure_breakdown']['invalid_kernel_index_root_lines']['index_7'] = 0
        with self.assertRaises(ValueError):
            summarize(s)

if __name__ == '__main__':
    unittest.main()
