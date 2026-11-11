package com.alwansan.gfx102;

import android.app.Activity;
import android.content.ContentValues;
import android.database.Cursor;
import android.graphics.Bitmap;
import android.net.Uri;
import android.opengl.GLES30;
import android.opengl.GLSurfaceView;
import android.os.Build;
import android.os.Bundle;
import android.provider.MediaStore;
import android.view.View;
import android.view.WindowManager;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.TextView;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.nio.charset.StandardCharsets;
import java.security.MessageDigest;
import java.util.Arrays;
import java.util.LinkedHashMap;
import java.util.Map;
import java.util.zip.ZipEntry;
import java.util.zip.ZipOutputStream;
import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;

/**
 * GFX102: independent GLES 3.0 extension enumeration, four controlled GPU reads.
 * Shader sources are new synthetic fixtures, NOT original Raft Shader48.
 * OpenGL calls happen only on GLSurfaceView's GL thread with a current context.
 */
public final class MainActivity extends Activity {
    private static final int SIDE = 256;
    private static final int[][] POINTS = {{128,98},{104,108},{152,108}};
    private static final float[] W = {.55f,1.0f,2.7f};
    private static final String[] MODES = {"Smooth","Flat","AffineEmulated","NativeNoPerspectiveES300","NativeNoPerspectiveES310","NativeNoPerspectiveES320"};
    private static final String EXTENSION = "GL_NV_shader_noperspective_interpolation";
    private final JSONArray events = new JSONArray();
    private final LinkedHashMap<String,byte[]> images = new LinkedHashMap<String,byte[]>();
    private JSONObject summary = new JSONObject();
    private TextView status;
    private GLSurfaceView view;
    private volatile boolean finished = false;
    private volatile String exportError = "";
    private int successfulReadbacks = 0;
    private boolean nativeExtension = false;

    private JSONObject j(Object... kv) {
        JSONObject o = new JSONObject();
        try { for(int i=0;i<kv.length;i+=2)o.put((String)kv[i],kv[i+1]); }
        catch(Exception ex){throw new RuntimeException(ex);}
        return o;
    }
    private synchronized void record(JSONObject o){events.put(o);}
    private void display(final String s) {
        runOnUiThread(new Runnable(){public void run(){ status.setText(s); }});
    }

    @Override public void onCreate(Bundle state) {
        super.onCreate(state);
        getWindow().addFlags(WindowManager.LayoutParams.FLAG_KEEP_SCREEN_ON);
        LinearLayout frame=new LinearLayout(this);
        frame.setOrientation(LinearLayout.VERTICAL);
        status=new TextView(this);status.setTextSize(17);status.setPadding(20,14,20,14);
        status.setText("GFX102: checking GLES extension and rendering controls.\nOriginal Raft Shader48 remains unverified.");
        frame.addView(status);
        Button export=new Button(this);
        export.setText("EXPORT ALL LOGS ZIP → Download/Games/cl/test/g/");
        export.setOnClickListener(new View.OnClickListener(){
            public void onClick(View v){startExport();}
        });
        frame.addView(export);
        view=new GLSurfaceView(this);
        view.setEGLContextClientVersion(3);
        view.setRenderer(new GLSurfaceView.Renderer(){
            public void onSurfaceCreated(GL10 unused,EGLConfig config){}
            public void onSurfaceChanged(GL10 unused,int width,int height){
                GLES30.glViewport(0,0,width,height);
            }
            public void onDrawFrame(GL10 unused){
                if(finished) return;
                finished=true;
                try {runProbe();}
                catch(Throwable e) {
                    record(j("event","fatal","error",e.getClass().getSimpleName()+": "+e.getMessage()));
                    display("GFX102 failure: "+e.getClass().getSimpleName()+"\nPress EXPORT to retrieve logs.");
                }
                startExport();
            }
        });
        view.setRenderMode(GLSurfaceView.RENDERMODE_WHEN_DIRTY);
        frame.addView(view,new LinearLayout.LayoutParams(-1,0,1));
        setContentView(frame);
    }

