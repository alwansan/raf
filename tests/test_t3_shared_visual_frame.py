"""Source-only T3 shared-frame evidence guards; NOT a GLES/Android device test."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/"apk-for-testing/unified/app/src/main/java/com/alwansan/raft/t3lab/T3LabActivity.java"
HOST=ROOT/"apk-for-testing/unified/app/src/main/java/com/alwansan/raftlab/UnifiedLabActivity.java"
MANIFEST=ROOT/"apk-for-testing/unified/app/src/main/AndroidManifest.xml"

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
        self.assertIn('String gpu=lastRenderedNote;',c)
        self.assertIn('if(gpu==null||gpu.length()<30||gpu.length()>700)',c)
        self.assertIn('"GLES synthetic frame; "+gpu+"; png_bytes="',c)
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

    def test_manual_t3_preview_is_explicit_arabic_and_keeps_screen_open(self):
        c=self.code
        self.assertIn('manualPreviewCase=getIntent()==null?',c)
        self.assertIn('manualPreviewCase.matches("T3-0[1-6]")',c)
        self.assertIn('if(manualPreviewCase!=null)scroll.setVisibility(View.GONE)',c)
        self.assertIn('button(actions,"📷 التقاط صورة هذا الاختبار والعودة إلى النتائج"',c)
        self.assertIn('void captureManualPreview()',c)
        self.assertIn('if(manualPreviewCase==null||manualCaptureStarted)return;',c)
        self.assertIn('waitForSharedRender(manualPreviewCase,idx,sequence,',c)
        self.assertIn('if(manualPreviewCase!=null){\n            select(',c)
        self.assertIn('شاهد الرسم الآن',c)
        self.assertNotIn('finishSharedEvidence(id,"PASS"',c)

    def test_host_t3_tap_and_manual_run_launch_real_preview(self):
        host=HOST.read_text(encoding="utf-8")
        self.assertIn('T3_VISUAL_PREVIEW=406',host)
        self.assertIn('void launchT3VisualCase(JSONObject c)',host)
        self.assertIn('intent.putExtra("manual_case_id",id)',host)
        self.assertIn('intent.putExtra("shared_session",session)',host)
        self.assertIn('startActivityForResult(intent,T3_VISUAL_PREVIEW)',host)
        self.assertIn('launchT3VisualCase(c);',host)
        self.assertIn('launchT3VisualCase(currentManual);',host)
        self.assertIn('t3CaseButtons=new LinearLayout(this)',host)
        self.assertIn('addButton(t3CaseButtons,"▶ فتح "+id+',host)
        self.assertIn('v->openPending(c)',host)
        self.assertIn('if(req==T3_VISUAL_PREVIEW)',host)
        self.assertIn('!expected.equals(data.getStringExtra("case_id"))',host)
        self.assertIn('if("EVIDENCE_READY".equals(verdict)&&!screenshotValid(uri))',host)
        self.assertIn('store(currentManual,verdict,',host)
        self.assertNotIn('store(currentManual,"PASS"',host)

    def test_portrait_owner_change_and_arabic_ui_are_not_replaced(self):
        host=HOST.read_text(encoding="utf-8")
        manifest=MANIFEST.read_text(encoding="utf-8")
        self.assertIn('android:screenOrientation="portrait"',manifest)
        self.assertIn('ArabicLabStrings.title(',host)
        self.assertIn('مختبر رافت الموحد',host)
        self.assertIn('النتيجة المتوقعة',self.code)

if __name__=="__main__":unittest.main()
