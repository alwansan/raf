package com.alwansan.raft.t3lab;

import android.app.Activity;
import android.graphics.Bitmap;
import android.graphics.Canvas;
import android.graphics.Paint;
import com.alwansan.raftlab.SharedSurfacePixelPolicy;
import android.view.PixelCopy;
import com.alwansan.raftlab.BuildConfig;
import android.content.ContentValues;
import android.content.Intent;
import android.graphics.PixelFormat;
import android.net.Uri;
import android.opengl.GLES30;
import android.opengl.GLSurfaceView;
import android.os.Build;
import android.os.Handler;
import android.os.Looper;
import android.os.Bundle;
import android.os.Environment;
import android.os.SystemClock;
import android.provider.MediaStore;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.HorizontalScrollView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.File;
import java.io.FileOutputStream;
import java.io.ByteArrayOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.FloatBuffer;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Date;
import java.util.Locale;
import java.text.SimpleDateFormat;
import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;

/** No Raft assets or executable testpacks. Synthetic GLES3 diagnostics, not Unity proof. */
public final class T3LabActivity extends Activity {
    static final String[] TITLES = {"الألوان الأساسية وبطاقة الرسوميات","تدرّج ألوان الزوايا",
        "دخان أحمر شفاف فوق الأزرق","مقارنة طريقتين للشفافية",
        "اختبار الإضاءة بين UNORM وsRGB","التحقق من رفض شيدر خاطئ"};
    static final String[] EXPECTED = {"ثلاثة أعمدة واضحة: أحمر وأخضر وأزرق. معلومات المعالج الرسومي في السجل.",
        "تدرّج ملون بين الزوايا، وليس بطاقة بيضاء بالكامل.",
        "ظهور الخلفية الزرقاء من خلال الطبقة الحمراء الشفافة؛ دون مربع أحمر معتم.",
        "ظهور لوحتين متقاربتين في اللون وليستا سوداوين.",
        "الجزء الأيمن أغمق من الجزء الأيسر عند فك ترميز sRGB.",
        "رفض الشيدر غير الصالح مع استمرار ظهور شاشة زرقاء مرئية."};
    static final String[] STEPS = {"انظر إلى الألوان الثلاثة ثم التقط الصورة.",
        "انظر إلى الأطراف والمنتصف؛ هل التدرج طبيعي؟",
        "تأكد أن اللون الأحمر شفاف فوق الخلفية الزرقاء.",
        "قارن لون اللوحتين، وتحقق من عدم اختفاء الألوان.",
        "قارن السطوع: يسار الصورة أكثر إضاءة من يمينها.",
        "يجب أن يظهر رسم احتياطي أزرق رغم رفض الشيدر الخاطئ."};
    static final int PICK_TESTPACK=61;
    final Object lock=new Object();
    File logfile;
    String session, testId="CASE01", packId="builtin", packHash="none";
    JSONObject packOverrides=new JSONObject();
    GLSurfaceView surface;
    Painter painter;
    TextView instructions, status;
    EditText note;
    volatile int caseIndex=0;
    volatile int renderSequence=0, lastRenderedSequence=-1, lastRenderedCase=-1;
    volatile int lastRenderedError=GLES30.GL_INVALID_OPERATION;
    volatile boolean lastRenderedAssertion=false;
    volatile String lastRenderedNote="لم يكتمل رسم إطار GLES بعد";
    volatile int[] lastRenderedLeft=null, lastRenderedRight=null;
    boolean manualCaptureStarted=false;
    String manualPreviewCase=null;

