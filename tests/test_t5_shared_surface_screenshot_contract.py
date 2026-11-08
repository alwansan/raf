"""Owner-proven T3 screenshot parity: generated PNG must contain verified GLES layer."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
T3 = ROOT/"apk-for-testing/unified/app/src/main/java/com/alwansan/raft/t3lab/T3LabActivity.java"
POLICY = ROOT/"apk-for-testing/unified/app/src/main/java/com/alwansan/raftlab/SharedSurfacePixelPolicy.java"
BUILD = ROOT/"apk-for-testing/unified/app/build.gradle"


class OwnerSurfaceScreenshotContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=T3.read_text(encoding="utf-8")
        cls.policy=POLICY.read_text(encoding="utf-8")
        cls.gradle=BUILD.read_text(encoding="utf-8")

    def test_pixelcopy_actual_gles_surface_and_window_composite(self):
        self.assertIn("PixelCopy.request(surface,gpu,result->",self.source)
        self.assertIn("PixelCopy.request(getWindow(),window,code->",self.source)
        self.assertIn("canvas.drawBitmap(gpu,",self.source)
        self.assertIn("getLocationInWindow",self.source)
        self.assertNotIn("Math.min(decor.getHeight(),900)",self.source)
        self.assertNotIn("Math.min(decor.getWidth(),1600)",self.source)

    def test_fail_closed_on_black_or_stale(self):
        self.assertIn("SharedSurfacePixelPolicy.validate(gpuLeft,gpuRight,photoLeft,photoRight)",self.source)
        self.assertIn("screenshot_pixel_mismatch",self.source)
        self.assertIn('finishSharedEvidence(id,"NEEDS_SCREENSHOT"',self.source)
        self.assertIn("sameRenderedFrame(expected,generation)",self.source)
        self.assertIn("verified_surface_pixels=true",self.source)
        self.assertIn("if(attempt<2)",self.source)
        self.assertIn("image SurfaceView is blank/black",self.policy)
        self.assertIn("PixelCopy SurfaceView pixels differ from GLES readback",self.policy)

    def test_media_store_png_bytes_still_verified(self):
        self.assertIn("IS_PENDING,1",self.source)
        self.assertIn("verifyPngReadback(dest,png.length,sha)",self.source)
        self.assertIn("IS_PENDING,0",self.source)
        self.assertIn("getContentResolver().delete(dest,null,null)",self.source)
        self.assertIn("isCompletePng(png)",self.source)

    def test_render_backend_left_unmodified_and_capture_part_of_driver_hash(self):
        self.assertIn("GLES30.glReadPixels(x,y,1,1",self.source)
        self.assertIn("glGetError()",self.source)
        self.assertIn("case=CASE0",self.source)
        self.assertIn("SharedSurfacePixelPolicy.java",self.gradle)
        self.assertEqual(len(re.findall(r"case [0-5]:",self.source)),12) # pixel contract and six GLSL draw cases
        self.assertNotIn("com.tencent.",self.source)


if __name__ == "__main__":
    unittest.main()
