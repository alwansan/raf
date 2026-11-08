package com.alwansan.raftlab;

import android.opengl.GLES20;
import android.opengl.GLES30;
import android.opengl.GLES31;
import android.opengl.GLSurfaceView;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.LinearLayout;
import org.json.JSONObject;

import java.nio.Buffer;
import java.nio.ByteBuffer;
import java.nio.ByteOrder;
import java.util.Locale;
import javax.microedition.khronos.egl.EGLConfig;
import javax.microedition.khronos.opengles.GL10;

/**
 * T1 bounded GLES 3.1 compute diagnostic. Only built-in synthetic shaders execute;
 * imported testpacks cannot supply GLSL, SPIR-V, native code, or parameters.
 * This checks Android GPU compute plumbing, NOT Unity FindKernel or Raft water.
 */
final class T1ComputeProbe {
    private static final int N = 16;
    private static final int BYTES = N * 4;
    private final MainActivity activity;
    private final GLSurfaceView view;
    private volatile boolean ready;
    private String contextVersion = "not-created";

    private static final String INIT =
        "#version 310 es\n" +
        "layout(local_size_x=4,local_size_y=1,local_size_z=1) in;\n" +
        "layout(std430,binding=0) buffer OutData { uint v[]; };\n" +
        "void main(){ uint i=gl_GlobalInvocationID.x; if(i<16u) v[i]=i*3u+7u; }\n";
    private static final String FIRST =
        "#version 310 es\n" +
        "layout(local_size_x=4,local_size_y=1,local_size_z=1) in;\n" +
        "layout(std430,binding=0) buffer OutData { uint v[]; };\n" +
        "void main(){ uint i=gl_GlobalInvocationID.x; if(i<16u) v[i]=i+10u; }\n";
    private static final String SECOND =
        "#version 310 es\n" +
        "layout(local_size_x=4,local_size_y=1,local_size_z=1) in;\n" +
        "layout(std430,binding=0) buffer OutData { uint v[]; };\n" +
        "void main(){ uint i=gl_GlobalInvocationID.x; if(i<16u) v[i]=v[i]*2u+1u; }\n";
    private static final String INVALID =
        "#version 310 es\n" +
        "layout(local_size_x=4) in;\n" +
        "void main(){ this_function_must_not_exist(); }\n";

