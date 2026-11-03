"""Synthetic fixtures only; actual original body is exercised privately in CI."""
import unittest
from scripts.adapt_android_render_lifetimes import guard_dynamic_resolution_timings

SOURCE = '''class DynamicResolution {
private void DetermineResolution() {
FrameTimingManager.CaptureFrameTimings();
    FrameTimingManager.GetLatestTimings(1u, frameTimings);
UseOriginalAlgorithm();
}
}
'''
class DynamicTimingTests(unittest.TestCase):
    def test_guard_rejects_missing_and_invalid_samples_before_algorithm(self):
        guarded = guard_dynamic_resolution_timings(SOURCE)
        self.assertIn('== 0u', guarded)
        self.assertIn('gpuFrameTime <= 0.0', guarded)
        self.assertIn('double.IsNaN', guarded)
        self.assertIn('double.IsInfinity', guarded)
        self.assertLess(guarded.index('== 0u'),guarded.index('UseOriginalAlgorithm'))
        self.assertEqual(guarded.count('CaptureFrameTimings()'),1)
        self.assertNotIn('ResizeBuffers(',guarded)

    def test_desktop_source_is_exactly_preserved(self):
        guarded = guard_dynamic_resolution_timings(SOURCE)
        lines=[];include=True
        for line in guarded.splitlines(keepends=True):
            token=line.strip()
            if token=='#if UNITY_ANDROID && !UNITY_EDITOR': include=False
            elif token=='#else': include=True
            elif token=='#endif': include=True
            elif include: lines.append(line)
        self.assertEqual(''.join(lines),SOURCE)

    def test_changed_timing_api_and_duplicate_reads_fail_closed(self):
        for source in (SOURCE.replace('GetLatestTimings(1u','GetLatestTimings(2u'),
                       SOURCE.replace('UseOriginalAlgorithm();','FrameTimingManager.GetLatestTimings(1u, frameTimings);')):
            with self.assertRaises(ValueError):guard_dynamic_resolution_timings(source)

if __name__=='__main__': unittest.main()