    private static int getInt(int what){
        int[] a=new int[1];GLES30.glGetIntegerv(what,a,0);return a[0];
    }
    private static String sha256(byte[] bytes)throws Exception{
        byte[] digest=MessageDigest.getInstance("SHA-256").digest(bytes);
        StringBuilder s=new StringBuilder();
        for(byte b:digest)s.append(String.format(java.util.Locale.US,"%02x",b&255));
        return s.toString();
    }
    private static int glslVersionFor(String mode) { return mode.endsWith("ES320")?320:mode.endsWith("ES310")?310:300; }
    private static String vertex(String mode,boolean extension,int glslVersion) {
        String head="#version "+glslVersion+" es\n"+
            (extension?"#extension "+EXTENSION+" : require\n":"")+
            "precision highp float;\n";
        String out;
        if(mode.startsWith("NativeNoPerspective"))out="noperspective out vec3 vColor;\n";
        else if(mode.equals("Flat"))out="flat out vec3 vColor;\n";
        else if(mode.equals("AffineEmulated"))out="smooth out vec3 vWeighted; smooth out float vClipW;\n";
        else out="smooth out vec3 vColor;\n";
        return head+out+
            "const vec2 pos[3]=vec2[3](vec2(-0.86,-0.77),vec2(0.86,-0.77),vec2(0.0,0.86));\n"+
            "const float ww[3]=float[3](0.55,1.0,2.7);\n"+
            "const vec3 colors[3]=vec3[3](vec3(1,0,0),vec3(0,1,0),vec3(0,0,1));\n"+
            "void main(){int i=gl_VertexID; float w=ww[i];\n"+
            "gl_Position=vec4(pos[i]*w,0.25*w,w);\n"+
            (mode.equals("AffineEmulated")?
               "vWeighted=colors[i]*w; vClipW=w;\n":"vColor=colors[i];\n")+
            "}\n";
    }
    private static String fragment(String mode,boolean extension,int glslVersion) {
        String head="#version "+glslVersion+" es\n"+
            (extension?"#extension "+EXTENSION+" : require\n":"")+
            "precision highp float;\n";
        if(mode.equals("AffineEmulated"))
            return head+"smooth in vec3 vWeighted; smooth in float vClipW;\n"+
                "layout(location=0) out vec4 o;\n"+
                "void main(){o=vec4(vWeighted/max(vClipW,0.00001),1.0);}\n";
        String qualifier=mode.startsWith("NativeNoPerspective")?"noperspective ":
                         mode.equals("Flat")?"flat ":"smooth ";
        return head+qualifier+"in vec3 vColor;\n"+
            "layout(location=0) out vec4 o;\n"+
            "void main(){o=vec4(vColor,1.0);}\n";
    }
    private int compile(int kind,String shaderSource,String mode,String stage) {
        int shader=GLES30.glCreateShader(kind);
        GLES30.glShaderSource(shader,shaderSource);
        GLES30.glCompileShader(shader);
        boolean ok=getShaderStatus(shader);
        String log=GLES30.glGetShaderInfoLog(shader);
        record(j("event","compile","mode",mode,"stage",stage,"success",ok,
            "driver_log",log,"gl_error",GLES30.glGetError()));
        if(!ok){GLES30.glDeleteShader(shader);return 0;}
        return shader;
    }
    private static boolean getShaderStatus(int shader) {
        int[] status=new int[1];
        GLES30.glGetShaderiv(shader,GLES30.GL_COMPILE_STATUS,status,0);
        return status[0]!=0;
    }
    private int makeProgram(String mode) {
        if(mode.startsWith("NativeNoPerspective")&&!nativeExtension){
            record(j("event","capability_skip","mode",mode,
                "reason","GL_NV_shader_noperspective_interpolation_NOT_ADVERTISED"));
            return 0;
        }
        boolean extension=mode.startsWith("NativeNoPerspective");
        int vs=compile(GLES30.GL_VERTEX_SHADER,vertex(mode,extension,glslVersionFor(mode)),mode,"vertex");
        int fs=compile(GLES30.GL_FRAGMENT_SHADER,fragment(mode,extension,glslVersionFor(mode)),mode,"fragment");
        int program=0;
        if(vs!=0&&fs!=0){
            program=GLES30.glCreateProgram();
            GLES30.glAttachShader(program,vs);
            GLES30.glAttachShader(program,fs);
            GLES30.glLinkProgram(program);
            int[] success=new int[1];
            GLES30.glGetProgramiv(program,GLES30.GL_LINK_STATUS,success,0);
            record(j("event","link","mode",mode,"success",success[0]!=0,
                "driver_log",GLES30.glGetProgramInfoLog(program),
                "gl_error",GLES30.glGetError()));
            if(success[0]==0){GLES30.glDeleteProgram(program);program=0;}
        }else record(j("event","link","mode",mode,"success",false,"skipped",true));
        if(vs!=0)GLES30.glDeleteShader(vs);
        if(fs!=0)GLES30.glDeleteShader(fs);
        return program;
    }

