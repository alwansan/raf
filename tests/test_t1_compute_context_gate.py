"""Source-level regression contracts for T1's shared GLES compute driver.

These tests cannot create an Android EGL context. Actual GLES 3.1 compute
correctness must be established on the owner's phone; Java compilation is an
independent CI gate. Keep this test separate from Unity FFT acceptance.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
PROBE = (ROOT / "apk-for-testing/host/app/src/main/java/com/alwansan/raftlab/T1ComputeProbe.java").read_text(encoding="utf-8")
HOST = (ROOT / "apk-for-testing/host/app/src/main/java/com/alwansan/raftlab/MainActivity.java").read_text(encoding="utf-8")


class T1ComputeContextGateTests(unittest.TestCase):
    def test_prevents_early_auto_dispatch(self):
        method = PROBE.split("private void waitForAutoContext(", 1)[1].split("void onPause()", 1)[0]
        self.assertIn("if(!ready)", method)
        self.assertIn("view.postDelayed(()->waitForAutoContext", method)
        self.assertIn("view.queueEvent(", method)
        self.assertLess(method.index("if(!ready)"), method.index("view.queueEvent("))
        # The not-ready branch MUST return before enqueueing GPU work.
        self.assertRegex(method, r"if\(!ready\)\s*\{[\s\S]*?view\.postDelayed\([\s\S]*?return;")
        self.assertIn("SETUP_CONTEXT_TIMEOUT", method)
        self.assertIn("no compute dispatch attempted", method)

    def test_timeout_is_bounded_below_host_warning(self):
        timeout = int(re.search(r"AUTO_CONTEXT_TIMEOUT_MS\s*=\s*(\d+)L", PROBE).group(1))
        poll = int(re.search(r"AUTO_CONTEXT_POLL_MS\s*=\s*(\d+)L", PROBE).group(1))
        self.assertGreaterEqual(timeout, 1500)
        self.assertLess(timeout, 18000)
        self.assertGreater(poll, 0)
        self.assertLessEqual(poll, 250)
        self.assertIn("android.os.SystemClock.elapsedRealtime()", PROBE)

    def test_render_context_readiness_and_cleanup(self):
        self.assertIn("onSurfaceCreated(GL10 gl, EGLConfig config)", PROBE)
        self.assertIn("ready=true;", PROBE)
        self.assertIn("void onPause(){ready=false;view.onPause();}", PROBE)
        self.assertIn("activity.isFinishing()||activity.isDestroyed()", PROBE)

    def test_only_known_compiled_cases_and_no_fake_gpu_success(self):
        self.assertIn('caseId.matches("T1-0[1-5]")', PROBE)
        self.assertIn("glDispatchCompute(4,1,1)", PROBE)
        self.assertIn('if(id.equals("T1-05"))return T1FftButterflyProbe.run();', PROBE)
        self.assertIn("glMapBufferRange(", PROBE)
        self.assertIn("glMemoryBarrier(", PROBE)
        self.assertIn("glGetShaderiv(shader,GLES20.GL_COMPILE_STATUS", PROBE)
        self.assertIn('if(!ready)return "FAIL no active GLES context"', PROBE)
        self.assertIn('value.startsWith("PASS")?"PASS":"FAIL"', HOST)
        self.assertNotIn("JSONObject.getString(\"glsl\")", PROBE)

    def test_auto_bridge_is_real_child_activity(self):
        self.assertIn('i.putExtra("auto_case_id",id)', (ROOT / "apk-for-testing/unified/app/src/main/java/com/alwansan/raftlab/UnifiedLabActivity.java").read_text(encoding="utf-8"))
        self.assertIn("t1Probe.runAutomated(id,value->", HOST)


if __name__ == "__main__":
    unittest.main()
