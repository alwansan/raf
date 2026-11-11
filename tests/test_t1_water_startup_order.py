import unittest
from scripts.t1_water_startup_order import analyze

def fixture():
    return {"session":"fixture",
            "final_error_category_breakdown":{
                "ultimate_water_invalid_pass":{"count":3,"first_observed_unix_ms":100},
                "water_fft_invalid_compute_kernel":{"count":1,"first_observed_unix_ms":102}},
            "final_game_milestones":{"world_loaded_message_observed":{"count":1,"first_observed_unix_ms":500}},
            "final_render_failure_breakdown":{
                "ultimate_water_invalid_pass_by_material":{"spectrum":1,"foam_global":2},
                "invalid_kernel_index_root_lines":{"index_6":1}}}

class TestOrder(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(analyze(fixture())["water_before_world_ms"],400)
    def test_material_partition(self):
        x=fixture();x["final_render_failure_breakdown"]["ultimate_water_invalid_pass_by_material"]["foam_global"]=0
        with self.assertRaises(ValueError):analyze(x)
    def test_kernel_partition(self):
        x=fixture();x["final_render_failure_breakdown"]["invalid_kernel_index_root_lines"]["index_6"]=0
        with self.assertRaises(ValueError):analyze(x)
    def test_missing_world(self):
        x=fixture();x["final_game_milestones"]["world_loaded_message_observed"]["count"]=0
        with self.assertRaises(ValueError):analyze(x)
    def test_wrong_order(self):
        x=fixture();x["final_error_category_breakdown"]["water_fft_invalid_compute_kernel"]["first_observed_unix_ms"]=600
        with self.assertRaises(ValueError):analyze(x)

if __name__=="__main__":
    unittest.main()
