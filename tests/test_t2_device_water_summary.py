"""Source-free tests of strict final device-water material totals."""
import unittest
from scripts.t2_device_water_summary import classify


def fixture():
    rows = {"spectrum": 8484, "foam_global": 15400, "subsurface_blur": 0,
            "utility_noise": 0, "other_ultimate_water": 0}
    return {"schema": 1, "session": "20261105-220911-559",
            "stop_time_android_process_exit_info": {
                "final_render_failure_breakdown": {"ultimate_water_invalid_pass_by_material": rows},
                "final_shader_pass_errors_total": 23884,
                "final_compute_kernel_errors_total": 3850,
                "final_error_category_breakdown": {"ultimate_water_invalid_pass": {"count": 23884}}}}


class TestDeviceWaterSummary(unittest.TestCase):
    def test_owner_aggregate(self):
        r = classify(fixture())
        self.assertEqual(r["by_material"]["foam_global"], 15400)
        self.assertEqual(r["water_pass_errors"], 23884)
        self.assertEqual(r["fft_kernel_errors_separate"], 3850)
        self.assertTrue(r["no_observed_blur_pass_error_is_not_pixel_validation"])

    def test_reject_missing_or_inconsistent_categories(self):
        for change in ("missing", "extra", "negative", "bool", "mismatch"):
            s = fixture()
            rows = s["stop_time_android_process_exit_info"]["final_render_failure_breakdown"]["ultimate_water_invalid_pass_by_material"]
            if change == "missing": rows.pop("foam_global")
            if change == "extra": rows["unknown"] = 0
            if change == "negative": rows["foam_global"] = -1
            if change == "bool": rows["foam_global"] = True
            if change == "mismatch": rows["foam_global"] += 1
            with self.subTest(change=change), self.assertRaises(ValueError):
                classify(s)

    def test_reject_category_root_mismatch(self):
        s = fixture()
        s["stop_time_android_process_exit_info"]["final_error_category_breakdown"]["ultimate_water_invalid_pass"]["count"] += 1
        with self.assertRaises(ValueError):
            classify(s)


if __name__ == "__main__":
    unittest.main()