    private static double[] expected(int x,int y,boolean smooth){
        // Pixel centers in 256×256 framebuffer; glReadPixels origin is bottom-left.
        double px=2.0*(x+.5)/SIDE-1.0, py=2.0*(y+.5)/SIDE-1.0;
        double x0=-.86,y0=-.77,x1=.86,y1=-.77,x2=0,y2=.86;
        double denominator=(y1-y2)*(x0-x2)+(x2-x1)*(y0-y2);
        double l0=((y1-y2)*(px-x2)+(x2-x1)*(py-y2))/denominator;
        double l1=((y2-y0)*(px-x2)+(x0-x2)*(py-y2))/denominator;
        double l2=1-l0-l1;
        double[] lambda={l0,l1,l2};
        if(smooth){
            double d=0;for(int i=0;i<3;i++){lambda[i]/=W[i];d+=lambda[i];}
            for(int i=0;i<3;i++)lambda[i]/=d;
        }
        return lambda;
    }
    private static double error(double[] a,double[] b){
        return (Math.abs(a[0]-b[0])+Math.abs(a[1]-b[1])+Math.abs(a[2]-b[2]))/3.0;
    }
    private static double[] readColor(byte[] rgba,int x,int y) {
        int base=(y*SIDE+x)*4;
        return new double[]{(rgba[base]&255)/255.0,(rgba[base+1]&255)/255.0,
            (rgba[base+2]&255)/255.0};
    }
    private static byte[] png(byte[] raw) {
        int[] argb=new int[SIDE*SIDE];
        for(int y=0;y<SIDE;y++)for(int x=0;x<SIDE;x++){
            int src=((SIDE-1-y)*SIDE+x)*4;
            int rr=raw[src]&255, gg=raw[src+1]&255, bb=raw[src+2]&255, aa=raw[src+3]&255;
            argb[y*SIDE+x]=(aa<<24)|(rr<<16)|(gg<<8)|bb;
        }
        Bitmap bm=Bitmap.createBitmap(SIDE,SIDE,Bitmap.Config.ARGB_8888);
        bm.setPixels(argb,0,SIDE,0,0,SIDE,SIDE);
        ByteArrayOutputStream bytes=new ByteArrayOutputStream();
        if(!bm.compress(Bitmap.CompressFormat.PNG,100,bytes))
            throw new IllegalStateException("PNG_COMPRESS_FAILED");
        bm.recycle();
        return bytes.toByteArray();
    }
    private static final class Samples {
        byte[] raw;
        double smoothError,affineError;
        JSONObject json;
    }
    private Samples render(String mode,int framebuffer) throws Exception{
        int program=makeProgram(mode);
        if(program==0)return null;
        GLES30.glBindFramebuffer(GLES30.GL_FRAMEBUFFER,framebuffer);
        GLES30.glViewport(0,0,SIDE,SIDE);
        GLES30.glDisable(GLES30.GL_BLEND);
        GLES30.glDisable(GLES30.GL_DEPTH_TEST);
        GLES30.glDisable(GLES30.GL_DITHER);
        GLES30.glClearColor(.09f,.14f,.21f,1f);
        GLES30.glClear(GLES30.GL_COLOR_BUFFER_BIT);
        GLES30.glUseProgram(program);
        GLES30.glDrawArrays(GLES30.GL_TRIANGLES,0,3);
        GLES30.glFinish();
        ByteBuffer buf=ByteBuffer.allocateDirect(SIDE*SIDE*4).order(ByteOrder.nativeOrder());
        GLES30.glReadPixels(0,0,SIDE,SIDE,GLES30.GL_RGBA,GLES30.GL_UNSIGNED_BYTE,buf);
        int glerr=GLES30.glGetError();
        GLES30.glUseProgram(0);
        GLES30.glDeleteProgram(program);
        if(glerr!=GLES30.GL_NO_ERROR)
            throw new IllegalStateException("GL_READBACK_ERROR_"+glerr+"_"+mode);
        Samples out=new Samples();out.raw=new byte[SIDE*SIDE*4];
        buf.position(0);buf.get(out.raw);
        JSONArray points=new JSONArray();
        double sumSmooth=0,sumAffine=0;
        for(int[] point:POINTS){
            int x=point[0],y=point[1];
            double[] observed=readColor(out.raw,x,y);
            double[] controlSmooth=expected(x,y,true);
            double[] controlAffine=expected(x,y,false);
            if(observed[0]+observed[1]+observed[2]<.7)
                throw new IllegalStateException("TEST_SAMPLE_NOT_INSIDE_TRIANGLE_"+mode);
            double eS=error(observed,controlSmooth),eA=error(observed,controlAffine);
            sumSmooth+=eS;sumAffine+=eA;
            points.put(j("x",x,"y",y,"observed",new JSONArray(Arrays.asList(
                    observed[0],observed[1],observed[2])),
                "cpu_smooth_error",eS,"cpu_affine_error",eA));
        }
        out.smoothError=sumSmooth/POINTS.length;
        out.affineError=sumAffine/POINTS.length;
        out.json=j("mode",mode,"gpu_readback",true,"cpu_smooth_mad",out.smoothError,
            "cpu_affine_mad",out.affineError,"raw_rgba_sha256",sha256(out.raw),
            "samples",points,"rgba8",true);
        String name="gpu-"+mode+".png";
        byte[] bytes=png(out.raw);
        synchronized(images){images.put(name,bytes);}
        out.json.put("png_filename",name);
        out.json.put("png_sha256",sha256(bytes));
        successfulReadbacks++;
        record(j("event","gpu_readback","result",out.json));
        return out;
    }

