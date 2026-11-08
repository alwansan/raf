"""Source-only T3 shared-frame evidence guards; NOT a GLES/Android device test."""
from pathlib import Path
import unittest

SRC=(Path(__file__).resolve().parents[1]/"apk-for-testing/unified/app/src/main/java/com/alwansan/raft/t3lab/T3LabActivity.java")

class T3SharedFramePolicy(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.code=SRC.read_text(encoding="utf-8")

    def test_same_case_render_ack_before_pixelcopy(self):
        c=self.code
        self.assertIn('lastRenderedSequence==sequence && lastRenderedCase==idx',c)
        self.assertIn('waitForSharedRender(id,idx,sequence,deadline)',c)
        self.assertIn('lastRenderedSequence!=renderSequence',c)
        self.assertIn('Case changed during PixelCopy',c)
        self.assertNotIn('postDelayed(()->captureSharedEvidence(id),1000)',c)

    def test_no_placeholder_success_on_gl_failure_or_timeout(self):
        c=self.code
        self.assertIn('finishSharedEvidence(id,"FAIL",null,"GLES case assertion failed:',c)
        self.assertIn('finishSharedEvidence(id,"FAIL",null,"No matching GLES frame',c)
        self.assertIn('lastRenderedAssertion=colors && glError==GLES30.GL_NO_ERROR',c)
        self.assertIn('lastRenderedError=GLES30.GL_INVALID_OPERATION',c)

    def test_real_readback_for_six_synthetic_cases(self):
        c=self.code
        self.assertIn('GLES30.glReadPixels(',c)
        self.assertIn('int[] left=pixel(',c)
        self.assertIn('int[] right=pixel(',c)
        for i in range(6):self.assertIn('case '+str(i)+': return',c)
        self.assertIn('left[0]>right[0]+20',c)
        self.assertIn('case 3: return left[0]>45',c)
        self.assertIn('Math.abs(left[0]-right[0])<=18',c)
        self.assertIn('negativeChecked && negativeRejected',c)

    def test_evidence_not_called_visual_pass(self):
        c=self.code
        self.assertIn('"EVIDENCE_READY",uri,"GLES synthetic frame, visual review still required"',c)
        self.assertIn('"NEEDS_SCREENSHOT"',c)
        self.assertIn('PixelCopy.request(getWindow(),bmp',c)
        self.assertNotIn('finishSharedEvidence(id,"PASS"',c)

    def test_select_and_render_snapshot_have_shared_lock(self):
        c=self.code
        self.assertIn('synchronized(lock){caseIndex=index;renderSequence++;lastRenderedSequence=-1;}',c)
        self.assertIn('synchronized(lock){current=caseIndex;generation=renderSequence;}',c)
        self.assertIn('lastRenderedSequence=generation;',c)

if __name__=="__main__":unittest.main()
