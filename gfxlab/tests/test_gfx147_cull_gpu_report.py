"""GFX147 synthetic source-free GPU Cull metric regressions; no original meshes."""
import unittest
import numpy as np

from gfxlab.tools.gfx147_cull_gpu_report import summarize


def pair():
    off = np.zeros((256, 256, 4), dtype=np.uint8)
    off[128, 65, :] = [10, 10, 10, 255]
    off[129, 66, :] = [20, 20, 20, 255]
    off[100, 100, :] = [30, 30, 30, 255]
    return off


class GFX147SourceFree(unittest.TestCase):
    def baseline(self):
        off = pair()
        back = off.copy()
        front = off.copy()
        return off, back, front

    def test_source_identical_controls_are_recognized(self):
        off, back, front = self.baseline()
        out = summarize(off, back, front, off.copy(), back.copy(), expected_source_coverage=3)
        self.assertTrue(out["off_repeat_exact"])
        self.assertTrue(out["back_repeat_exact"])
        self.assertTrue(out["back_vs_off"]["rgba_exact"])
        self.assertTrue(out["back_vs_off"]["coverage_mask_exact"])

    def test_outlier_inside_prior_hotspot_is_bounded(self):
        off, back, front = self.baseline()
        back[128, 65, 0] += 58
        front[100, 100, 0] += 59
        out = summarize(off, back, front, off.copy(), back.copy(), expected_source_coverage=3)
        self.assertEqual(out["back_vs_off"]["covered_rgb_difference_gt10_pixels"], 1)
        self.assertEqual(out["back_vs_off"]["covered_rgb_difference_gt10_in_previous_Adreno_hotspot_bbox"], 1)
        self.assertEqual(out["back_vs_off"]["covered_rgb_difference_gt10_outside_previous_hotspot_bbox"], 0)
        self.assertEqual(out["front_vs_off"]["covered_rgb_difference_gt10_outside_previous_hotspot_bbox"], 1)
        self.assertEqual(out["back_vs_off"]["covered_rgb_changed_bbox_xyxy"], [65,128,65,128])

    def test_rejects_original_coverage_drift(self):
        off, back, front = self.baseline()
        with self.assertRaisesRegex(ValueError, "coverage changed"):
            summarize(off, back, front, off.copy(), back.copy(), expected_source_coverage=3301)

    def test_rejects_nonbinary_alpha(self):
        off, back, front = self.baseline()
        back[129, 66, 3] = 17
        with self.assertRaisesRegex(ValueError, "Nonbinary"):
            summarize(off, back, front, off.copy(), back.copy(), expected_source_coverage=3)

    def test_rejects_wrong_image_dimensions(self):
        off, back, front = self.baseline()
        with self.assertRaisesRegex(ValueError, "shape or dtype"):
            summarize(off, back[:10], front, off.copy(), back.copy(), expected_source_coverage=3)

    def test_rejects_wrong_image_dtype(self):
        off, back, front = self.baseline()
        with self.assertRaisesRegex(ValueError, "shape or dtype"):
            summarize(off, back.astype(np.int32), front, off.copy(), back.copy(), expected_source_coverage=3)

    def test_rejects_nondeterministic_cull_back(self):
        off, back, front = self.baseline()
        second = back.copy()
        second[128, 65, 0] = 50
        with self.assertRaisesRegex(ValueError, "not deterministic"):
            summarize(off, back, front, off.copy(), second, expected_source_coverage=3)

    def test_rejects_gl_state_leak_after_disabling_culling(self):
        off, back, front = self.baseline()
        off_late = off.copy()
        off_late[128, 65, 0] = 50
        with self.assertRaisesRegex(ValueError, "baseline not restored"):
            summarize(off, back, front, off_late, back.copy(), expected_source_coverage=3)


if __name__ == "__main__":
    unittest.main()