    private void runProbe() throws Exception {
        String renderer=GLES30.glGetString(GLES30.GL_RENDERER);
        String glVersion=GLES30.glGetString(GLES30.GL_VERSION);
        String glslVersion=GLES30.glGetString(GLES30.GL_SHADING_LANGUAGE_VERSION);
        int major=getInt(GLES30.GL_MAJOR_VERSION);
        int minor=getInt(GLES30.GL_MINOR_VERSION);
        int extensionCount=getInt(GLES30.GL_NUM_EXTENSIONS);
        if(major<3 || extensionCount<0 || extensionCount>10000)
            throw new IllegalStateException("INVALID_GLES_CAPABILITY");
        for(int i=0;i<extensionCount;i++)
            if(EXTENSION.equals(GLES30.glGetStringi(GLES30.GL_EXTENSIONS,i)))
                nativeExtension=true;
        summary=j("experiment","GFX-MULTI-102",
            "device",Build.MANUFACTURER+" "+Build.MODEL,"android_sdk",Build.VERSION.SDK_INT,
            "renderer",renderer,"gles_version",glVersion,"glsl_version",glslVersion,
            "gles_major",major,"gles_minor",minor,"extension_count",extensionCount,
            "nv_noperspective_extension_advertised",nativeExtension,
            "native_interpolation_extension_in_gles3_core",false,
            "originalShaderRestored",false,"originalRaftShaderBytecodeUsed",false,
            "originalAnimationRestored",false,"pcAdrenoPixelParityVerified",false,
            "phase_closed",false,"synthetic_only",true,
            "started_ms",System.currentTimeMillis());
        record(j("event","environment","data",summary));
        int[] tex=new int[1],fbo=new int[1],vao=new int[1];
        GLES30.glGenTextures(1,tex,0);
        GLES30.glBindTexture(GLES30.GL_TEXTURE_2D,tex[0]);
        GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D,GLES30.GL_TEXTURE_MIN_FILTER,GLES30.GL_NEAREST);
        GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D,GLES30.GL_TEXTURE_MAG_FILTER,GLES30.GL_NEAREST);
        GLES30.glTexImage2D(GLES30.GL_TEXTURE_2D,0,GLES30.GL_RGBA8,
            SIDE,SIDE,0,GLES30.GL_RGBA,GLES30.GL_UNSIGNED_BYTE,null);
        GLES30.glGenFramebuffers(1,fbo,0);
        GLES30.glBindFramebuffer(GLES30.GL_FRAMEBUFFER,fbo[0]);
        GLES30.glFramebufferTexture2D(GLES30.GL_FRAMEBUFFER,GLES30.GL_COLOR_ATTACHMENT0,
            GLES30.GL_TEXTURE_2D,tex[0],0);
        if(GLES30.glCheckFramebufferStatus(GLES30.GL_FRAMEBUFFER)
               !=GLES30.GL_FRAMEBUFFER_COMPLETE)
            throw new IllegalStateException("RGBA8_FRAMEBUFFER_INCOMPLETE");
        GLES30.glGenVertexArrays(1,vao,0);
        GLES30.glBindVertexArray(vao[0]);
        Samples[] result=new Samples[MODES.length];
        try {
            for(int i=0;i<MODES.length;i++){
                result[i]=render(MODES[i],fbo[0]);
                if(result[i]!=null)
                    display("GFX102: "+MODES[i]+" GPU test done ("+successfulReadbacks+"/4).");
            }
        } finally {
            GLES30.glBindFramebuffer(GLES30.GL_FRAMEBUFFER,0);
            GLES30.glBindVertexArray(0);
            GLES30.glDeleteVertexArrays(1,vao,0);
            GLES30.glDeleteFramebuffers(1,fbo,0);
            GLES30.glDeleteTextures(1,tex,0);
        }
        final double threshold=.035;
        // Qualcomm can advertise NV noperspective but reject the reserved
        // keyword in #version 300 es. Try exact GLSL 300/310/320 variants
        // with the extension REQUIRED in both stages; never infer success
        // from advertised extension alone.
        Samples bestNative=null;
        int bestNativeVersion=-1;
        JSONArray nativeTrials=new JSONArray();
        for(int i=3;i<MODES.length;i++){
            Samples candidate=result[i];
            int version=glslVersionFor(MODES[i]);
            nativeTrials.put(j("glsl_es_version",version,"gpu_readback",candidate!=null,
                "affine_cpu_mad",candidate==null?JSONObject.NULL:candidate.affineError));
            if(candidate!=null&&(bestNative==null||candidate.affineError<bestNative.affineError)){
                bestNative=candidate;
                bestNativeVersion=version;
            }
        }
        boolean smoothGood=result[0]!=null&&result[0].smoothError<threshold;
        boolean affineGood=result[2]!=null&&result[2].affineError<threshold;
        boolean flatGood=false;
        if(result[1]!=null){
            byte[] flat=result[1].raw;
            double[] a=readColor(flat,POINTS[0][0],POINTS[0][1]);
            double[] b=readColor(flat,POINTS[1][0],POINTS[1][1]);
            double[] c=readColor(flat,POINTS[2][0],POINTS[2][1]);
            flatGood=error(a,b)<.015&&error(a,c)<.015;
        }
        boolean nativeGood=bestNative!=null&&bestNative.affineError<threshold;
        boolean nativeCollapsed=bestNative!=null&&bestNative.smoothError<threshold
            &&bestNative.affineError>threshold;
        String verdict;
        if(!smoothGood || !affineGood || !flatGood)
            verdict="CONTROL_FAILURE_OR_INCONCLUSIVE";
        else if(!nativeExtension)
            verdict="NATIVE_EXTENSION_NOT_ADVERTISED";
        else if(bestNative==null)
            verdict="NATIVE_EXTENSION_ADVERTISED_BUT_ALL_GLSL_VERSIONS_FAILED";
        else if(nativeGood)
            verdict="NATIVE_NV_NOPERSPECTIVE_GPU_MATCHED_AFFINE";
        else if(nativeCollapsed)
            verdict="NATIVE_QUALIFIER_COLLAPSED_TO_SMOOTH";
        else verdict="NATIVE_GPU_UNEXPECTED_INTERPOLATION";
        summary.put("gpu_readbacks",successfulReadbacks);
        summary.put("control_smooth_matches_cpu",smoothGood);
        summary.put("control_affine_emulated_matches_cpu",affineGood);
        summary.put("control_flat_stable",flatGood);
        summary.put("native_extension_shader_compiled_and_linked",bestNative!=null);
        summary.put("native_glsl_version_trials",nativeTrials);
        summary.put("native_best_glsl_es_version",bestNativeVersion);
        summary.put("native_gpu_matches_cpu_affine",nativeGood);
        summary.put("native_gpu_matches_cpu_smooth_only",nativeCollapsed);
        summary.put("diagnostic_status",verdict);
        summary.put("finished_ms",System.currentTimeMillis());
        JSONArray outputs=new JSONArray();
        for(Samples row:result)if(row!=null)outputs.put(row.json);
        summary.put("results",outputs);
        record(j("event","final","status",verdict));
        display("GFX102: "+verdict+"\nGLES extension advertised: "+nativeExtension+
            "\nControls correct: "+(smoothGood&&affineGood&&flatGood)+
            "\nGPU readbacks: "+successfulReadbacks+
            "\nAuto-exporting ZIP. Shader48 restoration remains OPEN.");
    }

    private void startExport() {
        new Thread(new Runnable(){public void run(){exportZip();}}).start();
    }
    private static void putText(ZipOutputStream zip,String name,String data)throws Exception {
        zip.putNextEntry(new ZipEntry(name));
        zip.write(data.getBytes(StandardCharsets.UTF_8));
        zip.closeEntry();
    }
    private synchronized void exportZip() {
        Uri uri=null;
        File backup=new File(getFilesDir(),"GFX102-last-test.zip");
        try {
            try(ZipOutputStream z=new ZipOutputStream(new FileOutputStream(backup))){
                putText(z,"summary.json",summary.toString(2));
                StringBuilder logs=new StringBuilder();
                synchronized(this){
                    for(int i=0;i<events.length();i++)
                        logs.append(events.getJSONObject(i).toString()).append('\n');
                }
                putText(z,"events.jsonl",logs.toString());
                putText(z,"LIMITS.txt","GFX102 is a synthetic-only GLES3 driver and extension check. "+
                    "No original Raft shader, material, texture, animation, PC parity or full-game pixel evidence. "+
                    "originalShaderRestored=false; phase_closed=false.\n");
                synchronized(images){
                    for(Map.Entry<String,byte[]> entry:images.entrySet()){
                        z.putNextEntry(new ZipEntry("captures/"+entry.getKey()));
                        z.write(entry.getValue());z.closeEntry();
                    }
                }
            }
            String name="GFX102-ALL-TEST-LOGS-"+System.currentTimeMillis()+".zip";
            ContentValues v=new ContentValues();
            v.put(MediaStore.Downloads.DISPLAY_NAME,name);
            v.put(MediaStore.Downloads.MIME_TYPE,"application/zip");
            v.put(MediaStore.Downloads.RELATIVE_PATH,"Download/Games/cl/test/g/");
            v.put(MediaStore.Downloads.IS_PENDING,1);
            uri=getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI,v);
            if(uri==null)throw new IllegalStateException("MediaStore insert null");
            try(InputStream in=new FileInputStream(backup);
                OutputStream out=getContentResolver().openOutputStream(uri)){
                if(out==null)throw new IllegalStateException("MediaStore stream null");
                byte[] bytes=new byte[32768];int n;
                while((n=in.read(bytes))!=-1)out.write(bytes,0,n);
            }
            ContentValues done=new ContentValues();
            done.put(MediaStore.Downloads.IS_PENDING,0);
            if(getContentResolver().update(uri,done,null,null)!=1)
                throw new IllegalStateException("MediaStore publish failed");
            try(Cursor c=getContentResolver().query(uri,
                new String[]{MediaStore.Downloads.SIZE,MediaStore.Downloads.RELATIVE_PATH},
                null,null,null)){
                if(c==null||!c.moveToFirst()||c.getLong(0)!=backup.length()||
                   !"Download/Games/cl/test/g/".equals(c.getString(1)))
                    throw new IllegalStateException("MediaStore size/path mismatch");
            }
            display("GFX102 logs saved: Download/Games/cl/test/g/"+name+
                "\nSend this ZIP back. Original Shader48 still OPEN.");
        } catch(Exception ex) {
            if(uri!=null)getContentResolver().delete(uri,null,null);
            exportError=ex.getClass().getSimpleName()+": "+ex.getMessage();
            display("GFX102 export failed: "+exportError+
                "\nPrivate ZIP retained; press EXPORT to retry.");
        }
    }
    @Override protected void onPause(){super.onPause();if(view!=null)view.onPause();}
    @Override protected void onResume(){super.onResume();if(view!=null)view.onResume();}
}
