"""GFX147.2 source-free negative/positive regressions for owner/Mesa pixel comparisons."""
import unittest

import numpy as np

from gfxlab.tools.gfx147_owner_cull_compare import rgba, compare_pixels


class SourceFreeCullCompareTests(unittest.TestCase):
    def make(self):
        x = np.zeros((256, 256, 4), dtype=np.uint8)
        x[128, 65] = [10,20,30,255]
        x[100,100] = [20,30,40,255]
        return x

    def test_exact_covered_color_differences_zero(self):
        ref=self.make()
        stats, delta=compare_pixels(ref,ref.copy(),ref[:,:,3]==255)
        self.assertEqual(stats["outlier_pixels_gt10"],0)
        self.assertEqual(stats["total_covered_rgb_abs_error"],0)
        self.assertEqual(stats["pixels_difference_any"],0)

    def test_one_high_error_pixel_counted_once_not_per_channel(self):
        ref=self.make()
        device=ref.copy()
        device[128,65,:3]=[65,90,85]
        stats, delta=compare_pixels(device,ref,ref[:,:,3]==255)
        self.assertEqual(stats["pixels_difference_any"],1)
        self.assertEqual(stats["outlier_pixels_gt10"],1)
        self.assertEqual(stats["outlier_pixels_gt30"],1)
        self.assertEqual(stats["max_rgb_channel_error"],70)

    def test_background_not_counted_in_covered_color_error(self):
        ref=self.make()
        device=ref.copy()
        device[1,1,:3]=255
        stats,_=compare_pixels(device,ref,ref[:,:,3]==255)
        self.assertEqual(stats["outlier_pixels_gt10"],0)

    def test_rejects_zero_geometry(self):
        ref=self.make()
        with self.assertRaisesRegex(ValueError,"Missing"):
            compare_pixels(ref,ref.copy(),np.zeros((256,256),dtype=bool))

    def test_rejects_wrong_image_shape(self):
        ref=self.make()
        with self.assertRaisesRegex(ValueError,"Wrong"):
            compare_pixels(ref[:128],ref,ref[:,:,3]==255)

    def test_rejects_wrong_coverage_shape(self):
        ref=self.make()
        with self.assertRaisesRegex(ValueError,"Wrong"):
            compare_pixels(ref,ref,np.ones((4,4),dtype=bool))

    def test_rejects_truncated_rgba_payload(self):
        with self.assertRaisesRegex(ValueError,"size"):
            rgba(b"synthetic-truncated")

    def test_256_squared_rgba_byte_order_is_preserved(self):
        ref=self.make()
        decoded=rgba(ref.tobytes())
        self.assertTrue(np.array_equal(ref,decoded))


if __name__ == "__main__":
    unittest.main()