    private T1ComputeProbe(MainActivity a, LinearLayout root) {
        activity=a;
        view=new GLSurfaceView(a);
        view.setEGLContextClientVersion(3);
        view.setRenderer(new GLSurfaceView.Renderer() {
            @Override public void onSurfaceCreated(GL10 gl, EGLConfig config) {
                contextVersion=String.valueOf(GLES20.glGetString(GLES20.GL_VERSION));
                ready=true;
                String driver="version="+contextVersion+
                    " vendor="+GLES20.glGetString(GLES20.GL_VENDOR)+
                    " renderer="+GLES20.glGetString(GLES20.GL_RENDERER)+
                    " glsl="+GLES20.glGetString(GLES20.GL_SHADING_LANGUAGE_VERSION);
                activity.runOnUiThread(()->activity.log("t1_gpu_context",driver));
            }
            @Override public void onSurfaceChanged(GL10 gl,int w,int h){}
            @Override public void onDrawFrame(GL10 gl){}
        });
        view.setRenderMode(GLSurfaceView.RENDERMODE_WHEN_DIRTY);
        root.addView(view,new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT,48));
        Button run=new Button(a);
        run.setText("Run selected T1 GPU CASE (compiled-in shaders only)");
        root.addView(run);
        run.setOnClickListener(v->{
            final JSONObject selected=activity.selected;
            if(selected==null||!selected.optString("id").matches("T1-0[1-4]")){
                activity.log("t1_gpu_reject","Select built-in T1-01..04");
                activity.caption.setText("Select one of T1-01..04 before running GPU test.");
                return;
            }
            if(!"builtin-t1-gles31".equals(activity.packId)){
                activity.log("t1_gpu_reject","Imported pack cannot execute GPU code; reset the app to builtin cases.");
                activity.caption.setText("GPU execution restricted to built-in T1 cases.");
                return;
            }
            final String id=selected.optString("id");
            activity.log("t1_gpu_begin",id);
            view.queueEvent(()->{
                String observed;
                try {
                    observed=execute(id);
                } catch(Throwable t) {
                    observed="FAIL exception="+t.getClass().getSimpleName()+": "+String.valueOf(t.getMessage());
                }
                final String observation=observed;
                activity.runOnUiThread(()->{
                    activity.log("t1_gpu_observed",id+" "+observation);
                    activity.caption.setText("GPU "+id+" — "+observation+
                        "\nRecord PASS/FAIL/UNEXPECTED and any notes below; export logs.");
                });
            });
            view.requestRender();
        });
    }
    static T1ComputeProbe install(MainActivity a, LinearLayout root) {
        a.packId="builtin-t1-gles31";
        String[] names={
            "GLES context and compute limits",
            "16-word one-pass SSBO dispatch/readback",
            "two dispatches with shader storage barrier/readback",
            "negative control: invalid GLSL must not compile"
        };
        String[] expected={
            "GLES >=3.1 with compute workgroup limit >=4 and local size >=4",
            "Exact 16 integers v[i] = i*3+7, no GL error",
            "Exact 16 integers v[i] = 2*(i+10)+1, no GL error",
            "Compiler rejects non-existent GLSL function"
        };
        for(int i=0;i<names.length;i++)try {
            a.cases.add(new JSONObject()
                .put("id",String.format(Locale.US,"T1-%02d",i+1))
                .put("type","note").put("title",names[i])
                .put("instructions","Select case; tap Run selected T1 GPU CASE. Inspect GPU observation; then mark actual result.")
                .put("expected",expected[i]));
        }catch(Exception ignored){}
        return new T1ComputeProbe(a,root);
    }
    // Reuse the same compiled original diagnostic controls for the SHARED APK.
    // Only return actual observed PASS/FAIL, never inferred from source-only CI.
    void runAutomated(String caseId, java.util.function.Consumer<String> callback) {
        if(!caseId.matches("T1-0[1-4]")) {callback.accept("FAIL unknown test");return;}
        view.queueEvent(()->{
            String value;
            try { value=execute(caseId); }
            catch(Throwable ex){ value="FAIL exception="+ex.getClass().getSimpleName()+": "+ex.getMessage(); }
            final String observed=value;
            activity.runOnUiThread(()->{
                activity.log("t1_gpu_auto_observed",caseId+" "+observed);
                callback.accept(observed);
            });
        });
        view.requestRender();
    }

    void onPause(){ready=false;view.onPause();}
    void onResume(){view.onResume();}
    private static int integer(int property) {
        int[] v=new int[1];
        GLES20.glGetIntegerv(property,v,0);
        return v[0];
    }
    private static int indexed(int property,int index) {
        int[] v=new int[1];
        GLES31.glGetIntegeri_v(property,index,v,0);
        return v[0];
    }
    private boolean hasCompute() {
        return contextVersion.contains("OpenGL ES 3.1") ||
            contextVersion.contains("OpenGL ES 3.2") ||
            contextVersion.contains("OpenGL ES 3.3");
    }
    private String execute(String id) {
        if(!ready)return "FAIL no active GLES context";
        if(!hasCompute())return "FAIL GLES3.1+ unavailable, context="+contextVersion;
        // A failed earlier draw must never be silently attributed to this dispatch.
        int stale;int drained=0;
        while((stale=GLES20.glGetError())!=GLES20.GL_NO_ERROR && drained++<32){}
        if(id.equals("T1-01")){
            int maxX=indexed(GLES31.GL_MAX_COMPUTE_WORK_GROUP_COUNT,0);
            int sizeX=indexed(GLES31.GL_MAX_COMPUTE_WORK_GROUP_SIZE,0);
            int invocations=integer(GLES31.GL_MAX_COMPUTE_WORK_GROUP_INVOCATIONS);
            int sharedMem=integer(GLES31.GL_MAX_COMPUTE_SHARED_MEMORY_SIZE);
            int err=GLES20.glGetError();
            boolean good=err==GLES20.GL_NO_ERROR&&maxX>=4&&sizeX>=4&&invocations>=4;
            return (good?"PASS":"FAIL")+" version="+contextVersion+
                " max_count_x="+maxX+" max_size_x="+sizeX+
                " max_invocations="+invocations+" shared_memory="+sharedMem+
                " preexisting_errors="+drained+" gl_error=0x"+Integer.toHexString(err);
        }
        if(id.equals("T1-04")){
            int shader=GLES20.glCreateShader(GLES31.GL_COMPUTE_SHADER);
            if(shader==0)return "FAIL cannot allocate compute shader";
            try {
                GLES20.glShaderSource(shader,INVALID);
                GLES20.glCompileShader(shader);
                int[] compiled=new int[1];
                GLES20.glGetShaderiv(shader,GLES20.GL_COMPILE_STATUS,compiled,0);
                int err=GLES20.glGetError();
                String compiler=GLES20.glGetShaderInfoLog(shader);
                return (compiled[0]==0&&err==GLES20.GL_NO_ERROR?"PASS":"FAIL")+
                    " invalid_shader_compiled="+compiled[0]+" gl_error=0x"+
                    Integer.toHexString(err)+" diagnostic_chars="+
                    (compiler==null?0:compiler.length());
            } finally { GLES20.glDeleteShader(shader); }
        }
        return dispatch(id.equals("T1-03"));
    }
    private static int compileProgram(String source) {
        int shader=GLES20.glCreateShader(GLES31.GL_COMPUTE_SHADER);
        if(shader==0)throw new IllegalStateException("glCreateShader=0");
        try {
            GLES20.glShaderSource(shader,source);
            GLES20.glCompileShader(shader);
            int[] compile=new int[1];
            GLES20.glGetShaderiv(shader,GLES20.GL_COMPILE_STATUS,compile,0);
            if(compile[0]!=GLES20.GL_TRUE)
                throw new IllegalStateException("shader compile failed: "+bounded(GLES20.glGetShaderInfoLog(shader)));
            int program=GLES20.glCreateProgram();
            if(program==0)throw new IllegalStateException("glCreateProgram=0");
            GLES20.glAttachShader(program,shader);
            GLES20.glLinkProgram(program);
            int[] link=new int[1];
            GLES20.glGetProgramiv(program,GLES20.GL_LINK_STATUS,link,0);
            if(link[0]!=GLES20.GL_TRUE){
                String info=bounded(GLES20.glGetProgramInfoLog(program));
                GLES20.glDeleteProgram(program);
                throw new IllegalStateException("program link failed: "+info);
            }
            return program;
        }finally{GLES20.glDeleteShader(shader);}
    }
    private static String bounded(String s){return s==null?"":s.substring(0,Math.min(s.length(),300)).replace('\n',' ');}
    private String dispatch(boolean twoPass) {
        int[] buffers=new int[1];
        int first=0,second=0;
        try {
            first=compileProgram(twoPass?FIRST:INIT);
            if(twoPass)second=compileProgram(SECOND);
            GLES30.glGenBuffers(1,buffers,0);
            if(buffers[0]==0)throw new IllegalStateException("SSBO allocation=0");
            GLES30.glBindBuffer(GLES31.GL_SHADER_STORAGE_BUFFER,buffers[0]);
            ByteBuffer zero=ByteBuffer.allocateDirect(BYTES).order(ByteOrder.nativeOrder());
            GLES30.glBufferData(GLES31.GL_SHADER_STORAGE_BUFFER,BYTES,zero,GLES30.GL_DYNAMIC_DRAW);
            GLES31.glBindBufferBase(GLES31.GL_SHADER_STORAGE_BUFFER,0,buffers[0]);
            GLES20.glUseProgram(first);
            GLES31.glDispatchCompute(4,1,1);
            if(twoPass){
                GLES31.glMemoryBarrier(GLES31.GL_SHADER_STORAGE_BARRIER_BIT);
                GLES20.glUseProgram(second);
                GLES31.glDispatchCompute(4,1,1);
            }
            GLES31.glMemoryBarrier(GLES31.GL_BUFFER_UPDATE_BARRIER_BIT);
            int dispatchError=GLES20.glGetError();
            if(dispatchError!=GLES20.GL_NO_ERROR)
                return "FAIL dispatch gl_error=0x"+Integer.toHexString(dispatchError);
            GLES30.glBindBuffer(GLES31.GL_SHADER_STORAGE_BUFFER,buffers[0]);
            Buffer raw=GLES30.glMapBufferRange(GLES31.GL_SHADER_STORAGE_BUFFER,0,BYTES,GLES30.GL_MAP_READ_BIT);
            if(!(raw instanceof ByteBuffer))return "FAIL SSBO readback null/non-bytebuffer";
            ByteBuffer bytes=((ByteBuffer)raw).order(ByteOrder.nativeOrder());
            int mismatch=-1,found=0,want=0;
            for(int i=0;i<N;i++){
                int got=bytes.getInt(i*4);
                int expected=twoPass?(2*(i+10)+1):(i*3+7);
                if(got!=expected&&mismatch<0){mismatch=i;found=got;want=expected;}
            }
            boolean unmapped=GLES30.glUnmapBuffer(GLES31.GL_SHADER_STORAGE_BUFFER);
            int endError=GLES20.glGetError();
            boolean passed=mismatch<0&&unmapped&&endError==GLES20.GL_NO_ERROR;
            return (passed?"PASS":"FAIL")+" matched="+(mismatch<0?16:"mismatch_at_"+mismatch)+
                (mismatch<0?"":" actual="+found+" expected="+want)+
                " unmap="+unmapped+" gl_error=0x"+Integer.toHexString(endError)+
                " checked_words="+N;
        }finally{
            GLES20.glUseProgram(0);
            GLES31.glBindBufferBase(GLES31.GL_SHADER_STORAGE_BUFFER,0,0);
            GLES30.glBindBuffer(GLES31.GL_SHADER_STORAGE_BUFFER,0);
            if(buffers[0]!=0)GLES30.glDeleteBuffers(1,buffers,0);
            if(first!=0)GLES20.glDeleteProgram(first);
            if(second!=0)GLES20.glDeleteProgram(second);
        }
    }
    // Do not report GPU elapsed time from Java wall-clock timings.
}