    TextView text(String value) { TextView t=new TextView(this); t.setText(value);
        t.setTextSize(15);t.setPadding(6,4,6,4);return t; }
    void button(LinearLayout parent,String name,View.OnClickListener action) {
        Button b=new Button(this);b.setText(name);parent.addView(b);b.setOnClickListener(action);
    }
    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        session=new SimpleDateFormat("yyyyMMdd-HHmmss",Locale.US).format(new Date())
            +"-"+SystemClock.elapsedRealtime();
        File dir=new File(getFilesDir(),"sessions");if(!dir.exists()&&!dir.mkdirs())
            throw new IllegalStateException("Cannot create app-private log directory");
        logfile=new File(dir,"events-"+session+".jsonl");
        manualPreviewCase=getIntent()==null?null:getIntent().getStringExtra("manual_case_id");
        if(manualPreviewCase!=null&&!manualPreviewCase.matches("T3-0[1-6]"))manualPreviewCase=null;
        LinearLayout page=new LinearLayout(this);page.setOrientation(LinearLayout.VERTICAL);
        page.setLayoutDirection(View.LAYOUT_DIRECTION_RTL);
        page.setPadding(10,10,10,10);
        setContentView(page);
        page.addView(text("مختبر رسوميات T3 | اختبار اصطناعي للألوان، وليس لعبة Raft | "+
            BuildConfig.SOURCE_SHA.substring(0,Math.min(10,BuildConfig.SOURCE_SHA.length()))));
        HorizontalScrollView scroll=new HorizontalScrollView(this);
        LinearLayout choices=new LinearLayout(this);
        for(int i=0;i<6;i++){final int index=i;button(choices,"CASE0"+(i+1),v->select(index));}
        scroll.addView(choices);page.addView(scroll);
        if(manualPreviewCase!=null)scroll.setVisibility(View.GONE);
        instructions=text("");page.addView(instructions);
        surface=new GLSurfaceView(this);surface.setEGLContextClientVersion(3);
        surface.getHolder().setFormat(PixelFormat.RGBA_8888);
        painter=new Painter();surface.setRenderer(painter);
        surface.setRenderMode(GLSurfaceView.RENDERMODE_WHEN_DIRTY);
        page.addView(surface,new LinearLayout.LayoutParams(-1,0,1));
        note=new EditText(this);note.setSingleLine(true);
        note.setHint("ملاحظتك عن الرسم (حتى 800 حرف)");
        LinearLayout actions=new LinearLayout(this);
        actions.setOrientation(LinearLayout.VERTICAL);
        if(manualPreviewCase!=null){
            page.addView(actions);
            button(actions,"📷 التقاط صورة هذا الاختبار والعودة إلى النتائج",v->captureManualPreview());
            button(actions,"↩ رجوع دون حفظ نتيجة",v->finish());
        }else{
            page.addView(note);
            page.addView(actions);
            button(actions,"نجاح في المشاهدة",v->result("PASS"));
            button(actions,"فشل في المشاهدة",v->result("FAIL"));
            button(actions,"نتيجة غير متوقعة",v->result("UNEXPECTED"));
            button(actions,"استيراد ملف T3 القديم (اختياري)",v->{
                Intent intent=new Intent(Intent.ACTION_OPEN_DOCUMENT);
                intent.addCategory(Intent.CATEGORY_OPENABLE);
                intent.setType("application/json");
                intent.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                startActivityForResult(intent,PICK_TESTPACK);
            });
            button(actions,"تصدير سجل T3",v->exportLogs());
        }
        status=text("اعرض الألوان على الشاشة ثم التقط الدليل؛ لا يُعلن النجاح دون مراجعتك.");
        page.addView(status);
        log("startup","package="+getPackageName()+" version=0.1.0 source="+BuildConfig.SOURCE_SHA
            +" device="+Build.MANUFACTURER+"/"+Build.MODEL+" api="+Build.VERSION.SDK_INT
            +" abi="+Build.SUPPORTED_ABIS[0]);
        select(0);
        runSharedAutoT3();
    }
    void runSharedAutoT3(){
        if(manualPreviewCase!=null){
            select(Integer.parseInt(manualPreviewCase.substring(4))-1);
            status.setText("شاهد الرسم الآن، ثم اضغط «التقاط صورة هذا الاختبار» عندما تكون مستعداً.");
            return;
        }
        String id=getIntent()==null?null:getIntent().getStringExtra("auto_case_id");
        if(id==null||!id.matches("T3-0[1-6]"))return;
        int idx=Integer.parseInt(id.substring(4))-1;
        new Handler(Looper.getMainLooper()).postDelayed(()->{
            select(idx);
            final int sequence=renderSequence;
            waitForSharedRender(id,idx,sequence,SystemClock.elapsedRealtime()+8000);
        },850);
    }
    /** Manual preview must be user-triggered and must never silently mark visual PASS. */
    void captureManualPreview(){
        if(manualPreviewCase==null||manualCaptureStarted)return;
        manualCaptureStarted=true;
        int idx=Integer.parseInt(manualPreviewCase.substring(4))-1;
        select(idx);
        status.setText("جارٍ التحقق من إطار GPU والتقاط الصورة. ستعود إلى قائمة النتائج.");
        final int sequence=renderSequence;
        waitForSharedRender(manualPreviewCase,idx,sequence,SystemClock.elapsedRealtime()+8000);
    }
    /** Only capture a rendered and CPU-read-back frame of this exact case/revision. */
    void waitForSharedRender(String id,int idx,int sequence,long deadline){
        if(lastRenderedSequence==sequence && lastRenderedCase==idx){
            if(!lastRenderedAssertion || lastRenderedError!=GLES30.GL_NO_ERROR){
                finishSharedEvidence(id,"FAIL",null,"GLES case assertion failed: "+lastRenderedNote);
            }else{
                // Allow EGL buffer swap/composition before copying our own window.
                new Handler(Looper.getMainLooper()).postDelayed(()->captureSharedEvidence(id),180);
            }
            return;
        }
        if(SystemClock.elapsedRealtime()>=deadline){
            finishSharedEvidence(id,"FAIL",null,"No matching GLES frame within timeout; never use stale pixels");
            return;
        }
        new Handler(Looper.getMainLooper()).postDelayed(
            ()->waitForSharedRender(id,idx,sequence,deadline),80);
    }
    /** Capture the actual independent GLES SurfaceView layer, not only the Window.
     *  Owner proof: window PixelCopy PNG was black while Android screenshot showed RGB.
     *  A byte-valid PNG is not a faithful image; verify two pixels vs glReadPixels.
     */
    void captureSharedEvidence(String id){
        captureSharedEvidence(id,0);
    }
    void captureSharedEvidence(String id,int attempt){
        final int expected=Integer.parseInt(id.substring(4))-1;
        final int generation=renderSequence;
        if(!sameRenderedFrame(expected,generation)){
            finishSharedEvidence(id,"NEEDS_SCREENSHOT",null,"Case changed/GLES assertion unavailable before SurfaceView capture");return;
        }
        if(surface==null||surface.getWidth()<16||surface.getHeight()<16||
           surface.getWidth()>4096||surface.getHeight()>4096 ||
           (long)surface.getWidth()*surface.getHeight()>12000000L){
            finishSharedEvidence(id,"NEEDS_SCREENSHOT",null,"GLES SurfaceView not sized for screenshot");return;
        }
        final int sw=surface.getWidth(),sh=surface.getHeight();
        final Bitmap gpu=Bitmap.createBitmap(sw,sh,Bitmap.Config.ARGB_8888);
        try{
            PixelCopy.request(surface,gpu,result->{
                if(!sameRenderedFrame(expected,generation)){
                    gpu.recycle();finishSharedEvidence(id,"NEEDS_SCREENSHOT",null,"GLES frame changed during SurfaceView PixelCopy");return;
                }
                if(result!=PixelCopy.SUCCESS){
                    gpu.recycle();retryOrManual(id,attempt,"SurfaceView PixelCopy code="+result);return;
                }
                int[] gpuLeft=lastRenderedLeft,gpuRight=lastRenderedRight;
                int[] photoLeft=SharedSurfacePixelPolicy.bitmapPixelToRgba(gpu.getPixel(sw/4,sh/2));
                int[] photoRight=SharedSurfacePixelPolicy.bitmapPixelToRgba(gpu.getPixel(3*sw/4,sh/2));
                String mismatch=SharedSurfacePixelPolicy.validate(gpuLeft,gpuRight,photoLeft,photoRight);
                if(mismatch!=null){
                    log("screenshot_pixel_mismatch","id="+id+" attempt="+attempt+" reason="+mismatch+
                        " surface="+sw+"x"+sh+
                        " photoLeft="+java.util.Arrays.toString(photoLeft)+
                        " photoRight="+java.util.Arrays.toString(photoRight));
                    gpu.recycle();retryOrManual(id,attempt,mismatch);return;
                }
                log("screenshot_pixel_match","id="+id+" attempt="+attempt+" surface="+sw+"x"+sh+
                    " left="+java.util.Arrays.toString(photoLeft)+
                    " right="+java.util.Arrays.toString(photoRight));
                // Capture UI chrome separately, then replace its possibly black
                // SurfaceView hole with the verified, independently copied GPU layer.
                final View decor=getWindow().getDecorView();
                final int dw=decor==null?0:decor.getWidth(),dh=decor==null?0:decor.getHeight();
                if(dw<16||dh<16||dw>4096||dh>4096||(long)dw*dh>12000000L){
                    publishVerifiedScreenshot(id,expected,generation,gpu,"verified-surface-only");
                    gpu.recycle();return;
                }
                final Bitmap window=Bitmap.createBitmap(dw,dh,Bitmap.Config.ARGB_8888);
                try{
                    PixelCopy.request(getWindow(),window,code->{
                        if(!sameRenderedFrame(expected,generation)){
                            window.recycle();gpu.recycle();
                            finishSharedEvidence(id,"NEEDS_SCREENSHOT",null,"GLES case changed during window composition");return;
                        }
                        if(code==PixelCopy.SUCCESS){
                            int[] at=new int[2],origin=new int[2];
                            surface.getLocationInWindow(at);
                            decor.getLocationInWindow(origin);
                            Canvas canvas=new Canvas(window);
                            canvas.drawBitmap(gpu,(float)(at[0]-origin[0]),
                                (float)(at[1]-origin[1]),new Paint(Paint.FILTER_BITMAP_FLAG));
                            publishVerifiedScreenshot(id,expected,generation,window,
                                "verified-GLSurfaceView-overlay-on-window");
                        }else{
                            log("screenshot_window_fallback","id="+id+" windowCopy="+code+
                                " using verified SurfaceView only");
                            publishVerifiedScreenshot(id,expected,generation,gpu,"verified-surface-only");
                        }
                        window.recycle();gpu.recycle();
                    },new Handler(Looper.getMainLooper()));
                }catch(Exception ex){
                    window.recycle();
                    log("screenshot_window_fallback","id="+id+" error="+ex.getClass().getSimpleName());
                    publishVerifiedScreenshot(id,expected,generation,gpu,"verified-surface-only");
                    gpu.recycle();
                }
            },new Handler(Looper.getMainLooper()));
        }catch(Exception e){
            gpu.recycle();retryOrManual(id,attempt,"SurfaceView PixelCopy exception "+e.getClass().getSimpleName());
        }
    }
    boolean sameRenderedFrame(int expected,int generation){
        return caseIndex==expected&&lastRenderedCase==expected&&
            renderSequence==generation&&lastRenderedSequence==generation&&
            lastRenderedAssertion&&lastRenderedError==GLES30.GL_NO_ERROR;
    }
    void retryOrManual(String id,int attempt,String reason){
        if(attempt<2){
            log("screenshot_retry","id="+id+" next="+(attempt+1)+" reason="+reason);
            surface.requestRender();
            new Handler(Looper.getMainLooper()).postDelayed(
                ()->captureSharedEvidence(id,attempt+1),280);
            return;
        }
        finishSharedEvidence(id,"NEEDS_SCREENSHOT",null,
            "No faithful SurfaceView PNG after 3 tries: "+reason+
            "; attach an actual owner screenshot or retry.");
    }
    void publishVerifiedScreenshot(String id,int expected,int generation,
                                   Bitmap bmp,String captureMethod){
        Uri dest=null;
        try{
            if(!sameRenderedFrame(expected,generation))
                throw new IOException("Rendered GLES case changed before PNG publication");
            if(Build.VERSION.SDK_INT<29)
                throw new IOException("MediaStore PNG export requires Android 10+");
            ByteArrayOutputStream encoded=new ByteArrayOutputStream(64*1024);
            if(!bmp.compress(Bitmap.CompressFormat.PNG,100,encoded))
                throw new IOException("Bitmap PNG encoding failed");
            byte[] png=encoded.toByteArray();
            if(!isCompletePng(png))throw new IOException("Incomplete PNG envelope");
            String sha=hexDigest(png);
            ContentValues v=new ContentValues();
            v.put(MediaStore.Downloads.DISPLAY_NAME,id+"-"+System.currentTimeMillis()+".png");
            v.put(MediaStore.Downloads.MIME_TYPE,"image/png");
            String parent=getIntent()==null?null:getIntent().getStringExtra("shared_session");
            if(parent==null||!parent.matches("[A-Za-z0-9._-]{6,90}"))parent=session;
            v.put(MediaStore.Downloads.RELATIVE_PATH,Environment.DIRECTORY_DOWNLOADS+"/Games/cl/test/shared-"+parent+"/");
            v.put(MediaStore.MediaColumns.IS_PENDING,1);
            dest=getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,v);
            if(dest==null)throw new IOException("Could not allocate pending PNG");
            try(OutputStream out=getContentResolver().openOutputStream(dest,"wt")){
                if(out==null)throw new IOException("Could not open pending PNG");
                out.write(png);out.flush();
            }
            verifyPngReadback(dest,png.length,sha);
            ContentValues visible=new ContentValues();
            visible.put(MediaStore.MediaColumns.IS_PENDING,0);
            if(getContentResolver().update(dest,visible,null,null)!=1)
                throw new IOException("Could not publish verified PNG");
            verifyPngReadback(dest,png.length,sha);
            if(!sameRenderedFrame(expected,generation))
                throw new IOException("GLES case changed before screenshot could be accepted");
            String gpu=lastRenderedNote;
            if(gpu==null||gpu.length()<30||gpu.length()>700)
                throw new IOException("Missing bounded GPU readback record");
            log("pixelcopy_png","id="+id+" method="+captureMethod+" uri="+dest+
                " bytes="+png.length+" sha256="+sha+" image="+bmp.getWidth()+"x"+bmp.getHeight()+
                " surface_match=true");
            finishSharedEvidence(id,"EVIDENCE_READY",dest.toString(),
                "GLES synthetic frame; "+gpu+"; png_bytes="+png.length+
                " png_sha256="+sha+" capture="+captureMethod+
                " verified_surface_pixels=true; human visual review still required");
        }catch(Exception e){
            if(dest!=null)try{getContentResolver().delete(dest,null,null);}
                catch(Exception cleanup){log("screenshot_cleanup_error",cleanup.getClass().getSimpleName());}
            log("screenshot_error",id+" "+e.getClass().getSimpleName()+": "+e.getMessage());
            finishSharedEvidence(id,"NEEDS_SCREENSHOT",null,
                "Verified SurfaceView capture could not be saved: "+e.getClass().getSimpleName());
        }
    }
    /** PNG signature + terminal IEND; Bitmap.compress is the trusted encoder. */
    static boolean isCompletePng(byte[] bytes){
        if(bytes==null||bytes.length<68||bytes.length>8*1024*1024)return false;
        int[] magic={137,80,78,71,13,10,26,10};
        for(int i=0;i<magic.length;i++)if((bytes[i]&255)!=magic[i])return false;
        int n=bytes.length;
        return bytes[n-8]=='I'&&bytes[n-7]=='E'&&bytes[n-6]=='N'&&bytes[n-5]=='D';
    }
    static String hexDigest(byte[] bytes)throws Exception{
        byte[] hash=MessageDigest.getInstance("SHA-256").digest(bytes);
        StringBuilder hex=new StringBuilder(hash.length*2);
        for(byte b:hash)hex.append(String.format(Locale.US,"%02x",b&255));
        return hex.toString();
    }
    void verifyPngReadback(Uri uri,int expectedBytes,String expectedSha)throws Exception{
        MessageDigest md=MessageDigest.getInstance("SHA-256");
        long count=0;
        try(InputStream in=getContentResolver().openInputStream(uri)){
            if(in==null)throw new IOException("PNG readback unavailable");
            byte[] buffer=new byte[16384];int n,zeroReads=0;
            while((n=in.read(buffer))!=-1){
                if(n==0){
                    if(++zeroReads>3)throw new IOException("PNG readback stalled");
                    continue;
                }
                zeroReads=0;
                count+=n;
                if(count>expectedBytes)throw new IOException("PNG readback exceeded encoded bytes");
                md.update(buffer,0,n);
            }
        }
        StringBuilder hash=new StringBuilder(64);
        for(byte b:md.digest())hash.append(String.format(Locale.US,"%02x",b&255));
        if(count!=expectedBytes||!hash.toString().equals(expectedSha))
            throw new IOException("PNG readback bytes/SHA256 mismatch");
    }
    void finishSharedEvidence(String id,String verdict,String uri,String observed){
        Intent reply=new Intent();reply.putExtra("case_id",id);reply.putExtra("status",verdict);
        reply.putExtra("observed",observed);if(uri!=null)reply.putExtra("screenshot_uri",uri);
        log("shared_auto_result",id+" "+verdict+" "+observed);
        setResult(RESULT_OK,reply);finish();
    }
    void select(int index){
        synchronized(lock){caseIndex=index;renderSequence++;lastRenderedSequence=-1;}
        testId="CASE0"+(index+1);
        JSONObject override=packOverrides.optJSONObject(testId);
        String step=override==null?STEPS[index]:override.optString("instructions",STEPS[index]);
        String expected=override==null?EXPECTED[index]:override.optString("expected",EXPECTED[index]);
        instructions.setText(testId+" — "+TITLES[index]+"\nالمطلوب: "+step+"\nالنتيجة المتوقعة: "+expected);
        note.setText("");
        log("case_start","index="+index+" pack="+packId);
        if(surface!=null)surface.requestRender();
    }
    void result(String verdict) {
        String observed=note.getText().toString().replace('\n',' ');
        if(observed.length()>800)observed=observed.substring(0,800);
        log("case_result",testId+"="+verdict+" observed="+observed);
        status.setText(testId+" — تم تسجيل الملاحظة: "+verdict+"، ويمكن تصدير السجل.");
    }
    synchronized void log(String event,String value) {
        try {
            JSONObject json=new JSONObject();json.put("utc_ms",System.currentTimeMillis());
            json.put("elapsed_ms",SystemClock.elapsedRealtime());json.put("event",event);
            json.put("test",testId);json.put("session",session);json.put("pack",packId);
            json.put("detail",value);
            try(FileOutputStream out=new FileOutputStream(logfile,true)){
                out.write((json.toString()+"\n").getBytes(StandardCharsets.UTF_8));
                out.getFD().sync();
            }
        }catch(Exception e){android.util.Log.e("T3Lab","Log write failed",e);}
    }
    void exportLogs() {
        if(Build.VERSION.SDK_INT<29){status.setText("تصدير الملفات يحتاج أندرويد 10 أو أحدث");return;}
        try {
            String parent=getIntent()==null?null:getIntent().getStringExtra("shared_session");
            String folder=parent!=null&&parent.matches("[A-Za-z0-9._-]{6,90}")?"Games/cl/test/shared-"+parent+"/":"Games/cl/test/t3-gles-material-"+session+"/";
            ContentValues cv=new ContentValues();
            cv.put(MediaStore.Downloads.DISPLAY_NAME,logfile.getName());
            cv.put(MediaStore.Downloads.MIME_TYPE,"application/x-ndjson");
            cv.put(MediaStore.Downloads.RELATIVE_PATH,Environment.DIRECTORY_DOWNLOADS+"/"+folder);
            Uri uri=getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,cv);
            if(uri==null)throw new IllegalStateException("MediaStore insertion failed");
            try(InputStream input=new java.io.FileInputStream(logfile);
                OutputStream out=getContentResolver().openOutputStream(uri,"w")){
                if(out==null)throw new IllegalStateException("MediaStore stream failed");
                byte[] bytes=new byte[16384];int n;while((n=input.read(bytes))!=-1)out.write(bytes,0,n);
            }
            status.setText("تم حفظ السجل: Download/"+folder+logfile.getName());
        }catch(Exception e){log("export_error",e.getClass().getSimpleName()+": "+e.getMessage());
            status.setText("تعذّر التصدير، والسجل محفوظ داخل التطبيق: "+e.getMessage());}
    }
    @Override protected void onActivityResult(int request,int result,Intent data) {
        super.onActivityResult(request,result,data);
        if(request!=PICK_TESTPACK||result!=RESULT_OK||data==null||data.getData()==null)return;
        try {
            byte[] bytes=new byte[65537];int n=0;
            try(InputStream in=getContentResolver().openInputStream(data.getData())){
                if(in==null)throw new IllegalStateException("Unreadable file");
                while(n<bytes.length){int k=in.read(bytes,n,bytes.length-n);if(k<0)break;n+=k;}
            }
            if(n>65536)throw new IllegalArgumentException("Pack exceeds 64 KiB");
            JSONObject obj=new JSONObject(new String(bytes,0,n,StandardCharsets.UTF_8));
            if(obj.length()!=7||obj.getInt("schema_version")!=1||
                !"T3".equals(obj.getString("worker")))throw new IllegalArgumentException("Not T3 data-only v1 pack");
            String id=obj.getString("pack_id");
            if(!id.matches("[a-z0-9][a-z0-9._-]{0,79}"))throw new IllegalArgumentException("Invalid pack id");
            if(!obj.isNull("source_sha")&&!obj.getString("source_sha").matches("[a-f0-9]{40}"))
                throw new IllegalArgumentException("Invalid source SHA");
            JSONArray tests=obj.getJSONArray("tests");
            if(tests.length()<1||tests.length()>6)throw new IllegalArgumentException("1..6 cases required");
            JSONObject parsed=new JSONObject();
            for(int i=0;i<tests.length();i++){
                JSONObject t=tests.getJSONObject(i);
                String key=t.getString("id");
                if(!key.matches("CASE0[1-6]")||parsed.has(key)||
                    !"note".equals(t.getString("type")) ||
                    t.getString("title").length()>1500 ||
                    t.getString("instructions").length()>1500 ||
                    t.getString("expected").length()>1500)
                    throw new IllegalArgumentException("Unsupported/duplicate test; text-only CASE01..06 required");
                parsed.put(key,t);
            }
            MessageDigest digest=MessageDigest.getInstance("SHA-256");
            byte[] hash=digest.digest(java.util.Arrays.copyOf(bytes,n));
            StringBuilder hex=new StringBuilder();for(byte b:hash)hex.append(String.format(Locale.US,"%02x",b&255));
            packOverrides=parsed;packId=id;packHash=hex.toString();
            log("pack_import","pack_id="+packId+" sha256="+packHash+" tests="+tests.length());
            select(caseIndex);
            Toast.makeText(this,"T3 data-only instructions loaded",Toast.LENGTH_LONG).show();
        }catch(Exception e){log("pack_reject",e.getClass().getSimpleName()+": "+e.getMessage());
            Toast.makeText(this,"Pack rejected: "+e.getMessage(),Toast.LENGTH_LONG).show();}
    }
    @Override protected void onPause(){super.onPause();if(surface!=null)surface.onPause();log("lifecycle","pause");}
    @Override protected void onResume(){super.onResume();if(surface!=null)surface.onResume();}
    @Override protected void onStop(){super.onStop();log("lifecycle","stop");}

    final class Painter implements GLSurfaceView.Renderer {
        final String vertex="#version 300 es\nlayout(location=0) in vec2 pos;\n"
           +"layout(location=1) in vec4 col;\nlayout(location=2) in vec2 uv;\n"
           +"out vec4 color;out vec2 texCoord;\nvoid main(){gl_Position=vec4(pos,0.0,1.0);color=col;texCoord=uv;}";
        final String fragment="#version 300 es\nprecision highp float;\nin vec4 color;in vec2 texCoord;\n"
           +"uniform sampler2D imageTex;uniform int useTex;out vec4 frag;\n"
           +"void main(){frag=color*(useTex==1?texture(imageTex,texCoord):vec4(1.0));}";
        int program=0,vbo=0,plain=0,srgb=0,smoke=0,width=1,height=1;
        int useTexLocation=-1;
        boolean negativeChecked=false,negativeRejected=false;
        int compile(int type,String source,String label){
            int shader=GLES30.glCreateShader(type);
            GLES30.glShaderSource(shader,source);GLES30.glCompileShader(shader);
            int[] status=new int[1];GLES30.glGetShaderiv(shader,GLES30.GL_COMPILE_STATUS,status,0);
            if(status[0]==0){String err=GLES30.glGetShaderInfoLog(shader);
                log("shader_compile_failure",label+" "+(err.length()>600?err.substring(0,600):err));
                GLES30.glDeleteShader(shader);return 0;}
            log("shader_compile_success",label);return shader;
        }
        int texture(int internal,int r,int g,int b,int a) {
            int[] out=new int[1];GLES30.glGenTextures(1,out,0);
            GLES30.glBindTexture(GLES30.GL_TEXTURE_2D,out[0]);
            GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D,GLES30.GL_TEXTURE_MIN_FILTER,GLES30.GL_NEAREST);
            GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D,GLES30.GL_TEXTURE_MAG_FILTER,GLES30.GL_NEAREST);
            GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D,GLES30.GL_TEXTURE_WRAP_S,GLES30.GL_CLAMP_TO_EDGE);
            GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D,GLES30.GL_TEXTURE_WRAP_T,GLES30.GL_CLAMP_TO_EDGE);
            ByteBuffer pixels=ByteBuffer.allocateDirect(16);
            for(int i=0;i<4;i++)pixels.put((byte)r).put((byte)g).put((byte)b).put((byte)a);
            pixels.flip();GLES30.glTexImage2D(GLES30.GL_TEXTURE_2D,0,internal,2,2,0,
                GLES30.GL_RGBA,GLES30.GL_UNSIGNED_BYTE,pixels);
            return out[0];
        }
        @Override public void onSurfaceCreated(GL10 gl,EGLConfig config) {
            program=0;negativeChecked=false;negativeRejected=false;
            log("gles_context","vendor="+GLES30.glGetString(GLES30.GL_VENDOR)
                +" renderer="+GLES30.glGetString(GLES30.GL_RENDERER)
                +" version="+GLES30.glGetString(GLES30.GL_VERSION)
                +" GLSL="+GLES30.glGetString(GLES30.GL_SHADING_LANGUAGE_VERSION));
            int vs=compile(GLES30.GL_VERTEX_SHADER,vertex,"valid_vertex");
            int fs=compile(GLES30.GL_FRAGMENT_SHADER,fragment,"valid_fragment");
            if(vs!=0&&fs!=0){
                program=GLES30.glCreateProgram();GLES30.glAttachShader(program,vs);GLES30.glAttachShader(program,fs);
                GLES30.glLinkProgram(program);int[] ok=new int[1];
                GLES30.glGetProgramiv(program,GLES30.GL_LINK_STATUS,ok,0);
                if(ok[0]==0){log("shader_link_failure",GLES30.glGetProgramInfoLog(program));program=0;}
            }
            if(vs!=0)GLES30.glDeleteShader(vs);if(fs!=0)GLES30.glDeleteShader(fs);
            if(program==0){log("fatal","GLES3 program unavailable");return;}
            useTexLocation=GLES30.glGetUniformLocation(program,"useTex");
            int[] buffers=new int[1];GLES30.glGenBuffers(1,buffers,0);vbo=buffers[0];
            plain=texture(GLES30.GL_RGBA8,128,128,128,255);
            srgb=texture(GLES30.GL_SRGB8_ALPHA8,128,128,128,255);
            smoke=texture(GLES30.GL_RGBA8,255,15,0,128);
            log("resource_init","unorm="+plain+" srgb="+srgb+" rgbaSmoke="+smoke+
                " gl_error=0x"+Integer.toHexString(GLES30.glGetError()));
        }
        @Override public void onSurfaceChanged(GL10 gl,int w,int h) {
            width=Math.max(1,w);height=Math.max(1,h);GLES30.glViewport(0,0,width,height);
        }
        void quad(float x0,float y0,float x1,float y1,float r,float g,float b,float a,int tex) {
            float[] values={
                x0,y0,r,g,b,a,0,0, x1,y0,r,g,b,a,1,0,
                x0,y1,r,g,b,a,0,1, x1,y1,r,g,b,a,1,1
            };
            draw(values,tex);
        }
        void draw(float[] array,int tex) {
            ByteBuffer memory=ByteBuffer.allocateDirect(array.length*4).order(ByteOrder.nativeOrder());
            FloatBuffer data=memory.asFloatBuffer();data.put(array);data.position(0);
            GLES30.glBindBuffer(GLES30.GL_ARRAY_BUFFER,vbo);
            GLES30.glBufferData(GLES30.GL_ARRAY_BUFFER,array.length*4,data,GLES30.GL_STREAM_DRAW);
            GLES30.glEnableVertexAttribArray(0);GLES30.glVertexAttribPointer(0,2,GLES30.GL_FLOAT,false,32,0);
            GLES30.glEnableVertexAttribArray(1);GLES30.glVertexAttribPointer(1,4,GLES30.GL_FLOAT,false,32,8);
            GLES30.glEnableVertexAttribArray(2);GLES30.glVertexAttribPointer(2,2,GLES30.GL_FLOAT,false,32,24);
            GLES30.glUniform1i(useTexLocation,tex==0?0:1);
            GLES30.glActiveTexture(GLES30.GL_TEXTURE0);GLES30.glBindTexture(GLES30.GL_TEXTURE_2D,tex);
            GLES30.glDrawArrays(GLES30.GL_TRIANGLE_STRIP,0,4);
        }
        int[] pixel(String name,int x,int y) {
            ByteBuffer buffer=ByteBuffer.allocateDirect(4);
            GLES30.glReadPixels(x,y,1,1,GLES30.GL_RGBA,GLES30.GL_UNSIGNED_BYTE,buffer);
            int[] rgba={buffer.get(0)&255,buffer.get(1)&255,buffer.get(2)&255,buffer.get(3)&255};
            log("pixel_rgba",name+"="+rgba[0]+","+rgba[1]+","+rgba[2]+","+rgba[3]);
            return rgba;
        }
        boolean pixelContract(int id,int[] left,int[] right){
            switch(id){
                case 0: return left[0]>190 && left[1]<55 && left[2]<55 &&
                    right[2]>190 && right[0]<55 && right[1]<55;
                case 1: return Math.abs(left[1]-right[1])>20 &&
                    !(left[0]>245 && left[1]>245 && left[2]>245);
                case 2: return left[0]>45 && left[2]>35 && left[2]<230;
                case 3: return left[0]>45 && left[2]>30 && right[0]>45 &&
                    Math.abs(left[0]-right[0])<=18 &&
                    Math.abs(left[1]-right[1])<=18 && Math.abs(left[2]-right[2])<=18;
                case 4: return left[0]>right[0]+20 && left[1]>right[1]+20 &&
                    left[2]>right[2]+20;
                case 5: return negativeChecked && negativeRejected &&
                    left[2]>left[1] && left[1]>left[0];
                default: return false;
            }
        }
        @Override public void onDrawFrame(GL10 gl) {
            final int current,generation;
            synchronized(lock){current=caseIndex;generation=renderSequence;}
            GLES30.glDisable(GLES30.GL_BLEND);GLES30.glClearColor(0.07f,0.07f,0.10f,1f);
            GLES30.glClear(GLES30.GL_COLOR_BUFFER_BIT);
            if(program==0){
                lastRenderedNote="GLES shader program unavailable";
                lastRenderedError=GLES30.GL_INVALID_OPERATION;
                lastRenderedAssertion=false;lastRenderedCase=current;lastRenderedSequence=generation;
                return;
            }
            GLES30.glUseProgram(program);GLES30.glUniform1i(GLES30.glGetUniformLocation(program,"imageTex"),0);
            switch(current) {
                case 0:
                    quad(-1,-1,-.34f,1,1,0,0,1,0);
                    quad(-.34f,-1,.34f,1,0,1,0,1,0);
                    quad(.34f,-1,1,1,0,0,1,1,0);
                    break;
                case 1:
                    draw(new float[]{
                        -1,-1,1,0,0,1,0,0, 1,-1,0,1,0,1,1,0,
                        -1,1,0,0,1,1,0,1, 1,1,1,1,1,1,1,1
                    },0);
                    break;
                case 2:
                    quad(-.95f,-.9f,.95f,.9f,0,.2f,.85f,1,0);
                    GLES30.glEnable(GLES30.GL_BLEND);
                    GLES30.glBlendFunc(GLES30.GL_SRC_ALPHA,GLES30.GL_ONE_MINUS_SRC_ALPHA);
                    quad(-.72f,-.7f,.72f,.7f,1,1,1,1,smoke);
                    GLES30.glDisable(GLES30.GL_BLEND);
                    break;
                case 3:
                    quad(-.95f,-.9f,-.05f,.9f,0,.1f,.85f,1,0);
                    quad(.05f,-.9f,.95f,.9f,0,.1f,.85f,1,0);
                    GLES30.glEnable(GLES30.GL_BLEND);
                    GLES30.glBlendFunc(GLES30.GL_SRC_ALPHA,GLES30.GL_ONE_MINUS_SRC_ALPHA);
                    quad(-.87f,-.6f,-.13f,.6f,1,.1f,0,.5f,0);
                    GLES30.glBlendFunc(GLES30.GL_ONE,GLES30.GL_ONE_MINUS_SRC_ALPHA);
                    quad(.13f,-.6f,.87f,.6f,.5f,.05f,0,.5f,0);
                    GLES30.glDisable(GLES30.GL_BLEND);
                    break;
                case 4:
                    quad(-.95f,-.9f,-.05f,.9f,1,1,1,1,plain);
                    quad(.05f,-.9f,.95f,.9f,1,1,1,1,srgb);
                    break;
                case 5:
                    if(!negativeChecked){
                        negativeChecked=true;
                        int bad=compile(GLES30.GL_FRAGMENT_SHADER,
                            "#version 300 es\nprecision mediump float;out vec4 x;void main(){x = INVALID_TOKEN;}","expected_negative");
                        if(bad==0){negativeRejected=true;
                            log("negative_control","PASS invalid shader rejected");}
                        else{log("negative_control","FAIL invalid shader compiled unexpectedly");
                            GLES30.glDeleteShader(bad);}
                    }
                    quad(-1,-1,1,1,.1f,.45f,.8f,1,0);
                    break;
                default:break;
            }
            int[] left=pixel("left_center",width/4,height/2);
            int[] right=pixel("right_center",3*width/4,height/2);
            int glError=GLES30.glGetError();
            boolean colors=pixelContract(current,left,right);
            String observed="case=CASE0"+(current+1)+" frame="+generation+
                " left="+java.util.Arrays.toString(left)+" right="+java.util.Arrays.toString(right)+
                " contract="+colors+" gl_error=0x"+Integer.toHexString(glError)+
                " viewport="+width+"x"+height;
            log("render",observed);
            lastRenderedNote=observed;
            lastRenderedLeft=left;
            lastRenderedRight=right;
            lastRenderedError=glError;
            lastRenderedAssertion=colors && glError==GLES30.GL_NO_ERROR;
            lastRenderedCase=current;
            lastRenderedSequence=generation;
        }
    }
}
