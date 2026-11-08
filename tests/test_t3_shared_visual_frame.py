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
        self.assertIn('finishSharedEvidence(id,"EVIDENCE_READY",uri,',c)
        self.assertIn('png_sha256=',c)
        self.assertIn('visual review still required',c)
        self.assertIn('"NEEDS_SCREENSHOT"',c)
        self.assertIn('PixelCopy.request(getWindow(),bmp',c)
        self.assertNotIn('finishSharedEvidence(id,"PASS"',c)

    def test_select_and_render_snapshot_have_shared_lock(self):
        c=self.code
        self.assertIn('synchronized(lock){caseIndex=index;renderSequence++;lastRenderedSequence=-1;}',c)
        self.assertIn('synchronized(lock){current=caseIndex;generation=renderSequence;}',c)
        self.assertIn('lastRenderedSequence=generation;',c)

    def test_png_not_published_until_readback_verified(self):
        c=self.code
        region=c.split('void captureSharedEvidence(String id){',1)[1].split(
            '/** PNG signature + terminal IEND;',1)[0]
        issued=region.index('v.put(MediaStore.MediaColumns.IS_PENDING,1)')
        write=region.index('out.write(png);out.flush()')
        first_check=region.index('verifyPngReadback(dest,png.length,sha)')
        visible=region.index('visible.put(MediaStore.MediaColumns.IS_PENDING,0)')
        publish=region.index('getContentResolver().update(dest,visible,null,null)!=1')
        second_check=region.index('verifyPngReadback(dest,png.length,sha)',first_check+1)
        accepted=region.index('finishSharedEvidence(id,"EVIDENCE_READY",uri,')
        self.assertTrue(issued<write<first_check<visible<publish<second_check<accepted)
        self.assertIn('getContentResolver().delete(dest,null,null)',region)
        self.assertIn('finishSharedEvidence(id,"NEEDS_SCREENSHOT",null,',region)
        self.assertNotIn('finishSharedEvidence(id,"PASS"',region)

    def test_png_digest_envelope_and_stalled_stream_fail_closed(self):
        c=self.code
        self.assertIn('if(!isCompletePng(png))throw new IOException',c)
        self.assertIn('static boolean isCompletePng(byte[] bytes)',c)
        self.assertIn('static String hexDigest(byte[] bytes)',c)
        self.assertIn('void verifyPngReadback(Uri uri,int expectedBytes,String expectedSha)',c)
        self.assertIn('if(count!=expectedBytes||!hash.toString().equals(expectedSha))',c)
        self.assertIn('if(count>expectedBytes)throw new IOException',c)
        self.assertIn('if(++zeroReads>3)throw new IOException',c)
        self.assertIn('MediaStore.Downloads.RELATIVE_PATH',c)
        self.assertIn('dest=getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,v)',c)
        self.assertIn('if(dest==null)throw new IOException',c)

if __name__=="__main__":unittest.main()
